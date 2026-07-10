import jmespath
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image

from pdfgen.common import fontstyle
from pdfgen.common.checkbox import Checkbox
from pdfgen.common.layout import LOGO_PATH, COMPANY_ADDRESS, COMPANY_EMAIL, COMPANY_PHONE
from pdfgen.common.utils import get_time_str

styles = getSampleStyleSheet()


def get_cover(import_data: dict):
    """封面页（A4）：Gas / Electrical / Smoke Alarm 三类报告共用。"""
    result = list()
    data = jmespath.search("baseInfo", import_data) or {}
    report_type = (data.get('type') or '').lower()
    rental_type = (data.get('rentalType') or '').lower()
    client = data.get('clientBranch') or {}

    # ----logo----
    img = Image(LOGO_PATH, width=379, height=89.6)
    result.append(img)
    result.append(Spacer(1, 12))

    # --- 报告标题 ---
    result.append(Paragraph("SAFETY &", fontstyle.title_style))
    result.append(Paragraph("COMPLIANCE", fontstyle.title_style))
    result.append(Paragraph("REPORT", fontstyle.title_style))

    # --- 类型勾选框 -----
    checkbox_row = [
        Checkbox("Gas", report_type == "gas"),
        Checkbox("Electrical", report_type == "electrical"),
        Checkbox("Smoke Alarm", report_type in ("smoke", "smoke alarm"))
    ]
    checkbox_table = Table([checkbox_row], hAlign='CENTER', colWidths=[100] * 3)
    checkbox_table.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    result.append(checkbox_table)
    result.append(Spacer(1, 20))

    # ---------------------------- client 信息 ----------------------------
    client_table_width = 210
    client_table_height = 350
    result.append(Spacer(1, 6))
    client_info = Paragraph(
        f"{client.get('agentName', '')}<br/><br/>{client.get('branchAddress', '')}",
        styles["Normal"])
    table_1 = Table([
        [Paragraph("<b>Client’s Detail:</b>", styles["Normal"]), client_info]
    ], colWidths=[client_table_width, client_table_height], hAlign='CENTER')
    table_1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 0.3, colors.grey),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    result.append(table_1)

    table_2 = Table([[Paragraph("", styles["Normal"])]],
                    colWidths=[client_table_width + client_table_height], style=[
            ('BACKGROUND', (0, 0), (-1, -1), fontstyle.COLOR_DARK_BLUE),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12)
        ])
    result.append(table_2)

    check_box_cell_content = [
        Checkbox("Rental Property", rental_type == 'rental property',
                 color=colors.black, font_size=10, bold=True),
        Spacer(1, 2),
        Checkbox("Rooming House", rental_type == 'rooming house',
                 color=colors.black, font_size=10, bold=True)
    ]

    table_report_base_data = [
        [Paragraph("<b>Reference ID:</b>", styles["Normal"]),
         Paragraph(f"{data.get('referenceId', '')}", styles["Normal"])],
        [Paragraph("<b>Property Type:</b>", styles["Normal"]),
         check_box_cell_content],
        [Paragraph("<b>Property Address:</b>", styles["Normal"]),
         Paragraph(f"{data.get('propertyAddress', '')}", styles["Normal"])],
        [Paragraph("<b>Inspected Date:</b>", styles["Normal"]),
         Paragraph(f"<b>{get_time_str(data.get('inspectedDate', ''))}</b>", styles["Normal"])],
    ]

    table_3 = Table(table_report_base_data, colWidths=[client_table_width, client_table_height], hAlign='CENTER')
    table_3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 0.3, colors.grey),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    result.append(table_3)

    tail = [COMPANY_ADDRESS, COMPANY_EMAIL, COMPANY_PHONE]
    tail_str = "<br/>".join(tail)
    tail_str = Paragraph(
        f'<para align="center" fontSize="7" color="{colors.grey}">{tail_str}</para>',
        styles['Normal']
    )
    result.append(tail_str)
    return result
