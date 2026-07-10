from reportlab.lib import colors
from reportlab.platypus import Flowable


class Checkbox(Flowable):
    """方框 + 对勾的勾选框，勾用线段绘制，不依赖字体是否包含 ✓ 字形。"""

    def __init__(self, label, checked=True, bold=False, font_size=15, color=colors.darkblue):
        super().__init__()
        self.label = label
        self.checked = checked
        # 按文字长度估算宽度，避免窄单元格里被判定溢出
        self.width = 15 + max(20, int(len(label) * font_size * 0.6))
        self.height = max(15, font_size + 2)
        self.font_size = font_size
        self.bold = bold
        self.color = color

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setFillColor(self.color)
        self.canv.setLineWidth(1)
        self.canv.rect(0, 0, 10, 10)
        if self.checked:
            self.canv.setLineWidth(1.6)
            self.canv.setLineCap(1)
            p = self.canv.beginPath()
            p.moveTo(2, 5)
            p.lineTo(4.2, 2.2)
            p.lineTo(8.5, 8.5)
            self.canv.drawPath(p, stroke=1, fill=0)
        self.canv.setFont("Helvetica-Bold" if self.bold else "Helvetica", self.font_size)
        self.canv.drawString(15, 0, self.label)
