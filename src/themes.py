"""
Theme Management for SkyTrail Desktop
"""

THEMES = {
    "sunset_gold": {
        "name": "Sunset Gold",
        "bg": "#1a0a00",
        "panel_bg": "#2d1500",
        "cyan": "#FFC850",
        "cyan_dim": "#e6a800",
        "amber": "#FFD700",
        "green": "#69f0ae",
        "red": "#ff5252",
        "purple": "#ce93d8",
        "orange": "#ff8a65",
        "text": "#fff8e7",
        "text_secondary": "#f5e6c8",
        "border": "#e6a800",
        "hover": "#3d1f00",
        "glow": "#FFC850",
    },
    "cosmic_purple": {
        "name": "Cosmic Purple",
        "bg": "#0a0015",
        "panel_bg": "#1a0030",
        "cyan": "#7c4dff",
        "cyan_dim": "#536dfe",
        "amber": "#ffd54f",
        "green": "#69f0ae",
        "red": "#ff5252",
        "purple": "#b388ff",
        "orange": "#ffab40",
        "text": "#e8eaf6",
        "text_secondary": "#c5cae9",
        "border": "#536dfe",
        "hover": "#2a004a",
        "glow": "#7c4dff",
    },
    "mystic_blue": {
        "name": "Mystic Blue",
        "bg": "#050810",
        "panel_bg": "#0a1628",
        "cyan": "#46DCFF",
        "cyan_dim": "#1E7890",
        "amber": "#FFC850",
        "green": "#28a745",
        "red": "#dc3545",
        "purple": "#9b59b6",
        "orange": "#e67e22",
        "text": "#ffffff",
        "text_secondary": "#cdeeff",
        "border": "#1E7890",
        "hover": "#0d2137",
        "glow": "#46DCFF",
    },
    "stardust_teal": {
        "name": "Stardust Teal",
        "bg": "#00100a",
        "panel_bg": "#001f14",
        "cyan": "#00e5ff",
        "cyan_dim": "#00897b",
        "amber": "#ffd740",
        "green": "#69f0ae",
        "red": "#ff5252",
        "purple": "#80cbc4",
        "orange": "#ffab40",
        "text": "#e0f7fa",
        "text_secondary": "#b2dfdb",
        "border": "#00897b",
        "hover": "#002f1f",
        "glow": "#00e5ff",
    },
    "royal_indigo": {
        "name": "Royal Indigo",
        "bg": "#0a0015",
        "panel_bg": "#1a0030",
        "cyan": "#9c27b0",
        "cyan_dim": "#6a1b9a",
        "amber": "#ffd54f",
        "green": "#69f0ae",
        "red": "#ff5252",
        "purple": "#ce93d8",
        "orange": "#ffab40",
        "text": "#f3e5f5",
        "text_secondary": "#e1bee7",
        "border": "#6a1b9a",
        "hover": "#2a004a",
        "glow": "#9c27b0",
    },
    "dark": {
        "name": "Dark",
        "bg": "#050810",
        "panel_bg": "#0a1220",
        "cyan": "#46DCFF",
        "cyan_dim": "#1E7890",
        "amber": "#FFC850",
        "green": "#28a745",
        "red": "#dc3545",
        "purple": "#9b59b6",
        "orange": "#e67e22",
        "text": "#ffffff",
        "text_secondary": "#cdeeff",
        "border": "#1E7890",
        "hover": "#1a2a4a",
        "glow": "#46DCFF",
    },
    "light": {
        "name": "Light",
        "bg": "#f0f4f8",
        "panel_bg": "#ffffff",
        "cyan": "#0d47a1",
        "cyan_dim": "#1a73e8",
        "amber": "#f57c00",
        "green": "#2e7d32",
        "red": "#c62828",
        "purple": "#6a1b9a",
        "orange": "#e65100",
        "text": "#1a1a1a",
        "text_secondary": "#333333",
        "border": "#b0bec5",
        "hover": "#e3f2fd",
        "glow": "#1a73e8",
    },
    "paper": {
        "name": "Paper",
        "bg": "#fdf6e3",
        "panel_bg": "#fffaf0",
        "cyan": "#2c3e50",
        "cyan_dim": "#34495e",
        "amber": "#d4a017",
        "green": "#2e7d32",
        "red": "#c62828",
        "purple": "#4a148c",
        "orange": "#e65100",
        "text": "#1a1a1a",
        "text_secondary": "#4a4a4a",
        "border": "#bdc3c7",
        "hover": "#f5f0e8",
        "glow": "#34495e",
    }
}


def apply_theme(window, theme_name="sunset_gold"):
    """Apply a theme to the application"""
    theme = THEMES.get(theme_name, THEMES["sunset_gold"])
    
    window.setStyleSheet(f"""
        QMainWindow, QWidget {{
            background-color: {theme['bg']};
        }}
        QLabel, QGroupBox {{
            color: {theme['text']};
        }}
        QTabWidget::pane {{
            background-color: {theme['panel_bg']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
        }}
        QTabBar::tab {{
            background-color: {theme['panel_bg']};
            color: {theme['cyan']};
            padding: 10px 20px;
            font-family: Consolas, monospace;
            font-size: 12px;
        }}
        QTabBar::tab:selected {{
            background-color: {theme['cyan']};
            color: {theme['bg']};
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
            font-family: Consolas, monospace;
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
        }}
        QPushButton {{
            background-color: {theme['cyan']};
            color: {theme['bg']};
            border-radius: 8px;
            padding: 12px;
            font-family: Consolas, monospace;
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
        }}
        QMenuBar::item:selected {{
            background-color: {theme['hover']};
        }}
        QMenu {{
            background-color: {theme['panel_bg']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
        }}
        QMenu::item:selected {{
            background-color: {theme['hover']};
        }}
        QStatusBar {{
            background-color: {theme['panel_bg']};
            color: {theme['cyan']};
        }}
        QGroupBox {{
            color: {theme['cyan']};
            border: 1px solid {theme['border']};
            border-radius: 8px;
            padding: 10px;
            font-family: Consolas, monospace;
            font-weight: bold;
        }}
        QCheckBox {{
            color: {theme['text']};
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
        }}
        QMessageBox QPushButton {{
            background-color: {theme['cyan']};
            color: {theme['bg']};
            border-radius: 6px;
            padding: 8px 16px;
            font-family: Consolas, monospace;
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
        }}
        QListWidget::item:selected, QTreeWidget::item:selected {{
            background-color: {theme['hover']};
            color: {theme['cyan']};
        }}
    """)


def get_theme_names():
    """Get list of available theme names"""
    return list(THEMES.keys())


def get_theme_colors(theme_name="sunset_gold"):
    """Get colors for a specific theme"""
    return THEMES.get(theme_name, THEMES["sunset_gold"])