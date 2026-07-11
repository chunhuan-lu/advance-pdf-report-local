"""Electrical 报告：封面（共用）+ 证书页 + Safety Services + Fittings/Notes + 照片页。

版式对照官方 Word 模板（data/Woodards - Electrical Report.pdf），A4 竖版。
照片项数量不限，每 3 个一组排版。
"""
from io import BytesIO

import jmespath
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle
)

from pdfgen.common import cover, fontstyle
from pdfgen.common.checkbox import Checkbox
from pdfgen.common.layout import get_header
from pdfgen.common.utils import get_time_str, smart_image_import

styles = getSampleStyleSheet()

CONTENT_WIDTH = 515
DARK_BLUE = colors.HexColor(fontstyle.COLOR_DARK_BLUE)
LABEL_BG = colors.HexColor('#EFEFEF')

DECLARATION_PARAGRAPHS = [
    "This electrical safety check is for electrical safety purposes only and is in accordance with the "
    "requirements of the Residential Tenancies Regulations 2021 and is prepared in accordance with section 2 "
    "of the Australian / New Zealand Standard AS/NZS 3019, Electrical installations – Periodic verification "
    "to confirm that the installation is not damaged or has not deteriorated so as to impair electrical safety; "
    "and to identify installation defects and departures from the requirements that may give rise to danger.",
    "Advance Essential Services’ licenced electrician has carried out an electrical safety check of this "
    "residential tenancy per the requirements of the Residential Tenancies Regulations 2021 and set out in the "
    "Australian/New Zealand Standard AS/NZS 3019, “Electrical installations – Periodic verification, "
    "and have recorded their observations and recommendations.",
]


def _p(text, bold=False, size=10):
    if bold:
        return Paragraph(f'<font size="{size}"><b>{text}</b></font>', styles['Normal'])
    return Paragraph(f'<font size="{size}">{text}</font>', styles['Normal'])


def _bar(title):
    t = Table([[Paragraph(f'<b><font color="white">{title}</font></b>', styles['Normal'])]],
              colWidths=[CONTENT_WIDTH])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t


def _kv_section(title, rows):
    """label/value 两列分区表。row 为 (l1, v1, l2, v2)，或 (l1, v1) 表示值横跨整行。"""
    data = []
    spans = []
    for r, row in enumerate(rows):
        if len(row) == 2:
            data.append([_p(row[0], bold=True), _p(row[1]), '', ''])
            spans.append(('SPAN', (1, r), (3, r)))
        else:
            data.append([_p(row[0], bold=True), _p(row[1]), _p(row[2], bold=True), _p(row[3])])
    table = Table(data, colWidths=[132, 126, 132, 125])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), LABEL_BG),
        ('BACKGROUND', (2, 0), (2, -1), LABEL_BG),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ] + spans))
    return [_bar(title), table, Spacer(1, 8)]


def _text_area(title, content, min_height=90):
    body = Table([[Paragraph(str(content or ''), styles['Normal'])]],
                 colWidths=[CONTENT_WIDTH], rowHeights=None)
    body.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), max(6, min_height)),
    ]))
    return [_bar(title), body, Spacer(1, 8)]


# ------------------------------------------------------------------ page 2

