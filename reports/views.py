import re
import traceback
import uuid

import jmespath
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from pdfgen import storage
from pdfgen.embed import embed_json, extract_json
from pdfgen.generate import build_report_pdf
from pdfgen.parse import parse_template_pdf
from reports.models import Report


def _ok(data=None):
    return Response({"success": True, "msg": None, "data": data})


def _fail(msg):
    return Response({"success": False, "msg": str(msg), "data": None})


def _report_meta(data: dict):
    return {
        "report_type": (jmespath.search("baseInfo.type", data) or 'gas').lower(),
        "reference_id": jmespath.search("baseInfo.referenceId", data) or '',
        "property_address": jmespath.search("baseInfo.propertyAddress", data) or '',
    }


def _upsert_report(report_id: str, data: dict, pdf_url=None):
    defaults = {"data": data, **_report_meta(data)}
    if pdf_url is not None:
        defaults["pdf_url"] = pdf_url
    report, _ = Report.objects.update_or_create(id=report_id, defaults=defaults)
    return report


class ReportListCreate(APIView):
    def get(self, request):
        return _ok([r.summary() for r in Report.objects.all()[:200]])

    def post(self, request):
        try:
            body = request.data or {}
            data = body.get('data') or {}
            report_id = body.get('id') or uuid.uuid4().hex
            report = _upsert_report(report_id, data)
            return _ok(report.summary())
        except Exception as e:
            traceback.print_exc()
            return _fail(e)


class ReportDetail(APIView):
    def get(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id)
            return _ok({**report.summary(), "data": report.data})
        except Report.DoesNotExist:
            return _fail("report not found")

    def put(self, request, report_id):
        try:
            data = (request.data or {}).get('data') or {}
            report = _upsert_report(report_id, data)
            return _ok(report.summary())
        except Exception as e:
            traceback.print_exc()
            return _fail(e)

    def delete(self, request, report_id):
        Report.objects.filter(id=report_id).delete()
        return _ok()


class PhotoUpload(APIView):
    def post(self, request):
        image = request.FILES.get('file')
        if not image:
            return _fail("no file uploaded")
        key = request.data.get('key') or uuid.uuid4().hex
        try:
            url = storage.save_photo(image, key)
            return _ok(url)
        except Exception as e:
            traceback.print_exc()
            return _fail(e)


class GeneratePdf(APIView):
    def post(self, request):
        body = request.data or {}
        data = body.get('data') or body  # 兼容直接发整份报告 JSON
        mode = body.get('mode') or 'final'
        report_id = body.get('id') or uuid.uuid4().hex
        try:
            pdf_bytes = build_report_pdf(data)
            if mode == 'preview':
                _upsert_report(report_id, data)  # 预览时顺手保存草稿
                resp = HttpResponse(pdf_bytes, content_type='application/pdf')
                resp['Content-Disposition'] = 'inline; filename="preview.pdf"'
                resp['X-Report-Id'] = report_id
                return resp

            pdf_bytes = embed_json(pdf_bytes, data)
            meta = _report_meta(data)
            ref = re.sub(r'[^A-Za-z0-9-]+', '_', meta["reference_id"]) or report_id[:8]
            filename = f"{meta['report_type']}_{ref}_{report_id[:6]}.pdf"
            url = storage.save_pdf_bytes(pdf_bytes, filename)
            report = _upsert_report(report_id, data, pdf_url=url)
            return _ok({"url": url, "report": report.summary()})
        except Exception as e:
            traceback.print_exc()
            return _fail(e)


class ParsePdf(APIView):
    def post(self, request):
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return _fail("no file uploaded")
        try:
            data = extract_json(pdf_file)
            source = 'embedded'
            if data is None:
                pdf_file.seek(0)
                data = parse_template_pdf(pdf_file, photo_saver=storage.save_photo_bytes)
                source = 'acroform'
            if data is None:
                return _fail("这个 PDF 里既没有嵌入数据，也不是可识别的表单模板，无法解析")
            return _ok({"data": data, "source": source})
        except Exception as e:
            traceback.print_exc()
            return _fail(e)
