"""解析历史表单式 PDF（Word 模板生成的 AcroForm），映射成本系统的报告 JSON。

- 字段名做归一化（小写、去掉非字母数字），以容忍模板里命名不一致
  （如 'flue Pass/Fail/NA1' / 'flue_Pass/Fail/NA2'）。
- 照片存放在图像按钮字段的外观流里，逐层下钻 XObject 提取。
- photo_saver(jpeg_bytes) -> url 由调用方注入，parse 层不关心存储方式。
"""
import re
from io import BytesIO

from PIL import Image as PILImage
from pypdf import PdfReader

from pdfgen import constants


def _norm(name: str) -> str:
    return re.sub(r'[^a-z0-9]', '', str(name).lower())


def _wrap(value, label="", options=None):
    return {"value": value, "label": label, "options": options or []}


class _Fields:
    def __init__(self, reader: PdfReader):
        raw = reader.get_fields() or {}
        self.map = {_norm(k): v for k, v in raw.items()}

    def has(self, key):
        return key in self.map

    def value(self, key):
        f = self.map.get(key)
        if f is None:
            return ''
        v = f.get('/V')
        if v is None:
            return ''
        return str(v)

    def text(self, key):
        s = self.value(key).strip()
        if s in ('/Off',):
            return ''
        if s.startswith('/'):
            s = s[1:]
        return s.strip()

    def checked(self, key):
        return self.value(key) == '/Yes'

    def radio_first(self, key, default=True):
        """模板里的两态单选组：'/0' = 第一个选项，'/1' = 第二个。"""
        v = self.value(key)
        if v == '/0':
            return True
        if v == '/1':
            return False
        return default


def _combine_date(dm: str, year: str) -> str:
    """'24/01' + '/2025' -> '2025-01-24'（模板日期是 d/m 顺序）。"""
    m = re.match(r'(\d{1,2})\s*/\s*(\d{1,2})', dm or '')
    ym = re.search(r'(\d{4})', year or '')
    if not (m and ym):
        return ''
    day, month = int(m.group(1)), int(m.group(2))
    try:
        return f"{ym.group(1)}-{month:02d}-{day:02d}"
    except ValueError:
        return ''


# ---------------------------------------------------------------- photos

def _image_bytes(obj):
    try:
        data = obj.get_data()
        with PILImage.open(BytesIO(data)) as im:
            im = im.convert("RGB")
            out = BytesIO()
            im.save(out, format='JPEG', quality=90)
            return out.getvalue()
    except Exception as e:
        print(f"[parse image] {e}")
        return None


def _find_image_in(node, depth=0):
    if node is None or depth > 6:
        return None
    best = None
    res = node.get('/Resources')
    xo = res.get('/XObject') if res else None
    if not xo:
        return None
    for v in xo.get_object().values():
        obj = v.get_object()
        subtype = obj.get('/Subtype')
        candidate = None
        if subtype == '/Image':
            candidate = _image_bytes(obj)
        elif subtype == '/Form':
            candidate = _find_image_in(obj, depth + 1)
        if candidate and (best is None or len(candidate) > len(best)):
            best = candidate
    return best


def _extract_field_photos(reader: PdfReader) -> dict:
    """{归一化字段名: jpeg bytes}"""
    photos = {}
    for page in reader.pages:
        for annot in page.get('/Annots') or []:
            a = annot.get_object()
            name = a.get('/T')
            ap = a.get('/AP')
            if not name or not ap:
                continue
            n = ap.get('/N')
            n = n.get_object() if hasattr(n, 'get_object') else n
            if n is None:
                continue
            if hasattr(n, 'keys') and '/BBox' not in n:
                nodes = [v.get_object() for v in n.values()]
            else:
                nodes = [n]
            best = None
            for node in nodes:
                img = _find_image_in(node)
                if img and (best is None or len(img) > len(best)):
                    best = img
            if best:
                photos[_norm(str(name))] = best
    return photos


# ---------------------------------------------------------------- smoke

