import os

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle, Paragraph

from pdfgen.common.utils import get_image_component, ASSETS_DIR

styles = getSampleStyleSheet()

COMPANY_NAME = "Advance Essential Services Pty Ltd"
COMPANY_ABN = "ABN 57 160 581 706"
COMPANY_EMAIL = "info@advanceessentials.com.au"
COMPANY_PHONE = "0439 095 382"
COMPANY_ADDRESS = "BUILDING 16, 153-155 ROOKS ROAD, VERMONT, VIC 3133"

LOGO_PATH = os.path.join(str(ASSETS_DIR), "logo.png")


def get_header(total_width=830):
    """页眉：logo + 公司信息。每次调用返回新的 flowable，避免跨文档复用状态。"""
    logo = get_image_component(LOGO_PATH, max_height=30, max_width=120)
    info = Paragraph(
        f'<para align="right" fontSize="7">{COMPANY_NAME}<br/>{COMPANY_ABN}<br/>'
        f'<a href="mailto:{COMPANY_EMAIL}" color="blue">{COMPANY_EMAIL}</a><br/>{COMPANY_PHONE}</para>',
        styles['Normal']
    )
    left = total_width * 430 // 830
    header_info = Table([[logo, info]], colWidths=[left, total_width - left], rowHeights=30)
    header_info.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    return [header_info]
