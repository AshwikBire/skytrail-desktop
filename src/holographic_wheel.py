"""
Holographic Zodiac Wheel — Glowing, semi-transparent planets at their actual
positions. Matches the Jarvis visual style with a celestial luxury theme.
"""

import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QRadialGradient,
    QFont, QPainterPath, QLinearGradient
)

# Luxury Celestial Color Palette
OBSIDIAN = "#0B0A08"
ESPRESSO = "#15120D"
DARK_WALNUT = "#1D1810"
ROYAL_GOLD = "#D4AF37"
CHAMPAGNE_GOLD = "#F4D77B"
IVORY = "#FFF8E7"
WARM_GRAY = "#B8AE9C"

# Planet colors in luxury celestial theme
PLANET_COLORS = {
    "sun": "#F4D77B",      # Champagne Gold
    "moon": "#FFF8E7",     # Ivory
    "mercury": "#B8AE9C",  # Warm Gray
    "venus": "#F4D77B",    # Champagne Gold
    "mars": "#C41E3A",     # Deep Red
    "jupiter": "#D4AF37",  # Royal Gold
    "saturn": "#8B7355",   # Bronze
    "rahu": "#1D1810",     # Dark Walnut
    "ketu": "#B8AE9C",     # Warm Gray
    "uranus": "#4A90D9",   # Deep Blue
    "neptune": "#2E8B57",  # Sea Green
    "pluto": "#8B0000",    # Dark Red
}

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANET_GLYPH = {
    "sun": "☉", "moon": "☽", "mercury": "☿", "venus": "♀",
    "mars": "♂", "jupiter": "♃", "saturn": "♄", "rahu": "☊",
    "ketu": "☋", "ascendant": "ASC",
}

PLANET_NAMES = {
    "sun": "Sun", "moon": "Moon", "mercury": "Mercury",
    "venus": "Venus", "mars": "Mars", "jupiter": "Jupiter",
    "saturn": "Saturn", "rahu": "Rahu", "ketu": "Ketu",
    "ascendant": "Ascendant"
}