def _parse_smoke(fields: _Fields, photos: dict, photo_saver):
    inspected = _combine_date(fields.text('inspectiondate'), fields.text('inspectionyear'))
    next_due = _combine_date(fields.text('inspectiondate'), fields.text('nextsmokecheckyear'))

    alarms = []
    for i in range(1, 4):
        brand = fields.text(f'smokebrand{i}')
        location = fields.text(f'smokelocation{i}')
        expiry = fields.text(f'expiry{i}')
        photo = photos.get(f'smoke{i}')
        if not any([brand, location, expiry, photo]):
            continue
        status = 'Compliant'
        if fields.checked(f'smokefail{i}') and not fields.checked(f'smokepass{i}'):
            status = 'Non-Compliant'
        alarms.append({
            "status": status,
            "brand": brand,
            "location": location,
            "expiry": expiry,
            "photoUrl": photo_saver(photo) if photo else "",
        })

    overall = 'Compliant' if fields.radio_first('smokepass', default=all(
        a['status'] == 'Compliant' for a in alarms) if alarms else True) else 'Non-Compliant'

    return {
        "baseInfo": {
            "type": "Smoke",
            "clientBranch": {
                "agentName": fields.text('clientname'),
                "branchAddress": fields.text('clientaddress'),
            },
            "referenceId": fields.text('reference'),
            "rentalType": "Rooming House" if fields.checked('rooming') else "Rental Property",
            "propertyAddress": fields.text('property'),
            "buildingClass": fields.text('buildingclass'),
            "inspectedDate": inspected,
            "nextCheckDue": next_due,
            "inspector": {
                "name": fields.text('electrician'),
                "licenceNo": fields.text('electricianlicence'),
            },
            "company": {
                "name": fields.text('ourcompany'),
                "address": fields.text('ouraddress'),
            },
        },
        "smokeCheckDetails": {
            "metCurrentRequirements": fields.checked('smokecurrent'),
            "metNewRequirements": fields.checked('smokenew'),
            "overallCompliant": overall,
            "alarms": alarms,
        },
    }


# ---------------------------------------------------------------- gas

_GAS_OVERALL_FIELDS = [
    ("compliantnoncompliant", "overallgascompliant"),
    ("recommendation", "overallgasrecommendation"),
    ("faulty", "overallgasfaulty"),
    ("safety", "overallgassafety"),
    ("disconnected", "overallgasurgent"),
]


