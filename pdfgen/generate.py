import jmespath

from pdfgen.gas import generator as gas_generator
from pdfgen.smoke import generator as smoke_generator


def build_report_pdf(data: dict) -> bytes:
    """按 baseInfo.type 分发到对应报告生成器，返回 PDF 字节流。"""
    report_type = (jmespath.search("baseInfo.type", data) or '').lower()
    if report_type in ('smoke', 'smoke alarm'):
        return smoke_generator.build(data)
    if report_type in ('gas', ''):
        return gas_generator.build(data)
    if report_type == 'electrical':
        raise ValueError("Electrical report is not supported yet")
    raise ValueError(f"Unknown report type: {report_type}")
