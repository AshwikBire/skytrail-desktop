"""
Holographic zodiac wheel — custom-painted circular birth chart display,
matching the Jarvis HUD visual language (glowing cyan rings, particles, HUD ticks).
"""
import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QFont

CYAN = QColor(70, 220, 255)
CYAN_DIM = QColor(30, 120, 160)
AMBER = QColor(255, 200, 80)
MAGENTA = QColor(220, 120, 255)

PLANET_GLYPHS = {
    "sun": "☉", "moon": "☽", "mercury": "☿", "venus": "♀", "mars": "♂",
    "jupiter": "♃", "saturn": "♄", "rahu": "☊", "ketu": "☋", "ascendant": "AC",
}

PLANET_COLORS = {
    "sun": AMBER, "moon": QColor(220, 240, 255), "mercury": QColor(120, 255, 180),
    "venus": QColor(255, 160, 220), "mars": QColor(255, 100, 100),
    "jupiter": QColor(255, 210, 100), "saturn": QColor(160, 160, 255),
    "rahu": MAGENTA, "ketu": QColor(150, 90, 200), "ascendant": CYAN,
}


class ZodiacWheel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(380, 380)
        self._angle = 0.0
        self.chart = None
        self.lang = "en"

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(33)

    def set_chart(self, chart, lang="en"):
        self.chart = chart
        self.lang = lang
        self.update()

    def _tick(self):
        self._angle = (self._angle + 0.15) % 360
        self.update()

    def paintEvent(self, event):
        from translations import sign_name

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        outer_r = min(w, h) / 2 * 0.92
        sign_ring_r = outer_r * 0.86
        planet_ring_r = outer_r * 0.62

        # Background glow
        glow = QRadialGradient(cx, cy, outer_r * 1.3)
        glow.setColorAt(0.0, QColor(20, 60, 90, 60))
        glow.setColorAt(1.0, QColor(6, 10, 20, 0))
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), outer_r * 1.3, outer_r * 1.3)

        # Outer boundary ring
        painter.setPen(QPen(CYAN, 1.6))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), outer_r, outer_r)
        painter.drawEllipse(QPointF(cx, cy), sign_ring_r, sign_ring_r)

        # Rotating faint tick ring
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self._angle)
        tick_pen = QPen(QColor(70, 220, 255, 70), 1)
        painter.setPen(tick_pen)
        for i in range(72):
            a = math.radians(i * 5)
            tick_len = 8 if i % 6 == 0 else 4
            x1, y1 = outer_r * 1.05 * math.cos(a), outer_r * 1.05 * math.sin(a)
            x2, y2 = (outer_r * 1.05 - tick_len) * math.cos(a), (outer_r * 1.05 - tick_len) * math.sin(a)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        painter.restore()

        # 12 sign divisions + labels
        painter.setPen(QPen(CYAN_DIM, 1))
        for i in range(12):
            a = math.radians(i * 30 - 90)  # start at top (Aries at top by convention here)
            x1, y1 = cx + planet_ring_r * 0.9 * math.cos(a), cy + planet_ring_r * 0.9 * math.sin(a)
            x2, y2 = cx + sign_ring_r * math.cos(a), cy + sign_ring_r * math.sin(a)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

            mid_a = math.radians(i * 30 + 15 - 90)
            label_r = (sign_ring_r + outer_r) / 2
            lx = cx + label_r * math.cos(mid_a)
            ly = cy + label_r * math.sin(mid_a)
            painter.setFont(QFont("Segoe UI", 9))
            painter.setPen(QPen(QColor(150, 220, 255, 200)))
            painter.drawText(int(lx - 30), int(ly - 10), 60, 20,
                              Qt.AlignmentFlag.AlignCenter, sign_name(i, self.lang))

        # Inner core glow
        core_grad = QRadialGradient(cx, cy, planet_ring_r * 0.5)
        core_grad.setColorAt(0.0, QColor(70, 220, 255, 40))
        core_grad.setColorAt(1.0, QColor(70, 220, 255, 0))
        painter.setBrush(QBrush(core_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), planet_ring_r * 0.5, planet_ring_r * 0.5)

        if self.chart is None:
            painter.setPen(QPen(QColor(70, 220, 255, 150)))
            painter.setFont(QFont("Consolas", 11))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Awaiting birth details...")
            painter.end()
            return

        # Plot planets around the wheel based on absolute longitude
        # Aries 0deg placed at top (-90deg), moving clockwise
        all_points = list(self.chart.planets) + [self.chart.ascendant]
        for p in all_points:
            a = math.radians(p.longitude - 90)
            r = planet_ring_r if p.key != "ascendant" else sign_ring_r * 0.98
            x = cx + r * math.cos(a)
            y = cy + r * math.sin(a)

            color = PLANET_COLORS.get(p.key, CYAN)
            glyph_glow = QRadialGradient(x, y, 16)
            glyph_glow.setColorAt(0.0, QColor(color.red(), color.green(), color.blue(), 160))
            glyph_glow.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 0))
            painter.setBrush(QBrush(glyph_glow))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x, y), 16, 16)

            painter.setPen(QPen(color))
            painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            glyph = PLANET_GLYPHS.get(p.key, "?")
            painter.drawText(int(x - 14), int(y - 12), 28, 24, Qt.AlignmentFlag.AlignCenter, glyph)

        painter.end()
