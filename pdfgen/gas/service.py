"""Gas Safety Service 页：设备明细表、检测表、安装检查表、固定声明。"""
import jmespath
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle

from pdfgen.common import fontstyle
from pdfgen.common.fontstyle import inline_style
from pdfgen.common.layout import get_header

styles = getSampleStyleSheet()


def _section_header(title, width=800):
    header_table = Table([[Paragraph(
        inline_style(title, size=11, color="#FFFFFF", align="center", bold=True),
        styles["BodyText"])]], colWidths=[width])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), fontstyle.COLOR_DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    return header_table


def get_app_detail_table(import_data: dict):
    result = list()
    result.append(Paragraph(
        f'<para ><font size="14" color="{fontstyle.COLOR_DARK_BLUE}"><b>Gas Safety Service</b></font></para>',
        styles['Heading3']))
    result.append(_section_header("APPLIANCE DETAILS"))

    data = jmespath.search("gasCheckDetails.applianceDetails[*]", import_data) or []
    appliance_detail_data = [
        ['', 'TYPE', 'LOCATION', 'MANUFACTURER', 'MODEL NO.', 'SERIAL NO.', 'FLUE TYPE', 'INSTALLATION']]
    for index, item in enumerate(data):
        appliance_detail_data.append([
            str(index + 1),
            (item.get('type') or {}).get('value', ''),
            (item.get('location') or {}).get('value', ''),
            (item.get('manufacturer') or {}).get('value', ''),
            (item.get('modelNo') or {}).get('value', ''),
            (item.get('serialNo') or {}).get('value', ''),
            (item.get('flueType') or {}).get('value', ''),
            (item.get('installation') or {}).get('value', ''),
        ])
    if len(data) < 4:
        appliance_detail_data += [[]] * (4 - len(data))

    appliance_details = Table(appliance_detail_data, colWidths=[20, 112, 112, 111, 111, 111, 111, 111])
    app_bl_co = [('BACKGROUND', (0, i), (-1, i), colors.white if i % 2 == 1 else colors.lightgrey)
                 for i in range(1, len(appliance_detail_data))]
    appliance_details.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)] + app_bl_co))
    result.append(appliance_details)
    return result


def get_service_ins_table(import_data: dict):
    result = list()
    result.append(_section_header("SERVICE & INSPECTION DETAILS"))

    data = jmespath.search("gasCheckDetails.serviceAndInspection[*]", import_data) or []
    rows = [['', 'OPERATING PRESSURE\n(KPA)', 'VENTILATION', 'FLUE VISUAL',
             'FLUE OPERATION', 'CARBON MONOXIDE TEST', 'SAFE TO USE']]
    for index, item in enumerate(data):
        rows.append([
            str(index + 1),
            (item.get('operatingPressure') or {}).get('value', ''),
            (item.get('ventilation') or {}).get('value', ''),
            (item.get('flueVisual') or {}).get('value', ''),
            (item.get('flueOperation') or {}).get('value', ''),
            (item.get('carbonMonoxideTest') or {}).get('value', ''),
            (item.get('safeToUse') or {}).get('value', ''),
        ])
    if len(data) < 4:
        rows += [[]] * (4 - len(data))

    table = Table(rows, colWidths=[20, 115, 105, 120, 140, 170, 130])
    bg_co = [('BACKGROUND', (0, i), (-1, i), colors.white if i % 2 == 1 else colors.lightgrey)
             for i in range(1, len(rows))]
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ] + bg_co))
    result.append(table)
    return result


def get_install_det_table(import_data: dict):
    ins_details = list()
    header = Table([["INSTALLATION DETAILS", "RESULT"]], colWidths=[680, 120])
    header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), fontstyle.COLOR_DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    ins_details.append(header)

    data = jmespath.search("gasCheckDetails.installationDetails[*]", import_data) or []
    if not data:
        return ins_details

    ins_detail_data = []
    for item in data:
        result_field = item.get('result') or {}
        ins_detail_data.append([
            str(item.get('order', '')),
            result_field.get('label', ''),
            Paragraph(str(item.get('description', '')), styles['Normal']),
            result_field.get('value', '')
        ])

    table = Table(ins_detail_data, colWidths=[20, 200, 460, 120])
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (2, -1), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    ins_details.append(table)
    return ins_details


DECLARATION_TEXT = (
    "Advance Essential Services, being responsible for the inspection of the identified "
    "gas appliances or installations in the rental property or rooming house, "
    "particulars of which are described here, having exercised reasonable skill and "
    "care when carrying out the inspection, hereby declare on the date of inspection "
    "that the information in this report, including the observations and "
    "recommendations, provides an accurate assessment of the condition of the gas "
    "appliances or installations in the rental property or rooming house taking into "
    "account the stated extent of the installation and the limitations of the "
    "inspection and testing.")


def get_declaration_table(import_data: dict):
    carbon = jmespath.search("gasCheckDetails.carbonAlarmDetails", import_data) or {}
    data = [
        ['CARBON MONOXIDE ALARM DETAILS', 'DECLARATION'],
        [f"APPROVED ALARM FITTED   {carbon.get('approvedAlarmFitted', '') or ''}",
         Paragraph(DECLARATION_TEXT, styles["Normal"])],
        [f"ALARM TEST   {carbon.get('alarmTest', '') or ''}", ''],
        [f"NO. APPLIANCES TESTED   {carbon.get('noAppliancesTested', '') or ''}", ''],
    ]

    table = Table(data, colWidths=[220, 580])
    table.setStyle(TableStyle([
        ('SPAN', (1, 1), (1, 3)),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor(fontstyle.COLOR_DARK_BLUE)),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return [table]


def get_gas_safety_service(import_data: dict):
    res = list()
    res += get_header()
    res += get_app_detail_table(import_data)
    res += get_service_ins_table(import_data)
    res += get_install_det_table(import_data)
    res += get_declaration_table(import_data)
    return res
