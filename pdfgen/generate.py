import jmespath

from pdfgen.electrical import generator as electrical_generator
from pdfgen.gas import generator as gas_generator
from pdfgen.smoke import generator as smoke_generator


_DETAILS_TYPE = {
    'smokeCheckDetails': 'smoke',
    'elecCheckDetails': 'electrical',
    'gasCheckDetails': 'gas',
}


def build_report_pdf(data: dict) -> bytes:
    """按 baseInfo.type 分发到对应报告生成器，返回 PDF 字节流。

    声明的 type 和实际携带的详情块不一致时，以详情块为准，
    防止调用方类型映射出错时生成一份空报告。
    """
    report_type = (jmespath.search("baseInfo.type", data) or '').lower()
    if report_type in ('smoke alarm',):
        report_type = 'smoke'

    present = [t for k, t in _DETAILS_TYPE.items() if data.get(k)]
    if len(present) == 1 and report_type != present[0]:
        report_type = present[0]

    if report_type == 'smoke':
        return smoke_generator.build(data)
    if report_type in ('gas', ''):
        return gas_generator.build(data)
    if report_type == 'electrical':
        return electrical_generator.build(data)
    raise ValueError(f"Unknown report type: {report_type}")
