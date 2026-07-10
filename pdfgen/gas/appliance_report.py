import jmespath
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle, Paragraph

from pdfgen.common import fontstyle
from pdfgen.common.checkbox import Checkbox
from pdfgen.common.layout import get_header
from pdfgen.common.utils import smart_image_import

styles = getSampleStyleSheet()


class PhotoData:
    def __init__(self, title: str, remark: str, compliant: str, photo_list: list):
        self.title = title
        self.remark = remark
        self.compliant = compliant
        self.photo_list = photo_list or []


def get_compliant_checkbox_component(compliant: bool):
    checkbox_row = Table([[
        Checkbox("COMPLIANT", compliant, font_size=10, color=colors.green, bold=True),
        Checkbox("NON-COMPLIANT", not compliant, font_size=10, color=colors.red, bold=True)]],
        colWidths=[85, 95])
    return checkbox_row


def generate_photo_row(left_block: PhotoData, right_block):
    left_text = Paragraph(f"<b>{left_block.title}</b><br/>{left_block.remark}", styles['Normal'])
    left_compliant = (left_block.compliant or '').lower() == "compliant"
    left_photo = smart_image_import(left_block.photo_list[0]) if left_block.photo_list else None
    if right_block:
        right_text = Paragraph(f"<b>{right_block.title}</b><br/>{right_block.remark}", styles['Normal'])
        right_compliant = (right_block.compliant or '').lower() == "compliant"
        right_photo = smart_image_import(right_block.photo_list[0]) if right_block.photo_list else None
    else:
        right_text = ""
        right_compliant = None
        right_photo = ""

    table_data = [
        [left_text, left_photo, right_text, right_photo],
        [get_compliant_checkbox_component(left_compliant), '',
         get_compliant_checkbox_component(right_compliant) if right_compliant is not None else "", '']
    ]

    photo_row = Table(table_data, colWidths=[200, 200, 200, 200], rowHeights=[150, 30])
    photo_row.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -0), 'TOP'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('SPAN', (1, 0), (1, 1)),
        ('SPAN', (3, 0), (3, 1)),
    ]))
    return photo_row


def get_gas_app_report(import_data: dict):
    data = jmespath.search("gasCheckDetails.gasApplianceReport[*]", import_data) or []
    if not data:
        return []
    result = list()
    result += get_header()
    result.append(Paragraph(
        f'<para align="center"><font size="15" color="{fontstyle.COLOR_DARK_BLUE}"><b>GAS '
        f'APPLIANCE REPORT</b></font></para>', styles['Heading2']))
    data = list(data)
    if len(data) % 2 != 0:
        data.append(None)
    pairs = list(zip(data[::2], data[1::2]))
    for left, right in pairs:
        left_type = left.get("type") or {}
        left_data = PhotoData(
            left_type.get("value", ""),
            left.get("remark", ""),
            left_type.get("radio-value", ""),
            left.get("photoUrl"))
        if right is not None:
            right_type = right.get("type") or {}
            right_data = PhotoData(
                right_type.get("value", ""),
                right.get("remark", ""),
                right_type.get("radio-value", ""),
                right.get("photoUrl"))
        else:
            right_data = None
        result.append(generate_photo_row(left_data, right_data))
    return result
