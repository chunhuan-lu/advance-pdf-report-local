from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle

COLOR_DARK_BLUE = "#0A234F"


def inline_style(text, size=11, color="#000000", align="left", bold=False, italic=False, underline=False):
    """生成 ReportLab Paragraph 用的内联样式文本。"""
    tags = text
    if underline:
        tags = f"<u>{tags}</u>"
    if italic:
        tags = f"<i>{tags}</i>"
    if bold:
        tags = f"<b>{tags}</b>"
    return f'<para align="{align}"><font size="{size}" color="{color}">{tags}</font></para>'


white_on_blue_style = ParagraphStyle(
    name='WhiteOnBlue',
    fontName='Helvetica-Bold',
    fontSize=11,
    textColor=colors.white,
    leading=14,
    alignment=0,
    spaceBefore=4,
    spaceAfter=4,
    leftIndent=4,
    rightIndent=4,
)

title_style = ParagraphStyle(
    name="MyTitle",
    fontName="Helvetica-Bold",
    fontSize=50,
    leading=60,
    alignment=1,
    textColor=colors.black,
    spaceAfter=12,
)
