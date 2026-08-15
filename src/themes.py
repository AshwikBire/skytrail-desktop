"""
Theme Management for SkyTrail Desktop
Luxury Celestial Theme - Obsidian, Gold & Ivory
"""

THEMES = {
    "luxury_celestial": {
        "name": "Luxury Celestial",
        # Brand Colors
        "bg": "#0B0A08",           # Obsidian - Main Background
        "panel_bg": "#15120D",     # Espresso - Panel Background
        "cyan": "#D4AF37",         # Royal Gold - Primary Accent
        "cyan_dim": "#B8962E",     # Darker Gold
        "amber": "#F4D77B",        # Champagne Gold - Highlights
        "gold": "#D4AF37",         # Royal Gold
        "green": "#D4AF37",        # Gold for success states
        "red": "#8B0000",          # Dark Red for errors
        "purple": "#B8962E",       # Gold variant
        "orange": "#F4D77B",       # Champagne Gold
        "text": "#FFF8E7",         # Ivory - Primary Text
        "text_secondary": "#B8AE9C", # Warm Gray - Secondary Text
        "border": "#D4AF37",       # Royal Gold - Borders
        "hover": "#1D1810",        # Dark Walnut - Hover
        "glow": "#F4D77B",         # Champagne Gold Glow
        "accent": "#D4AF37",       # Royal Gold Accents
        "subtle": "#B8AE9C",       # Warm Gray Subtle
    },
    "obsidian": {
        "name": "Obsidian",
        "bg": "#0B0A08",
        "panel_bg": "#15120D",
        "cyan": "#D4AF37",
        "cyan_dim": "#B8962E",
        "amber": "#F4D77B",
        "gold": "#D4AF37",
        "green": "#D4AF37",
        "red": "#8B0000",
        "purple": "#B8962E",
        "orange": "#F4D77B",
        "text": "#FFF8E7",
        "text_secondary": "#B8AE9C",
        "border": "#D4AF37",
        "hover": "#1D1810",
        "glow": "#F4D77B",
        "accent": "#D4AF37",
        "subtle": "#B8AE9C",
    },
    "royal_gold": {
        "name": "Royal Gold",
        "bg": "#0B0A08",
        "panel_bg": "#15120D",
        "cyan": "#F4D77B",
        "cyan_dim": "#D4AF37",
        "amber": "#F4D77B",
        "gold": "#D4AF37",
        "green": "#F4D77B",
        "red": "#8B0000",
        "purple": "#D4AF37",
        "orange": "#F4D77B",
        "text": "#FFF8E7",
        "text_secondary": "#B8AE9C",
        "border": "#F4D77B",
        "hover": "#1D1810",
        "glow": "#F4D77B",
        "accent": "#F4D77B",
        "subtle": "#B8AE9C",
    },
    "ivory": {
        "name": "Ivory",
        "bg": "#FFF8E7",
        "panel_bg": "#F5EDD6",
        "cyan": "#D4AF37",
        "cyan_dim": "#B8962E",
        "amber": "#D4AF37",
        "gold": "#D4AF37",
        "green": "#D4AF37",
        "red": "#8B0000",
        "purple": "#B8962E",
        "orange": "#D4AF37",
        "text": "#0B0A08",
        "text_secondary": "#B8AE9C",
        "border": "#D4AF37",
        "hover": "#E8DFC8",
        "glow": "#D4AF37",
        "accent": "#D4AF37",
        "subtle": "#B8AE9C",
    },
    "dark_walnut": {
        "name": "Dark Walnut",
        "bg": "#1D1810",
        "panel_bg": "#15120D",
        "cyan": "#F4D77B",
        "cyan_dim": "#D4AF37",
        "amber": "#F4D77B",
        "gold": "#D4AF37",
        "green": "#D4AF37",
        "red": "#8B0000",
        "purple": "#D4AF37",
        "orange": "#F4D77B",
        "text": "#FFF8E7",
        "text_secondary": "#B8AE9C",
        "border": "#D4AF37",
        "hover": "#0B0A08",
        "glow": "#F4D77B",
        "accent": "#D4AF37",
        "subtle": "#B8AE9C",
    },
    "champagne": {
        "name": "Champagne",
        "bg": "#F4D77B",
        "panel_bg": "#FFF8E7",
        "cyan": "#0B0A08",
        "cyan_dim": "#1D1810",
        "amber": "#D4AF37",
        "gold": "#D4AF37",
        "green": "#0B0A08",
        "red": "#8B0000",
        "purple": "#1D1810",
        "orange": "#D4AF37",
        "text": "#0B0A08",
        "text_secondary": "#B8AE9C",
        "border": "#0B0A08",
        "hover": "#E8DFC8",
        "glow": "#D4AF37",
        "accent": "#0B0A08",
        "subtle": "#B8AE9C",
    }
}