def get_certificate_page(import_data: dict):
    base = jmespath.search("baseInfo", import_data) or {}
    details = jmespath.search("elecCheckDetails", import_data) or {}
    client = base.get('clientBranch') or {}
    inspector = base.get('inspector') or {}
    company = base.get('company') or {}

    result = list()
    result += get_header(total_width=CONTENT_WIDTH)

    title = Table([[Paragraph(
        f'<para align="center"><font size="17" color="{fontstyle.COLOR_DARK_BLUE}">'
        f'<b>ELECTRICAL SAFETY CERTIFICATE</b></font></para>', styles['Normal'])]],
        colWidths=[CONTENT_WIDTH])
    title.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    result.append(title)
    result.append(Spacer(1, 10))

    info_rows = [
        [_p('Reference ID:', bold=True), _p(base.get('referenceId', '')),
         _p('Inspection Date:', bold=True), _p(get_time_str(base.get('inspectedDate', '')))],
        [_p('Property Address:', bold=True), _p(base.get('propertyAddress', '')),
         _p('NEXT Electrical Safety Check Due:', bold=True), _p(get_time_str(base.get('nextCheckDue', '')))],
        [_p('Description of Premises:', bold=True), _p(base.get('premisesDescription', '') or ''),
         _p('Client:', bold=True), _p(client.get('agentName', ''))],
    ]
    info_table = Table(info_rows, colWidths=[110, 160, 135, 110])
    info_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), LABEL_BG),
        ('BACKGROUND', (2, 0), (2, -1), LABEL_BG),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    result.append(info_table)
    result.append(Spacer(1, 10))

    result.append(_bar('ELECTRICIAN INFORMATION'))
    elec_rows = [
        [_p('Inspector:', bold=True), _p(inspector.get('name', '')),
         _p('Company:', bold=True), _p(company.get('name', ''))],
        [_p('Licence No.:', bold=True), _p(inspector.get('licenceNo', '')),
         '', _p(company.get('address', ''))],
    ]
    elec_table = Table(elec_rows, colWidths=[110, 160, 135, 110])
    elec_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), LABEL_BG),
        ('BACKGROUND', (2, 0), (2, -1), LABEL_BG),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    result.append(elec_table)
    result.append(Spacer(1, 12))

    # OVERALL FINDINGS
    result.append(_bar('OVERALL FINDINGS'))
    overall = details.get('overallFindings') or []
    rows = []
    for item in overall:
        options = (item.get('options') or ['', ''])[:2]
        ticked = (item.get('tickedPos') or '').lower() == (options[0] or '').lower()
        checkbox_pair = Table([[
            Checkbox(options[0], ticked, font_size=9, color=colors.green, bold=True),
            Checkbox(options[1] if len(options) > 1 else '', not ticked, font_size=9,
                     color=colors.red, bold=True)]],
            colWidths=[88, 100])
        rows.append([
            _p(str(item.get('label', '')).replace('\n', '<br/>'), bold=True),
            checkbox_pair,
            Paragraph(str(item.get('remark', '') or ''), styles['Normal']),
        ])
    if rows:
        overall_table = Table(rows, colWidths=[145, 200, 170],
                              rowHeights=[52] * len(rows))
        overall_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), LABEL_BG),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        result.append(overall_table)
    return result


# ------------------------------------------------------------------ page 3

def get_services_page(import_data: dict):
    d = jmespath.search("elecCheckDetails", import_data) or {}
    mains = d.get('mains') or {}
    earth = d.get('mainEarth') or {}
    sb = d.get('switchboard') or {}
    db = d.get('distributionBoard') or {}
    fc = d.get('finalCircuits') or {}

    result = list()
    result += get_header(total_width=CONTENT_WIDTH)
    result.append(Paragraph(
        f'<font size="15" color="{fontstyle.COLOR_DARK_BLUE}"><b>Electrical Safety Services</b></font>',
        styles['Heading3']))

    result += _kv_section('MAINS', [
        ('Type', mains.get('type', ''), 'Mains Entry Condition', mains.get('entryCondition', '')),
        ('Supply', mains.get('supply', ''), 'Size (Estimate)', mains.get('size', '')),
        ('Mains Cable Condition to Switchboard', mains.get('cableCondition', ''),
         'Main Switch Type', mains.get('switchType', '')),
    ])
    result += _kv_section('MAIN EARTH', [
        ('Type', earth.get('type', ''), 'Condition of Connection', earth.get('connectionCondition', '')),
        ('Size (Estimate)', earth.get('size', ''), 'Earth Resistance Test', earth.get('resistanceTest', '')),
        ('Accessibility / Location', earth.get('location', '')),
    ])
    result += _kv_section('METER BOARD / MAIN SWITCHBOARD', [
        ("RCD's Installed", sb.get('rcdInstalled', ''), 'Earth Bar Present', sb.get('earthBar', '')),
        ('Fuses / Circuit Breakers Correctly Labelled', sb.get('fusesLabelled', ''),
         'MEN Link Present', sb.get('menLink', '')),
        ('RCD Trip Test', sb.get('rcdTripTest', ''), 'IP Rating / Fire Rating', sb.get('ipFireRating', '')),
        ('Polarity Test', sb.get('polarityTest', ''), 'Overall Condition', sb.get('overallCondition', '')),
        ('Final Sub Circuit Earth Resistance Test', sb.get('subCircuitEarthTest', ''),
         'Location', sb.get('location', '')),
    ])
    result += _kv_section('DISTRIBUTION BOARD', [
        ('Distribution Board Present', db.get('present', ''),
         'Submain Switch Condition', db.get('submainCondition', '')),
        ("Fuses / MCB's Correctly Labelled", db.get('fusesLabelled', ''),
         'Earth Bar Present', db.get('earthBar', '')),
        ('Number of MCB', db.get('mcbCount', ''), 'Circuits Labelled', db.get('circuitsLabelled', '')),
        ('Number of Fuses', db.get('fusesCount', ''), 'Overall Condition', db.get('overallCondition', '')),
        ('Number of RCD / RCBO', db.get('rcdCount', ''), 'Location', db.get('location', '')),
    ])
    result += _kv_section('FINAL CIRCUIT CABLES', [
        ('Final Circuit Cable Type', fc.get('cableType', ''),
         'Bare Earths Sleeved', fc.get('bareEarthsSleeved', '')),
        ('Condition of Insulation', fc.get('insulationCondition', ''),
         'Rewiring Required', fc.get('rewiringRequired', '')),
        ('Cables Correctly Supported', fc.get('cablesSupported', ''),
         'Number of Circuits to Rewire', fc.get('circuitsToRewire', '')),
    ])
    return result