class ZodiacWheel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chart = None
        self.lang = "en"
        self.glow_radius = 0.0
        self.glow_direction = 1
        self.setMinimumSize(400, 400)
        self.setMaximumSize(600, 600)
        
        # Animation timer for glow effect
        self.timer = QTimer()
        self.timer.timeout.connect(self._animate_glow)
        self.timer.start(50)
    
    def set_chart(self, chart, lang="en"):
        """Set the chart data to display"""
        self.chart = chart
        self.lang = lang
        self.update()
    
    def _animate_glow(self):
        """Animate the glow radius for planets"""
        self.glow_radius += 0.05 * self.glow_direction
        if self.glow_radius > 1.0:
            self.glow_direction = -1
        elif self.glow_radius < 0.0:
            self.glow_direction = 1
        self.update()
    
    def paintEvent(self, event):
        """Paint the zodiac wheel with luxury celestial theme"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        center = rect.center()
        center_x = float(center.x())
        center_y = float(center.y())
        size = min(rect.width(), rect.height())
        radius = size * 0.42
        inner_radius = radius * 0.78
        
        # --- Draw Background Glow ---
        bg_gradient = QRadialGradient(center_x, center_y, radius * 1.2)
        bg_gradient.setColorAt(0.0, QColor(ROYAL_GOLD).lighter(120))
        bg_gradient.setColorAt(0.3, QColor(ESPRESSO))
        bg_gradient.setColorAt(1.0, QColor(OBSIDIAN))
        painter.fillRect(rect, bg_gradient)
        
        # --- Draw Outer Ring with Gold Border ---
        painter.setPen(QPen(QColor(ROYAL_GOLD), 2.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(center_x, center_y), radius + 8, radius + 8)
        
        # --- Draw Inner Ring ---
        painter.setPen(QPen(QColor(CHAMPAGNE_GOLD), 1.5))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)
        
        # --- Draw Zodiac Signs with Luxury Colors ---
        sign_font = QFont("Cinzel", 10, QFont.Weight.Bold)
        painter.setFont(sign_font)
        
        for i, sign in enumerate(SIGNS):
            angle = math.radians(i * 30 - 90)
            x = center_x + (radius + 20) * math.cos(angle)
            y = center_y + (radius + 20) * math.sin(angle)
            
            # Sign color based on element
            if i in [0, 3, 6, 9]:  # Cardinal - Royal Gold
                color = ROYAL_GOLD
            elif i in [1, 4, 7, 10]:  # Fixed - Champagne Gold
                color = CHAMPAGNE_GOLD
            else:  # Mutable - Warm Gray
                color = WARM_GRAY
            
            painter.setPen(QPen(QColor(color), 1.5))
            painter.drawText(int(x - 18), int(y + 6), sign)
        
        # --- Draw Zodiac Segments with Gold Tints ---
        for i in range(12):
            start_angle = i * 30 - 90
            painter.setPen(QPen(QColor(ROYAL_GOLD), 1.0, Qt.PenStyle.DotLine))
            painter.drawArc(
                int(center_x - inner_radius),
                int(center_y - inner_radius),
                int(inner_radius * 2),
                int(inner_radius * 2),
                start_angle * 16,
                30 * 16
            )
        
        # --- Draw Inner Circle with Luxury Gradient ---
        inner_gradient = QRadialGradient(center_x, center_y, inner_radius)
        inner_gradient.setColorAt(0.0, QColor(ESPRESSO))
        inner_gradient.setColorAt(0.5, QColor(DARK_WALNUT))
        inner_gradient.setColorAt(1.0, QColor(OBSIDIAN))
        painter.setPen(QPen(QColor(ROYAL_GOLD), 1.5))
        painter.setBrush(QBrush(inner_gradient))
        painter.drawEllipse(QPointF(center_x, center_y), inner_radius, inner_radius)
        
        # --- Draw Planets ---
        if self.chart:
            self._draw_planets(painter, center_x, center_y, inner_radius)
        
        # --- Draw Center Decoration ---
        center_gradient = QRadialGradient(center_x, center_y, 20)
        center_gradient.setColorAt(0.0, QColor(ROYAL_GOLD))
        center_gradient.setColorAt(0.5, QColor(CHAMPAGNE_GOLD))
        center_gradient.setColorAt(1.0, QColor(ROYAL_GOLD).darker(150))
        painter.setPen(QPen(QColor(ROYAL_GOLD), 1.0))
        painter.setBrush(QBrush(center_gradient))
        painter.drawEllipse(QPointF(center_x, center_y), 12, 12)
        
        # Center star decoration
        painter.setPen(QPen(QColor(CHAMPAGNE_GOLD), 1.0))
        for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
            rad = math.radians(angle)
            x1 = center_x + 8 * math.cos(rad)
            y1 = center_y + 8 * math.sin(rad)
            x2 = center_x + 18 * math.cos(rad)
            y2 = center_y + 18 * math.sin(rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
    
    def _draw_planets(self, painter, center_x, center_y, inner_radius):
        """Draw planets with luxury celestial glow"""
        for planet in self.chart.planets:
            if planet.key == "ascendant":
                continue
            
            # Calculate position
            lon_rad = math.radians(planet.longitude - 90)
            planet_radius = inner_radius * 0.75
            
            # Get planet color
            color_hex = PLANET_COLORS.get(planet.key, CHAMPAGNE_GOLD)
            color = QColor(color_hex)
            
            # Position
            px = center_x + planet_radius * math.cos(lon_rad)
            py = center_y + planet_radius * math.sin(lon_rad)
            
            # Glow effect
            glow_radius = 10 + self.glow_radius * 6
            glow = QRadialGradient(px, py, glow_radius)
            glow.setColorAt(0.0, color.lighter(150))
            glow.setColorAt(0.5, color)
            glow.setColorAt(1.0, QColor(ROYAL_GOLD).darker(150))
            
            # Draw glow
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(px, py), glow_radius, glow_radius)
            
            # Draw planet circle
            painter.setPen(QPen(QColor(IVORY), 1.5))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(px, py), 6, 6)
            
            # Draw planet glyph with luxury font
            glyph = PLANET_GLYPH.get(planet.key, "?")
            painter.setPen(QPen(QColor(OBSIDIAN), 1.0))
            painter.setFont(QFont("Segoe UI Symbol", 10, QFont.Weight.Bold))
            painter.drawText(int(px - 8), int(py + 5), glyph)
            
            # Draw planet name (with luxury style)
            name = PLANET_NAMES.get(planet.key, planet.key.capitalize())
            if self.lang == "hi":
                # Hindi names would go here
                pass
            
            painter.setPen(QPen(QColor(CHAMPAGNE_GOLD), 1.0))
            painter.setFont(QFont("Inter", 8))
            
            # Position name above planet
            text_x = center_x + (planet_radius + 20) * math.cos(lon_rad)
            text_y = center_y + (planet_radius + 20) * math.sin(lon_rad)
            painter.drawText(int(text_x - 12), int(text_y + 3), name[:4])
        
        # Draw Ascendant with special gold styling
        asc = self.chart.ascendant
        if asc:
            lon_rad = math.radians(asc.longitude - 90)
            asc_radius = inner_radius * 0.75
            
            # Position
            px = center_x + asc_radius * math.cos(lon_rad)
            py = center_y + asc_radius * math.sin(lon_rad)
            
            # Ascendant glow (Royal Gold)
            glow_radius = 14 + self.glow_radius * 8
            glow = QRadialGradient(px, py, glow_radius)
            glow.setColorAt(0.0, QColor(ROYAL_GOLD).lighter(120))
            glow.setColorAt(0.5, QColor(ROYAL_GOLD))
            glow.setColorAt(1.0, QColor(ESPRESSO))
            
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(px, py), glow_radius, glow_radius)
            
            # Ascendant diamond with gold
            painter.setPen(QPen(QColor(ROYAL_GOLD), 2.0))
            painter.setBrush(QBrush(QColor(CHAMPAGNE_GOLD)))
            
            # Draw diamond shape
            diamond_size = 10
            
            diamond_path = QPainterPath()
            diamond_path.moveTo(px, py - diamond_size)
            diamond_path.lineTo(px + diamond_size, py)
            diamond_path.lineTo(px, py + diamond_size)
            diamond_path.lineTo(px - diamond_size, py)
            diamond_path.closeSubpath()
            
            painter.drawPath(diamond_path)
            
            # "ASC" label with luxury styling
            painter.setPen(QPen(QColor(ROYAL_GOLD), 1.0))
            painter.setFont(QFont("Cinzel", 8, QFont.Weight.Bold))
            painter.drawText(
                int(px - 12),
                int(py + diamond_size + 16),
                "ASC"
            )
    
    def sizeHint(self):
        return self.minimumSizeHint()
    
    def minimumSizeHint(self):
        return self.minimumSize()