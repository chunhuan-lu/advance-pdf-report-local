"""Smoke Alarm 报告：封面（共用）+ DOMESTIC SMOKE ALARM COMPLIANCE CERTIFICATE。

烟感器数量不限：每 3 个一组排版，超出自动换行/分页。
"""
from io import BytesIO

import jmespath
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle, Flowable
)

from pdfgen.common import cover, fontstyle
from pdfgen.common.checkbox import Checkbox
from pdfgen.common.layout import get_header
from pdfgen.common.utils import get_time_str, smart_image_import

styles = getSampleStyleSheet()

CONTENT_WIDTH = 515  # A4 竖版可用宽度
DARK_BLUE = colors.HexColor(fontstyle.COLOR_DARK_BLUE)


class BigCheck(Flowable):
    """声明区的大勾选框。"""

    def __init__(self, checked=True, size=30):
        super().__init__()
        self.checked = checked
        self.size = size
        self.width = size
        self.height = size

    def draw(self):
        s = self.size
        self.canv.setStrokeColor(colors.black)
        self.canv.setLineWidth(1.5)
        self.canv.rect(0, 0, s, s)
        if self.checked:
            self.canv.setLineWidth(3)
            self.canv.setLineCap(1)
            p = self.canv.beginPath()
            p.moveTo(s * 0.18, s * 0.5)
            p.lineTo(s * 0.42, s * 0.22)
            p.lineTo(s * 0.85, s * 0.82)
            self.canv.drawPath(p, stroke=1, fill=0)


def _label(text):
    return Paragraph(f'<b>{text}</b>', styles['Normal'])


def _info_tables(base):
    client = base.get('clientBranch') or {}
    inspector = base.get('inspector') or {}
    company = base.get('company') or {}

    label_bg = colors.HexColor('#EFEFEF')
    info_rows = [
        [_label('Reference ID:'), Paragraph(base.get('referenceId', ''), styles['Normal']),
         _label('Inspection Date:'), Paragraph(get_time_str(base.get('inspectedDate', '')), styles['Normal'])],
        [_label('Property Address:'), Paragraph(base.get('propertyAddress', ''), styles['Normal']),
         _label('NEXT Smoke Alarm Check Due:'), Paragraph(get_time_str(base.get('nextCheckDue', '')), styles['Normal'])],
        [_label('Building Class:'), Paragraph(base.get('buildingClass', '') or '', styles['Normal']),
         _label('Client:'), Paragraph(client.get('agentName', ''), styles['Normal'])],
    ]
    info_table = Table(info_rows, colWidths=[105, 165, 130, 115])
    info_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), label_bg),
        ('BACKGROUND', (2, 0), (2, -1), label_bg),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    elec_header = Table([[Paragraph('<b><font color="white">ELECTRICIAN INFORMATION</font></b>',
                                    styles['Normal'])]], colWidths=[CONTENT_WIDTH])
    elec_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))

    elec_rows = [
        [_label('Inspector:'), Paragraph(inspector.get('name', ''), styles['Normal']),
         _label('Company:'), Paragraph(company.get('name', ''), styles['Normal'])],
        [_label('Licence No.:'), Paragraph(inspector.get('licenceNo', ''), styles['Normal']),
         '', Paragraph(company.get('address', ''), styles['Normal'])],
    ]
    elec_table = Table(elec_rows, colWidths=[105, 165, 130, 115])
    elec_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), label_bg),
        ('BACKGROUND', (2, 0), (2, -1), label_bg),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return [info_table, Spacer(1, 10), elec_header, elec_table]


def _statement_row(checked: bool, statement_red: str):
    text = Paragraph(
        f'<b>On the Inspection Date and at the Inspection Address, the smoke alarms<br/>'
        f'<font color="red">{statement_red}</font></b>', styles['Normal'])
    t = Table([[BigCheck(checked), text]], colWidths=[55, CONTENT_WIDTH - 55])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F2F4F7')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
    ]))
    return t


