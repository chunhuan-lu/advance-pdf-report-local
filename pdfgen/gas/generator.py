from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import PageBreak, BaseDocTemplate, PageTemplate, Frame, NextPageTemplate

from pdfgen.common import cover
from pdfgen.gas import certificate, service, appliance_report


def build(import_data: dict) -> bytes:
    """生成 Gas 报告 PDF，返回字节流。"""
    buffer = BytesIO()

    frame_A4 = Frame(40, 40, A4[0] - 80, A4[1] - 80, id='frameA4')
    template_A4 = PageTemplate(id='A4', pagesize=A4, frames=[frame_A4])
    # 证书/服务/照片页使用横向自定义尺寸
    custom_size = (842, 680)
    frame_custom = Frame(30, 30, custom_size[0] - 60, custom_size[1] - 50, id='frameCustom')
    template_custom = PageTemplate(id='Custom', pagesize=custom_size, frames=[frame_custom])

    doc = BaseDocTemplate(buffer, pageTemplates=[template_A4, template_custom])
    story = list()
    # ----------------------------- 封面 -----------------------------
    story += cover.get_cover(import_data)
    story.append(NextPageTemplate('Custom'))
    story.append(PageBreak())
    # =========================== GAS SAFETY CERTIFICATE ==============
    story += certificate.get_safety_certificate_page(import_data)
    story.append(PageBreak())
    # =========================== GAS SAFETY SERVICE ==================
    story += service.get_gas_safety_service(import_data)
    # ============================= PHOTO =============================
    photo_part = appliance_report.get_gas_app_report(import_data)
    if photo_part:
        story.append(PageBreak())
        story += photo_part

    doc.build(story)
    return buffer.getvalue()