# ------------------------------------------------------------------ page 4

def get_fittings_page(import_data: dict):
    d = jmespath.search("elecCheckDetails", import_data) or {}
    f = d.get('fittings') or {}

    result = list()
    result += get_header(total_width=CONTENT_WIDTH)
    result += _kv_section('FITTINGS', [
        ('Socket Outlets', f.get('socketOutlets', ''), 'Extract Fans', f.get('extractFans', '')),
        ('Switches', f.get('switches', ''), 'Wet Areas IP Rating', f.get('wetAreasIp', '')),
        ('Indoor Lighting', f.get('indoorLighting', ''), 'Exterior Lighting', f.get('exteriorLighting', '')),
        ('Hot Water', f.get('hotWater', ''), 'Heating', f.get('heating', '')),
        ('Rangehood', f.get('rangehood', ''), 'Oven', f.get('oven', '')),
        ('Other Fittings', f.get('otherFittings', '')),
        ('Garage / Shed', f.get('garageShed', '')),
    ])
    result += _text_area('URGENT REPAIRS', d.get('urgentRepairs', ''), min_height=80)
    result += _text_area('OBSERVATIONS', d.get('observations', ''), min_height=80)
    for para in DECLARATION_PARAGRAPHS:
        result.append(Paragraph(f'<font size="8.5">{para}</font>', styles['Normal']))
        result.append(Spacer(1, 6))
    return result


# ------------------------------------------------------------------ page 5

def _photo_group_table(items: list):
    col_w = CONTENT_WIDTH / 3.0
    n = len(items)

    def pad(row):
        return row + [''] * (3 - n)

    title_row = pad([Paragraph(f'<b>{item.get("title", "")}</b>', styles['Normal']) for item in items])
    check_row = pad([
        Table([[
            Checkbox("COMPLIANT", (item.get('status') or '').lower() == 'compliant',
                     font_size=6.5, color=colors.black, bold=True),
            Checkbox("NON-COMPLIANT", (item.get('status') or '').lower() != 'compliant',
                     font_size=6.5, color=colors.black, bold=True),
        ]], colWidths=[col_w * 0.45, col_w * 0.55])
        for item in items])
    photo_row = pad([smart_image_import(item.get('photoUrl'), max_width=col_w - 14, max_height=190) or ''
                     for item in items])

    table = Table([title_row, check_row, photo_row],
                  colWidths=[col_w] * 3, rowHeights=[24, 20, 205])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), LABEL_BG),
        ('VALIGN', (0, 0), (-1, 1), 'MIDDLE'),
        ('VALIGN', (0, 2), (-1, 2), 'MIDDLE'),
        ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    return table


def get_appliance_report(import_data: dict):
    items = jmespath.search("elecCheckDetails.applianceReport[*]", import_data) or []
    if not items:
        return []
    result = list()
    result += get_header(total_width=CONTENT_WIDTH)
    title = Table([[Paragraph(
        f'<para align="center"><font size="17" color="{fontstyle.COLOR_DARK_BLUE}">'
        f'<b>ELECTRICAL APPLIANCE REPORT</b></font></para>', styles['Normal'])]],
        colWidths=[CONTENT_WIDTH])
    title.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    result.append(title)
    result.append(Spacer(1, 10))
    for i in range(0, len(items), 3):
        result.append(KeepTogether([_photo_group_table(items[i:i + 3]), Spacer(1, 12)]))
    return result


# ------------------------------------------------------------------ build

def build(import_data: dict) -> bytes:
    """生成 Electrical 报告 PDF，返回字节流。"""
    buffer = BytesIO()
    frame_A4 = Frame(40, 40, A4[0] - 80, A4[1] - 80, id='frameA4')
    template_A4 = PageTemplate(id='A4', pagesize=A4, frames=[frame_A4])
    doc = BaseDocTemplate(buffer, pageTemplates=[template_A4])

    story = list()
    story += cover.get_cover(import_data)
    story.append(PageBreak())
    story += get_certificate_page(import_data)
    story.append(PageBreak())
    story += get_services_page(import_data)
    story.append(PageBreak())
    story += get_fittings_page(import_data)
    photo_part = get_appliance_report(import_data)
    if photo_part:
        story.append(PageBreak())
        story += photo_part
    doc.build(story)
    return buffer.getvalue()