def _alarm_group_table(alarms: list, start_index: int):
    """一组最多 3 个烟感器的表格。"""
    label_w = 55
    col_w = (CONTENT_WIDTH - label_w) / 3.0
    n = len(alarms)

    def pad(row):
        return row + [''] * (3 - n)

    header_row = [''] + pad([Paragraph(f'<para align="center"><b>Smoke {start_index + i + 1}</b></para>',
                                       styles['Normal']) for i in range(n)])
    check_row = [''] + pad([
        Table([[
            Checkbox("Compliant", (a.get('status') or '').lower() == 'compliant',
                     font_size=7, color=colors.black, bold=True),
            Checkbox("Non-Compliant", (a.get('status') or '').lower() != 'compliant',
                     font_size=7, color=colors.black, bold=True),
        ]], colWidths=[col_w * 0.44, col_w * 0.56])
        for a in alarms])
    brand_row = [_label('Brand')] + pad([Paragraph(str(a.get('brand', '') or ''), styles['Normal'])
                                         for a in alarms])
    location_row = [_label('Location')] + pad([Paragraph(str(a.get('location', '') or ''), styles['Normal'])
                                               for a in alarms])
    expiry_row = [_label('Expiry')] + pad([Paragraph(str(a.get('expiry', '') or ''), styles['Normal'])
                                           for a in alarms])
    photo_row = [''] + pad([smart_image_import(a.get('photoUrl'), max_width=col_w - 14, max_height=160) or ''
                            for a in alarms])

    table = Table(
        [header_row, check_row, brand_row, location_row, expiry_row, photo_row],
        colWidths=[label_w] + [col_w] * 3,
        rowHeights=[20, 18, 20, 20, 20, 185])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#EFEFEF')),
        ('BACKGROUND', (0, 2), (0, -1), colors.HexColor('#EFEFEF')),
        ('VALIGN', (0, 0), (-1, 4), 'MIDDLE'),
        ('VALIGN', (0, 5), (-1, 5), 'MIDDLE'),
        ('ALIGN', (1, 5), (-1, 5), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    return table


def get_smoke_certificate_page(import_data: dict):
    result = list()
    result += get_header(total_width=CONTENT_WIDTH)

    base = jmespath.search("baseInfo", import_data) or {}
    details = jmespath.search("smokeCheckDetails", import_data) or {}

    title = Table([[Paragraph(
        f'<para align="center"><font size="16" color="{fontstyle.COLOR_DARK_BLUE}">'
        f'<b>DOMESTIC SMOKE ALARM<br/>COMPLIANCE CERTIFICATE</b></font></para>', styles['Normal'])]],
        colWidths=[CONTENT_WIDTH])
    title.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    result.append(title)
    result.append(Spacer(1, 10))

    result += _info_tables(base)
    result.append(Spacer(1, 10))

    result.append(_statement_row(bool(details.get('metCurrentRequirements')),
                                 'Met the Current Requirements.'))
    result.append(Spacer(1, 10))
    result.append(_statement_row(bool(details.get('metNewRequirements')),
                                 'Met the New Requirements.'))
    result.append(Spacer(1, 10))

    # SMOKE ALARMS 标题 + 整体合规
    overall = (details.get('overallCompliant') or '').lower() == 'compliant'
    heading = Table([[
        Paragraph(f'<font size="13" color="{fontstyle.COLOR_DARK_BLUE}"><b>SMOKE ALARMS</b></font><br/>'
                  f'<font size="9">At this inspection, the following alarms were present or installed.</font>',
                  styles['Normal']),
        [Checkbox("Compliant", overall, font_size=10, color=colors.green, bold=True),
         Spacer(1, 4),
         Checkbox("Non- Compliant", not overall, font_size=10, color=colors.red, bold=True)],
    ]], colWidths=[CONTENT_WIDTH - 160, 160])
    heading.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    result.append(heading)
    result.append(Spacer(1, 8))

    alarms = details.get('alarms') or []
    for i in range(0, len(alarms), 3):
        # 每组整体排版，放不下就整组挪到下一页，避免表格拦腰拆开
        result.append(KeepTogether([_alarm_group_table(alarms[i:i + 3], i), Spacer(1, 12)]))
    return result


def build(import_data: dict) -> bytes:
    """生成 Smoke Alarm 报告 PDF，返回字节流。"""
    buffer = BytesIO()
    frame_A4 = Frame(40, 40, A4[0] - 80, A4[1] - 80, id='frameA4')
    template_A4 = PageTemplate(id='A4', pagesize=A4, frames=[frame_A4])
    doc = BaseDocTemplate(buffer, pageTemplates=[template_A4])

    story = list()
    story += cover.get_cover(import_data)
    story.append(PageBreak())
    story += get_smoke_certificate_page(import_data)
    doc.build(story)
    return buffer.getvalue()
