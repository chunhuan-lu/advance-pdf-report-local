"""在生成的 PDF 里嵌入源 JSON，实现"上传旧 PDF → 无损回填表单"。"""
import json
from io import BytesIO

from pypdf import PdfReader, PdfWriter

ATTACHMENT_NAME = "report_data.json"


def embed_json(pdf_bytes: bytes, data: dict) -> bytes:
    reader = PdfReader(BytesIO(pdf_bytes))
    writer = PdfWriter(clone_from=reader)
    writer.add_attachment(ATTACHMENT_NAME, json.dumps(data, ensure_ascii=False).encode("utf-8"))
    out = BytesIO()
    writer.write(out)
    return out.getvalue()


def extract_json(file_obj):
    """尝试取出嵌入的报告 JSON；没有则返回 None。"""
    try:
        reader = PdfReader(file_obj)
        if reader.is_encrypted:
            reader.decrypt("")
        attachments = reader.attachments
        for name in attachments:
            if name == ATTACHMENT_NAME:
                contents = attachments[name]
                if contents:
                    return json.loads(bytes(contents[0]).decode("utf-8"))
    except Exception as e:
        print(f"[extract_json] {e}")
    return None