def apply_theme(window, theme_name="luxury_celestial"):
    """Apply a theme to the application"""
    theme = THEMES.get(theme_name, THEMES["luxury_celestial"])
    
    window.setStyleSheet(f"""
        QMainWindow, QWidget {{
            background-color: {theme['bg']};
        }}
        QLabel, QGroupBox {{
            color: {theme['text']};
            font-family: 'Inter', sans-serif;
        }}
        QTabWidget::pane {{
            background-color: {theme['panel_bg']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
        }}
        QTabBar::tab {{
            background-color: {theme['panel_bg']};
            color: {theme['text_secondary']};
            padding: 10px 20px;
            font-family: 'Inter', sans-serif;
            font-size: 12px;
        }}
        QTabBar::tab:selected {{
            background-color: {theme['cyan']};
            color: {theme['bg']};
            font-weight: bold;
        }}
        QTabBar::tab:hover {{
            background-color: {theme['hover']};
            color: {theme['text']};
        }}
        QLineEdit, QComboBox, QDateEdit, QSpinBox {{
            background-color: {theme['panel_bg']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 8px;
            font-family: 'Inter', sans-serif;
        }}
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
            border: 2px solid {theme['cyan']};
        }}
        QTextEdit {{
            background-color: {theme['panel_bg']};
            color: {theme['text_secondary']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 10px;
            font-family: 'Inter', sans-serif;
        }}
        QPushButton {{
            background-color: {theme['cyan']};
            color: {theme['bg']};
            border-radius: 8px;
            padding: 12px;
            font-family: 'Inter', sans-serif;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {theme['cyan_dim']};
            color: {theme['text']};
        }}
        QPushButton:checked {{
            background-color: {theme['cyan']};
            color: {theme['bg']};
        }}
        QPushButton:!checked {{
            background-color: {theme['panel_bg']};
            color: {theme['cyan']};
            border: 1px solid {theme['border']};
        }}
        QPushButton:!checked:hover {{
            background-color: {theme['hover']};
        }}
        QMenuBar {{
            background-color: {theme['panel_bg']};
            color: {theme['cyan']};
            font-family: 'Inter', sans-serif;
        }}
        QMenuBar::item:selected {{
            background-color: {theme['hover']};
        }}
        QMenu {{
            background-color: {theme['panel_bg']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            font-family: 'Inter', sans-serif;
        }}
        QMenu::item:selected {{
            background-color: {theme['hover']};
        }}
        QStatusBar {{
            background-color: {theme['panel_bg']};
            color: {theme['cyan']};
            font-family: 'Inter', sans-serif;
        }}
        QGroupBox {{
            color: {theme['cyan']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
            padding: 10px;
            font-family: 'Inter', sans-serif;
            font-weight: bold;
        }}
        QCheckBox {{
            color: {theme['text']};
            font-family: 'Inter', sans-serif;
        }}
        QScrollBar:vertical {{
            background-color: {theme['panel_bg']};
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {theme['cyan_dim']};
            border-radius: 6px;
            min-height: 20px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background-color: {theme['panel_bg']};
            height: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {theme['cyan_dim']};
            border-radius: 6px;
            min-width: 20px;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        QDialog {{
            background-color: {theme['panel_bg']};
        }}
        QMessageBox {{
            background-color: {theme['panel_bg']};
        }}
        QMessageBox QLabel {{
            color: {theme['text']};
            font-family: 'Inter', sans-serif;
        }}
        QMessageBox QPushButton {{
            background-color: {theme['cyan']};
            color: {theme['bg']};
            border-radius: 6px;
            padding: 8px 16px;
            font-family: 'Inter', sans-serif;
            font-weight: bold;
        }}
        QMessageBox QPushButton:hover {{
            background-color: {theme['cyan_dim']};
        }}
        QProgressBar {{
            background-color: {theme['panel_bg']};
            border: 1px solid {theme['border']};
            border-radius: 4px;
            color: {theme['text']};
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {theme['cyan']};
            border-radius: 4px;
        }}
        QListWidget, QTreeWidget {{
            background-color: {theme['panel_bg']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            border-radius: 6px;
            padding: 4px;
            font-family: 'Inter', sans-serif;
        }}
        QListWidget::item:selected, QTreeWidget::item:selected {{
            background-color: {theme['hover']};
            color: {theme['cyan']};
        }}
        QComboBox QAbstractItemView {{
            background-color: {theme['panel_bg']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            selection-background-color: {theme['hover']};
            font-family: 'Inter', sans-serif;
        }}
        QLabel#title_label {{
            font-family: 'Cinzel', serif;
            font-size: 28px;
            font-weight: bold;
            letter-spacing: 4px;
            color: {theme['cyan']};
        }}
        QLabel#tagline_label {{
            font-family: 'Cormorant Garamond', serif;
            font-style: italic;
            font-size: 14px;
            color: {theme['text_secondary']};
        }}
        QLabel#heading_label {{
            font-family: 'Cinzel', serif;
            font-size: 16px;
            color: {theme['gold']};
        }}
    """)


def get_theme_names():
    """Get list of available theme names"""
    return list(THEMES.keys())


def get_theme_colors(theme_name="luxury_celestial"):
    """Get colors for a specific theme"""
    return THEMES.get(theme_name, THEMES["luxury_celestial"])