def _parse_gas(fields: _Fields, photos: dict, photo_saver):
    inspected = _combine_date(fields.text('inspectiondate'), fields.text('inspectionyear'))
    next_due = _combine_date(fields.text('inspectiondate'), fields.text('nextsafetycheckyear'))

    overall_findings = []
    for spec, (field_key, remark_key) in zip(constants.GAS_OVERALL_FINDINGS, _GAS_OVERALL_FIELDS):
        first = fields.radio_first(field_key, default=True)
        overall_findings.append({
            "label": spec["label"],
            "options": spec["options"],
            "tickedPos": spec["options"][0] if first else spec["options"][1],
            "remark": fields.text(remark_key),
        })

    appliance_details = []
    service_inspection = []
    for i in range(1, 5):
        type_v = fields.text(f'gastype{i}')
        loc_v = fields.text(f'gaslocation{i}')
        manu_v = fields.text(f'gasmanu{i}')
        model_v = fields.text(f'gasmodel{i}')
        serial_v = fields.text(f'gasserial{i}')
        flue_v = fields.text(f'gasflue{i}')
        install_v = fields.text(f'gasinstall{i}')
        if any([type_v, loc_v, manu_v, model_v, serial_v]):
            appliance_details.append({
                "type": _wrap(type_v, "TYPE", constants.GAS_APPLIANCE_TYPES),
                "location": _wrap(loc_v, "LOCATION", constants.GAS_LOCATIONS),
                "manufacturer": _wrap(manu_v, "MANUFACTURER", constants.GAS_MANUFACTURERS),
                "modelNo": _wrap(model_v, "MODEL NO."),
                "serialNo": _wrap(serial_v, "SERIAL NO."),
                "flueType": _wrap(flue_v, "FLUE TYPE", constants.GAS_FLUE_TYPES),
                "installation": _wrap(install_v, "INSTALLATION", constants.GAS_INSTALL_OPTIONS),
            })

        kpa = fields.text(f'kpa{i}')
        venti = fields.text(f'ventipassfailna{i}')
        flue = fields.text(f'fluepassfailna{i}')
        flue_op = fields.text(f'flueoppassfailna{i}')
        carbon = fields.text(f'carbonpassfailna{i}')
        safe = fields.text(f'safeynna{i}')
        if any([kpa, venti, flue, flue_op, carbon, safe]):
            service_inspection.append({
                "operatingPressure": _wrap(kpa, "OPERATING PRESSURE\n(KPA)"),
                "ventilation": _wrap(venti, "VENTILATION", constants.PASS_FAIL_NA),
                "flueVisual": _wrap(flue, "FLUE VISUAL", constants.PASS_FAIL_NA),
                "flueOperation": _wrap(flue_op, "FLUE OPERATION", constants.PASS_FAIL_NA),
                "carbonMonoxideTest": _wrap(carbon, "CARBON MONOXIDE TEST", constants.PASS_FAIL_NA),
                "safeToUse": _wrap(safe, " SAFE TO USE", constants.YES_NO_NA),
            })

    installation_details = []
    for item in constants.GAS_INSTALLATION_ITEMS:
        n = item["order"]
        key = 'resultyn1' if n == 1 else f'passfailresult{n}'
        installation_details.append({
            "order": n,
            "description": item["description"],
            "result": _wrap(fields.text(key) or "Pass", item["label"], ["Pass", "Fail"]),
        })

    appliance_report = []
    for i in range(1, 7):
        text = fields.text(f'gasappl{i}')
        photo = photos.get(f'gasapp{i}afimage')
        if not (text or photo):
            continue
        lines = [ln.strip() for ln in re.split(r'[\r\n]+', text) if ln.strip()]
        title = lines[0] if lines else ''
        remark = ' '.join(lines[1:]) if len(lines) > 1 else ''
        compliant = True
        if fields.checked(f'gasappfail{i}') and not fields.checked(f'gasappcomp{i}'):
            compliant = False
        appliance_report.append({
            "type": {
                "value": title,
                "label": "",
                "radio-value": "Compliant" if compliant else "Non-Compliant",
                "options": [{"name": title, "radio": ["Compliant", "Non-Compliant"]}],
            },
            "remark": remark,
            "photoUrl": [photo_saver(photo)] if photo else [],
        })

    return {
        "baseInfo": {
            "type": "Gas",
            "clientBranch": {
                "agentName": fields.text('clientname'),
                "branchAddress": fields.text('clientaddress'),
            },
            "referenceId": fields.text('reference'),
            "rentalType": "Rooming House" if fields.checked('rooming') else "Rental Property",
            "propertyAddress": fields.text('property'),
            "inspectedDate": inspected,
            "nextCheckDue": next_due,
            "inspector": {
                "name": fields.text('gasinspector'),
                "licenceNo": fields.text('gaslicence'),
            },
        },
        "gasCheckDetails": {
            "overallFindings": overall_findings,
            "applianceDetails": appliance_details,
            "serviceAndInspection": service_inspection,
            "installationDetails": installation_details,
            "gasApplianceReport": appliance_report,
            "carbonAlarmDetails": {
                "approvedAlarmFitted": fields.text('carbonfitted'),
                "alarmTest": fields.text('carbontest'),
                "noAppliancesTested": fields.text('totaltested'),
            },
        },
    }


# ---------------------------------------------------------------- entry

def parse_template_pdf(file_obj, photo_saver):
    """解析 AcroForm 模板 PDF。返回报告 JSON；不是表单 PDF 时返回 None。"""
    reader = PdfReader(file_obj)
    if reader.is_encrypted:
        reader.decrypt("")
    fields = _Fields(reader)
    if not fields.map:
        return None
    photos = _extract_field_photos(reader)

    if fields.checked('smoke') or fields.has('smokebrand1'):
        return _parse_smoke(fields, photos, photo_saver)
    if fields.checked('gas') or fields.has('gastype1'):
        return _parse_gas(fields, photos, photo_saver)
    if fields.checked('electrical'):
        raise ValueError("Electrical report import is not supported yet")
    return None
