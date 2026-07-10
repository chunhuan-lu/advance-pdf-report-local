import jmespath
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, Paragraph

from pdfgen.common import fontstyle
from pdfgen.common.checkbox import Checkbox
from pdfgen.common.layout import get_header
from pdfgen.common.utils import get_time_str

styles = getSampleStyleSheet()


def get_checkbox(compliant: bool, green_text="Compliant", red_text="Non-Compliant"):
    checkbox_row = Table([[
        Checkbox(green_text, compliant, font_size=10, color=colors.green, bold=True),
        Checkbox(red_text, not compliant, font_size=10, color=colors.red, bold=True)]],
        colWidths=[85, 95])
    return checkbox_row


def get_safety_certificate_page(import_data: dict):
    gas_certi_page_res = list()
    gas_certi_page_res += get_header()
    gas_certi_page_res.append(Paragraph(
        f'<para align="center"><font size="15" color="{fontstyle.COLOR_DARK_BLUE}">'
        f'<b>GAS SAFETY CERTIFICATE</b></font></para>', styles['Heading2']))

    base_data = jmespath.search("baseInfo", import_data) or {}
    client = base_data.get('clientBranch') or {}
    inspector = base_data.get('inspector') or {}

    # 左栏数据
    left_data = [
        [Paragraph('<b>Property Address</b>', fontstyle.white_on_blue_style)],
        [Paragraph(f'{base_data.get("propertyAddress", "")}', styles['Normal'])],
        [Paragraph('<b>Client Details</b>', fontstyle.white_on_blue_style)],
        [Paragraph(f'{client.get("agentName", "")}<br/><br/>{client.get("branchAddress", "")}',
                   styles['Normal'])],
    ]
    # 右栏数据
    right_data = [
        [Paragraph('<para align="right"><b>Reference ID</b></para>', fontstyle.white_on_blue_style),
         base_data.get('referenceId', '')],
        [Paragraph('<para align="right"><b>Inspector</b></para>', fontstyle.white_on_blue_style),
         inspector.get('name', '')],
        [Paragraph('<para align="right"><b>Licence No.</b></para>', fontstyle.white_on_blue_style),
         inspector.get('licenceNo', '')],
        [],
        [Paragraph('<para align="right"><b>Inspection Date</b></para>', fontstyle.white_on_blue_style),
         get_time_str(base_data.get('inspectedDate', ''))],
        [Paragraph('<para align="right"><b>NEXT Gas Safety Check Due</b></para>', fontstyle.white_on_blue_style),
         get_time_str(base_data.get('nextCheckDue', ''))],
    ]

    left_table = Table(left_data, colWidths=350, rowHeights=[25, 50, 25, 50])
    left_table.setStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(fontstyle.COLOR_DARK_BLUE)),
        ('BACKGROUND', (0, 2), (0, 2), colors.HexColor(fontstyle.COLOR_DARK_BLUE)),
        ('VALIGN', (0, 1), (-1, -1), 0.5, "TOP"),
    ])

    right_table = Table(right_data, colWidths=[180, 220], rowHeights=[25, 25, 25, 25, 25, 25])
    right_table.setStyle([
        ('GRID', (0, 0), (1, 2), 0.5, colors.grey),
        ('GRID', (0, 4), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, 2), colors.HexColor(fontstyle.COLOR_DARK_BLUE)),
        ('BACKGROUND', (0, 4), (0, -1), colors.HexColor(fontstyle.COLOR_DARK_BLUE)),
        ('SPAN', (0, 3), (1, 3)),
    ])

    # =================== OVERALL FINDINGS ===================
    overall_list = jmespath.search("gasCheckDetails.overallFindings[*]", import_data) or []

    overall_datas = [
        ["OVERALL FINDINGS", "", ""]
    ]
    for item in overall_list:
        options = item.get('options') or ["", ""]
        ticked = (item.get('tickedPos') or '').lower() == (options[0] or '').lower()
        overall_datas.append([
            item.get('label', ''),
            get_checkbox(ticked, *options[:2]),
            Paragraph(str(item.get('remark', '') or ''), styles['Normal'])
        ])

    # 行高跟随数据行数，不再写死 5 行
    overall_table = Table(overall_datas, colWidths=[150, 200, 450],
                          rowHeights=[30] + [50] * (len(overall_datas) - 1))
    overall_table.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(fontstyle.COLOR_DARK_BLUE)),
        ('BACKGROUND', (0, 1), (0, -1), colors.grey),
        ('BACKGROUND', (1, 1), (1, -1), colors.lightgrey),
        ('SPAN', (0, 0), (-1, 0)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 0), (-1, 0), "Helvetica-Bold"),
        ('FONTNAME', (0, 1), (0, -1), "Helvetica-Bold"),
        ('VALIGN', (0, 0), (-1, -1), "MIDDLE"),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (0, 1), (0, -1), "RIGHT"),
    ])

    main_info_table = Table([
        [left_table, right_table],
        [],
        [],
        [overall_table, ]], colWidths=[400, 400])
    main_info_table.setStyle([
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
    ])
    gas_certi_page_res.append(main_info_table)
    return gas_certi_page_res
