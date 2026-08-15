"""
SkyTrail Desktop — Advanced Astrology with All Features
Complete integration with PDF Export, Screenshot, Themes, Astrocartography, Notifications & Rectification
"""

import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QFrame,
    QTabWidget, QGroupBox, QGridLayout, QMessageBox, QScrollArea,
    QSplitter, QSpinBox, QDateEdit, QCheckBox, QFileDialog, QDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate
from PyQt6.QtGui import QAction, QFont, QPixmap

from holographic_wheel import ZodiacWheel
from astro_calc import compute_chart, get_prediction, kundali_milan
from horoscope_ai import generate_reading, is_ollama_available
from translations import t, sign_name, planet_name, nakshatra_name, CITY_PRESETS
from api_key_manager import key_manager
from api_settings_dialog import APISettingsDialog
from advanced_yogas import YogaDetector
from panchang import Panchang
from muhurta import Muhurta
from transits import TransitAnalyzer

# New imports for advanced features
from pdf_exporter import PDFExporter
from themes import THEMES, apply_theme
from astrocartography import Astrocartographer
from notifications import NotificationManager
from rectification import BirthTimeRectifier

# Default colors (will be overridden by theme)
DARK_BG = "#1a0a00"
PANEL_BG = "#2d1500"
CYAN = "#FFC850"
CYAN_DIM = "#e6a800"
AMBER = "#FFD700"
GREEN = "#69f0ae"
RED = "#ff5252"
PURPLE = "#ce93d8"
ORANGE = "#ff8a65"


class HoroscopeWorker(QThread):
    result_ready = pyqtSignal(str)
    status_update = pyqtSignal(str)
    
    def __init__(self, chart, name, lang, ai_source="local"):
        super().__init__()
        self.chart = chart
        self.name = name
        self.lang = lang
        self.ai_source = ai_source
    
    def run(self):
        try:
            self.status_update.emit(f"Generating reading using {self.ai_source.upper()} AI...")
            reading = generate_reading(self.chart, self.name, self.lang, mode=self.ai_source)
            self.result_ready.emit(reading)
        except Exception as e:
            if self.lang == "hi":
                self.result_ready.emit(f"त्रुटि: {str(e)}")
            else:
                self.result_ready.emit(f"Error: {str(e)}")


class SkyTrailWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "en"
        self.system = "vedic"
        self.ayanamsa = "Lahiri"
        self.ai_source = "local"
        self.current_chart = None
        self.current_chart2 = None
        self._current_lat = 18.5204
        self._current_lon = 73.8567
        self._current_tz = 5.5
        self.current_theme = "sunset_gold"  # Default theme
        
        self.setWindowTitle("SkyTrail Desktop - Advanced Astrology")
        self.resize(1400, 900)
        
        # Apply default theme first
        apply_theme(self, self.current_theme)
        
        # Setup menu
        self._setup_menu()
        
        # Setup status bar
        self.statusBar().showMessage("Ready")
        
        # Notification manager
        self.notification_manager = NotificationManager()
        
        # Main widget
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)
        
        # Header
        root.addLayout(self._build_header())
        
        # Body with tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: {PANEL_BG};
                border: 1px solid {CYAN_DIM};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: {PANEL_BG};
                color: {CYAN};
                padding: 10px 20px;
                font-family: Consolas, monospace;
                font-size: 12px;
            }}
            QTabBar::tab:selected {{
                background-color: {CYAN};
                color: {DARK_BG};
            }}
            QTabBar::tab:hover {{
                background-color: {CYAN_DIM};
                color: white;
            }}
        """)
        
        # Create all tabs
        self.tabs.addTab(self._build_chart_tab(), "🔮 Chart")
        self.tabs.addTab(self._build_predictions_tab(), "📊 Predictions")
        self.tabs.addTab(self._build_yoga_tab(), "🌟 Yogas")
        self.tabs.addTab(self._build_panchang_tab(), "📅 Panchang")
        self.tabs.addTab(self._build_muhurta_tab(), "🎯 Muhurta")
        self.tabs.addTab(self._build_transit_tab(), "🌊 Transits")
        self.tabs.addTab(self._build_matchmaking_tab(), "💕 Matchmaking")
        self.tabs.addTab(self._build_ai_tab(), "🤖 AI Reading")
        self.tabs.addTab(self._build_astrocartography_tab(), "🌍 Astrocartography")
        
        root.addWidget(self.tabs)
        
        self._refresh_labels()
        
        # Check notifications on startup
        self._check_notifications()
    
    # ---------- Menu ----------
    
    def _setup_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet(f"background-color: {PANEL_BG}; color: {CYAN};")
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        export_pdf_action = QAction("📄 Export PDF Report", self)
        export_pdf_action.triggered.connect(self._export_pdf)
        file_menu.addAction(export_pdf_action)
        
        screenshot_action = QAction("📸 Take Screenshot", self)
        screenshot_action.setShortcut("Ctrl+S")
        screenshot_action.triggered.connect(self._take_screenshot)
        file_menu.addAction(screenshot_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        theme_menu = view_menu.addMenu("🎨 Theme")
        # Add all themes from THEMES
        for theme_key in THEMES.keys():
            display_name = THEMES[theme_key]["name"]
            action = QAction(display_name, self)
            action.triggered.connect(lambda checked, t=theme_key: self._change_theme(t))
            theme_menu.addAction(action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        rectification_action = QAction("🔧 Birth Time Rectification", self)
        rectification_action.triggered.connect(self._open_rectification)
        tools_menu.addAction(rectification_action)
        
        notifications_action = QAction("🔔 Notifications", self)
        notifications_action.triggered.connect(self._open_notifications)
        tools_menu.addAction(notifications_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        api_action = QAction("API Settings", self)
        api_action.triggered.connect(self.open_api_settings)
        settings_menu.addAction(api_action)
        
        ayanamsa_menu = settings_menu.addMenu("Ayanamsa")
        for ayanamsa in ["Lahiri", "Raman", "KP", "True Citra", "Fagan-Bradley"]:
            action = QAction(ayanamsa, self)
            action.triggered.connect(lambda checked, a=ayanamsa: self._set_ayanamsa(a))
            ayanamsa_menu.addAction(action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _show_about(self):
        QMessageBox.about(self, "About SkyTrail", 
            "SkyTrail Desktop v3.0\n\n"
            "Advanced Astrology with:\n"
            "• 50+ Yogas Detection\n"
            "• Full Panchang System\n"
            "• Muhurta (Electional Astrology)\n"
            "• Transit Predictions\n"
            "• Kundali Milan (Matchmaking)\n"
            "• Face, Career, Marriage Analysis\n"
            "• PDF Export\n"
            "• Screenshot Capture\n"
            "• 8 Themes (Sunset Gold, Cosmic Purple, etc.)\n"
            "• Astrocartography\n"
            "• Push Notifications\n"
            "• Birth Time Rectification\n"
            "• AI-Powered Readings\n\n"
            "Built with ❤️")
    
    def _set_ayanamsa(self, ayanamsa: str):
        self.ayanamsa = ayanamsa
        self.statusBar().showMessage(f"Ayanamsa set to: {ayanamsa}")
        if self.current_chart:
            self._on_generate()
    
    # ---------- Header ----------
    
    def _build_header(self):
        row = QHBoxLayout()
        
        # Title
        self.title_label = QLabel("SKYTRAIL")
        self.title_label.setStyleSheet(
            f"color: {CYAN}; font-family: Consolas, monospace; font-size: 24px; "
            "font-weight: bold; letter-spacing: 6px;"
        )
        row.addWidget(self.title_label)
        row.addStretch()
        
        # System toggle
        self.vedic_btn = QPushButton("VEDIC")
        self.western_btn = QPushButton("WESTERN")
        for btn in (self.vedic_btn, self.western_btn):
            btn.setCheckable(True)
            btn.setStyleSheet(self._toggle_style(False))
        self.vedic_btn.setChecked(True)
        self.vedic_btn.setStyleSheet(self._toggle_style(True))
        self.vedic_btn.clicked.connect(lambda: self._set_system("vedic"))
        self.western_btn.clicked.connect(lambda: self._set_system("western"))
        row.addWidget(self.vedic_btn)
        row.addWidget(self.western_btn)
        row.addSpacing(16)
        
        # Language toggle
        self.en_btn = QPushButton("EN")
        self.hi_btn = QPushButton("हिं")
        for btn in (self.en_btn, self.hi_btn):
            btn.setCheckable(True)
            btn.setStyleSheet(self._toggle_style(False))
        self.en_btn.setChecked(True)
        self.en_btn.setStyleSheet(self._toggle_style(True))
        self.en_btn.clicked.connect(lambda: self._set_lang("en"))
        self.hi_btn.clicked.connect(lambda: self._set_lang("hi"))
        row.addWidget(self.en_btn)
        row.addWidget(self.hi_btn)
        row.addSpacing(16)
        
        # AI toggle
        self.local_ai_btn = QPushButton("AI: LOCAL")
        self.nemotron_ai_btn = QPushButton("AI: NEMOTRON")
        for btn in (self.local_ai_btn, self.nemotron_ai_btn):
            btn.setCheckable(True)
            btn.setStyleSheet(self._toggle_style(False))
        self.local_ai_btn.setChecked(True)
        self.local_ai_btn.setStyleSheet(self._toggle_style(True))
        self.local_ai_btn.clicked.connect(lambda: self._set_ai_source("local"))
        self.nemotron_ai_btn.clicked.connect(lambda: self._set_ai_source("nemotron"))
        row.addWidget(self.local_ai_btn)
        row.addWidget(self.nemotron_ai_btn)
        
        # Settings button
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(40, 40)
        settings_btn.setStyleSheet(
            f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; border-radius: 8px; font-size: 18px;"
        )
        settings_btn.clicked.connect(self.open_api_settings)
        row.addWidget(settings_btn)
        
        return row
    
    def _toggle_style(self, active: bool) -> str:
        if active:
            return (f"background-color: {CYAN}; color: {DARK_BG}; border-radius: 6px; "
                     "padding: 8px 16px; font-family: Consolas, monospace; font-weight: bold;")
        return (f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
                "border-radius: 6px; padding: 8px 16px; font-family: Consolas, monospace; font-weight: bold;")
    
    # ---------- Chart Tab ----------
    
    def _build_chart_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Left: Form
        left = QVBoxLayout()
        left.setSpacing(10)
        
        self.form_labels = {}
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter name...")
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("15-06-1998")
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("14:30")
        
        fields = [
            ("name", self.name_input),
            ("birth_date", self.date_input),
            ("birth_time", self.time_input),
        ]
        
        for key, widget in fields:
            lbl = QLabel()
            lbl.setStyleSheet(f"color: {CYAN_DIM}; font-family: Consolas, monospace; font-size: 11px;")
            self.form_labels[key] = lbl
            widget.setStyleSheet(
                f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
                "border-radius: 6px; padding: 8px; font-family: Consolas, monospace;"
            )
            left.addWidget(lbl)
            left.addWidget(widget)
        
        # City presets
        self.city_label = QLabel()
        self.city_label.setStyleSheet(f"color: {CYAN_DIM}; font-family: Consolas, monospace; font-size: 11px;")
        left.addWidget(self.city_label)
        self.city_combo = QComboBox()
        self.city_combo.addItem("—")
        self.city_combo.addItems(list(CITY_PRESETS.keys()))
        self.city_combo.setStyleSheet(
            f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
            "border-radius: 6px; padding: 6px; font-family: Consolas, monospace;"
        )
        self.city_combo.currentTextChanged.connect(self._apply_city_preset)
        left.addWidget(self.city_combo)
        
        self.generate_btn = QPushButton()
        self.generate_btn.setStyleSheet(
            f"background-color: {CYAN}; color: {DARK_BG}; border-radius: 8px; padding: 12px; "
            "font-family: Consolas, monospace; font-weight: bold; font-size: 13px;"
        )
        self.generate_btn.clicked.connect(self._on_generate)
        left.addSpacing(8)
        left.addWidget(self.generate_btn)
        left.addStretch()
        
        # Middle: Wheel
        middle = QVBoxLayout()
        self.wheel = ZodiacWheel()
        middle.addWidget(self.wheel)
        
        # Right: Planet Positions
        right = QVBoxLayout()
        self.positions_box = QTextEdit()
        self.positions_box.setReadOnly(True)
        self.positions_box.setPlaceholderText("Planetary positions will appear here...")
        self.positions_box.setStyleSheet(
            f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
            "border-radius: 6px; padding: 10px; font-family: Consolas, monospace; font-size: 12px;"
        )
        right.addWidget(self.positions_box)
        
        layout.addLayout(left, 2)
        layout.addLayout(middle, 5)
        layout.addLayout(right, 3)
        
        return tab
    
    # ---------- Predictions Tab ----------
    
    def _build_predictions_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setSpacing(15)
        
        self.prediction_cards = {}
        categories = ["Face", "Career", "Marriage", "Children", "Success", "Personality"]
        
        for i, category in enumerate(categories):
            group = QGroupBox(f"🔮 {category}")
            group.setStyleSheet(f"""
                QGroupBox {{
                    color: {CYAN};
                    border: 1px solid {CYAN_DIM};
                    border-radius: 8px;
                    padding: 10px;
                    font-family: Consolas, monospace;
                    font-weight: bold;
                }}
            """)
            
            card = QVBoxLayout()
            card.setSpacing(8)
            
            content = QTextEdit()
            content.setReadOnly(True)
            content.setStyleSheet(
                f"background-color: {PANEL_BG}; color: {CYAN}; border: none; "
                "font-family: Segoe UI, sans-serif; font-size: 13px;"
            )
            content.setMaximumHeight(150)
            content.setPlaceholderText(f"{category} prediction will appear here...")
            
            card.addWidget(content)
            group.setLayout(card)
            
            layout.addWidget(group, i // 3, i % 3)
            self.prediction_cards[category.lower()] = content
        
        self.pred_btn = QPushButton("📊 Generate All Predictions")
        self.pred_btn.setStyleSheet(
            f"background-color: {CYAN}; color: {DARK_BG}; border-radius: 8px; padding: 12px; "
            "font-family: Consolas, monospace; font-weight: bold; font-size: 14px;"
        )
        self.pred_btn.clicked.connect(self._generate_predictions)
        layout.addWidget(self.pred_btn, 2, 1)
        
        return tab
    
    # ---------- Yoga Tab ----------
    
    def _build_yoga_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info_label = QLabel("🌟 50+ Vedic Yogas Detection")
        info_label.setStyleSheet(f"color: {AMBER}; font-family: Consolas, monospace; font-size: 16px; font-weight: bold;")
        layout.addWidget(info_label)
        
        self.yoga_box = QTextEdit()
        self.yoga_box.setReadOnly(True)
        self.yoga_box.setPlaceholderText("Click 'Detect Yogas' to analyze your chart...")
        self.yoga_box.setStyleSheet(
            f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
            "border-radius: 8px; padding: 16px; font-family: Segoe UI, sans-serif; font-size: 13px;"
        )
        layout.addWidget(self.yoga_box)
        
        btn_layout = QHBoxLayout()
        
        self.yoga_btn = QPushButton("🌟 Detect Yogas")
        self.yoga_btn.setStyleSheet(
            f"background-color: {PURPLE}; color: {DARK_BG}; border-radius: 8px; padding: 12px; "
            "font-family: Consolas, monospace; font-weight: bold; font-size: 13px;"
        )
        self.yoga_btn.clicked.connect(self._detect_yogas)
        btn_layout.addWidget(self.yoga_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        return tab
    
    # ---------- Panchang Tab ----------
    
    def _build_panchang_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        
        self.panchang_date = QDateEdit()
        self.panchang_date.setDate(QDate.currentDate())
        self.panchang_date.setCalendarPopup(True)
        self.panchang_date.setStyleSheet(
            f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
            "border-radius: 6px; padding: 6px; font-family: Consolas, monospace;"
        )
        date_layout.addWidget(self.panchang_date)
        
        self.get_panchang_btn = QPushButton("📅 Get Panchang")
        self.get_panchang_btn.setStyleSheet(
            f"background-color: {CYAN}; color: {DARK_BG}; border-radius: 6px; padding: 8px 16px; "
            "font-family: Consolas, monospace; font-weight: bold;"
        )
        self.get_panchang_btn.clicked.connect(self._get_panchang)
        date_layout.addWidget(self.get_panchang_btn)
        date_layout.addStretch()
        
        layout.addLayout(date_layout)
        
        self.panchang_box = QTextEdit()
        self.panchang_box.setReadOnly(True)
        self.panchang_box.setPlaceholderText("Panchang details will appear here...")
        self.panchang_box.setStyleSheet(
            f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
            "border-radius: 8px; padding: 16px; font-family: Segoe UI, sans-serif; font-size: 13px;"
        )
        layout.addWidget(self.panchang_box)
        
        return tab
    
    # ---------- Muhurta Tab ----------
    
    def _build_muhurta_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        event_layout = QHBoxLayout()
        event_layout.addWidget(QLabel("Event Type:"))
        
        self.event_combo = QComboBox()
        self.event_combo.addItems(["Wedding 💍", "Business 🏢", "Travel ✈️"])
        self.event_combo.setStyleSheet(
            f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
            "border-radius: 6px; padding: 6px; font-family: Consolas, monospace;"
        )
        event_layout.addWidget(self.event_combo)
        
        self.muhurta_btn = QPushButton("🎯 Find Muhurta")
        self.muhurta_btn.setStyleSheet(
            f"background-color: {ORANGE}; color: {DARK_BG}; border-radius: 6px; padding: 8px 16px; "
            "font-family: Consolas, monospace; font-weight: bold;"
        )
        self.muhurta_btn.clicked.connect(self._find_muhurta)
        event_layout.addWidget(self.muhurta_btn)
        event_layout.addStretch()
        
        layout.addLayout(event_layout)
        
        self.muhurta_box = QTextEdit()
        self.muhurta_box.setReadOnly(True)
        self.muhurta_box.setPlaceholderText("Muhurta results will appear here...")
        self.muhurta_box.setStyleSheet(
            f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
            "border-radius: 8px; padding: 16px; font-family: Segoe UI, sans-serif; font-size: 13px;"
        )
        layout.addWidget(self.muhurta_box)
        
        return tab
    
    # ---------- Transit Tab ----------
    
    def _build_transit_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        transit_layout = QHBoxLayout()
        
        self.transit_btn = QPushButton("🌊 Analyze Current Transits")
        self.transit_btn.setStyleSheet(
            f"background-color: {GREEN}; color: {DARK_BG}; border-radius: 6px; padding: 8px 16px; "
            "font-family: Consolas, monospace; font-weight: bold;"
        )
        self.transit_btn.clicked.connect(self._analyze_transits)
        transit_layout.addWidget(self.transit_btn)
        
        self.forecast_btn = QPushButton("📈 Yearly Forecast")
        self.forecast_btn.setStyleSheet(
            f"background-color: {AMBER}; color: {DARK_BG}; border-radius: 6px; padding: 8px 16px; "
            "font-family: Consolas, monospace; font-weight: bold;"
        )
        self.forecast_btn.clicked.connect(self._get_forecast)
        transit_layout.addWidget(self.forecast_btn)
        
        transit_layout.addStretch()
        layout.addLayout(transit_layout)
        
        self.transit_box = QTextEdit()
        self.transit_box.setReadOnly(True)
        self.transit_box.setPlaceholderText("Transit analysis will appear here...")
        self.transit_box.setStyleSheet(
            f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
            "border-radius: 8px; padding: 16px; font-family: Segoe UI, sans-serif; font-size: 13px;"
        )
        layout.addWidget(self.transit_box)
        
        return tab
    
    # ---------- Matchmaking Tab ----------
    
    def _build_matchmaking_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Person 1
        group1 = QGroupBox("👤 Person 1")
        group1.setStyleSheet(f"color: {CYAN}; border: 1px solid {CYAN_DIM}; border-radius: 8px; padding: 10px;")
        layout1 = QHBoxLayout()
        
        self.name1_input = QLineEdit()
        self.name1_input.setPlaceholderText("Name")
        self.name1_input.setStyleSheet(f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; border-radius: 6px; padding: 8px;")
        layout1.addWidget(self.name1_input)
        
        self.date1_input = QLineEdit()
        self.date1_input.setPlaceholderText("DD-MM-YYYY")
        self.date1_input.setStyleSheet(f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; border-radius: 6px; padding: 8px;")
        layout1.addWidget(self.date1_input)
        
        self.time1_input = QLineEdit()
        self.time1_input.setPlaceholderText("HH:MM")
        self.time1_input.setStyleSheet(f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; border-radius: 6px; padding: 8px;")
        layout1.addWidget(self.time1_input)
        
        group1.setLayout(layout1)
        layout.addWidget(group1)
        
        # Person 2
        group2 = QGroupBox("👤 Person 2")
        group2.setStyleSheet(f"color: {CYAN}; border: 1px solid {CYAN_DIM}; border-radius: 8px; padding: 10px;")
        layout2 = QHBoxLayout()
        
        self.name2_input = QLineEdit()
        self.name2_input.setPlaceholderText("Name")
        self.name2_input.setStyleSheet(f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; border-radius: 6px; padding: 8px;")
        layout2.addWidget(self.name2_input)
        
        self.date2_input = QLineEdit()
        self.date2_input.setPlaceholderText("DD-MM-YYYY")
        self.date2_input.setStyleSheet(f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; border-radius: 6px; padding: 8px;")
        layout2.addWidget(self.date2_input)
        
        self.time2_input = QLineEdit()
        self.time2_input.setPlaceholderText("HH:MM")
        self.time2_input.setStyleSheet(f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; border-radius: 6px; padding: 8px;")
        layout2.addWidget(self.time2_input)
        
        group2.setLayout(layout2)
        layout.addWidget(group2)
        
        self.match_btn = QPushButton("💕 Kundali Milan (Matchmaking)")
        self.match_btn.setStyleSheet(
            f"background-color: {PURPLE}; color: {DARK_BG}; border-radius: 8px; padding: 12px; "
            "font-family: Consolas, monospace; font-weight: bold; font-size: 14px;"
        )
        self.match_btn.clicked.connect(self._do_matchmaking)
        layout.addWidget(self.match_btn)
        
        self.match_box = QTextEdit()
        self.match_box.setReadOnly(True)
        self.match_box.setPlaceholderText("Matchmaking results will appear here...")
        self.match_box.setStyleSheet(
            f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
            "border-radius: 8px; padding: 16px; font-family: Segoe UI, sans-serif; font-size: 13px;"
        )
        layout.addWidget(self.match_box)
        
        return tab
    
    # ---------- AI Tab ----------
    
    def _build_ai_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.reading_box = QTextEdit()
        self.reading_box.setReadOnly(True)
        self.reading_box.setPlaceholderText("AI reading will appear here...")
        self.reading_box.setStyleSheet(
            f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
            "border-radius: 8px; padding: 16px; font-family: Segoe UI, sans-serif; font-size: 14px;"
        )
        layout.addWidget(self.reading_box)
        
        self.reading_btn = QPushButton("🤖 Generate AI Reading")
        self.reading_btn.setStyleSheet(
            f"background-color: {AMBER}; color: {DARK_BG}; border-radius: 8px; padding: 12px; "
            "font-family: Consolas, monospace; font-weight: bold; font-size: 13px;"
        )
        self.reading_btn.clicked.connect(self._generate_ai_reading)
        layout.addWidget(self.reading_btn)
        
        return tab
    
    # ---------- Astrocartography Tab ----------
    
    def _build_astrocartography_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info_label = QLabel("🌍 Astrocartography - Find Your Favorable Locations")
        info_label.setStyleSheet(f"color: {AMBER}; font-family: Consolas, monospace; font-size: 16px; font-weight: bold;")
        layout.addWidget(info_label)
        
        # Category selector
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Category:"))
        
        self.astro_category = QComboBox()
        self.astro_category.addItems(["Career", "Marriage", "Success", "Wealth", "Education", "Spiritual"])
        self.astro_category.setStyleSheet(
            f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
            "border-radius: 6px; padding: 6px; font-family: Consolas, monospace;"
        )
        cat_layout.addWidget(self.astro_category)
        
        self.astro_btn = QPushButton("🔍 Find Locations")
        self.astro_btn.setStyleSheet(
            f"background-color: {GREEN}; color: {DARK_BG}; border-radius: 6px; padding: 8px 16px; "
            "font-family: Consolas, monospace; font-weight: bold;"
        )
        self.astro_btn.clicked.connect(self._show_astrocartography)
        cat_layout.addWidget(self.astro_btn)
        cat_layout.addStretch()
        
        layout.addLayout(cat_layout)
        
        self.astro_box = QTextEdit()
        self.astro_box.setReadOnly(True)
        self.astro_box.setPlaceholderText("Astrocartography results will appear here...")
        self.astro_box.setStyleSheet(
            f"background-color: {PANEL_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
            "border-radius: 8px; padding: 16px; font-family: Segoe UI, sans-serif; font-size: 13px;"
        )
        layout.addWidget(self.astro_box)
        
        return tab
    
    # ---------- Core Functions ----------
    
    def _apply_city_preset(self, city: str):
        if city in CITY_PRESETS:
            lat, lon, tz = CITY_PRESETS[city]
            self._current_lat = lat
            self._current_lon = lon
            self._current_tz = tz
            self.statusBar().showMessage(f"📍 Selected: {city}")
    
    def _set_system(self, system: str):
        self.system = system
        self.vedic_btn.setChecked(system == "vedic")
        self.western_btn.setChecked(system == "western")
        self.vedic_btn.setStyleSheet(self._toggle_style(system == "vedic"))
        self.western_btn.setStyleSheet(self._toggle_style(system == "western"))
        if self.current_chart:
            self._on_generate()
    
    def _set_lang(self, lang: str):
        self.lang = lang
        self.en_btn.setChecked(lang == "en")
        self.hi_btn.setChecked(lang == "hi")
        self.en_btn.setStyleSheet(self._toggle_style(lang == "en"))
        self.hi_btn.setStyleSheet(self._toggle_style(lang == "hi"))
        self._refresh_labels()
        if self.current_chart:
            self.wheel.set_chart(self.current_chart, self.lang)
            self._render_positions()
    
    def _set_ai_source(self, source: str):
        self.ai_source = source
        self.local_ai_btn.setChecked(source == "local")
        self.nemotron_ai_btn.setChecked(source == "nemotron")
        self.local_ai_btn.setStyleSheet(self._toggle_style(source == "local"))
        self.nemotron_ai_btn.setStyleSheet(self._toggle_style(source == "nemotron"))
    
    def _refresh_labels(self):
        self.title_label.setText("SKYTRAIL" if self.lang == "en" else "स्काईट्रेल")
        self.vedic_btn.setText("VEDIC" if self.lang == "en" else "वैदिक")
        self.western_btn.setText("WESTERN" if self.lang == "en" else "पाश्चात्य")
        self.generate_btn.setText("GENERATE CHART" if self.lang == "en" else "चार्ट बनाएं")
        self.city_label.setText("Quick City" if self.lang == "en" else "त्वरित शहर")
        self.reading_btn.setText("🤖 Generate AI Reading" if self.lang == "en" else "🤖 AI रीडिंग बनाएं")
        self.pred_btn.setText("📊 Generate All Predictions" if self.lang == "en" else "📊 सभी भविष्यवाणियां बनाएं")
        self.yoga_btn.setText("🌟 Detect Yogas" if self.lang == "en" else "🌟 योग खोजें")
        self.get_panchang_btn.setText("📅 Get Panchang" if self.lang == "en" else "📅 पंचांग देखें")
        self.muhurta_btn.setText("🎯 Find Muhurta" if self.lang == "en" else "🎯 मुहूर्त खोजें")
        self.transit_btn.setText("🌊 Analyze Current Transits" if self.lang == "en" else "🌊 वर्तमान गोचर विश्लेषण करें")
        self.forecast_btn.setText("📈 Yearly Forecast" if self.lang == "en" else "📈 वार्षिक भविष्यवाणी")
        self.match_btn.setText("💕 Kundali Milan (Matchmaking)" if self.lang == "en" else "💕 कुंडली मिलान")
        self.astro_btn.setText("🔍 Find Locations" if self.lang == "en" else "🔍 स्थान खोजें")
        
        labels = {
            "name": ("Name", "नाम"),
            "birth_date": ("Birth Date (DD-MM-YYYY)", "जन्म तिथि (DD-MM-YYYY)"),
            "birth_time": ("Birth Time (24hr HH:MM)", "जन्म समय (24hr HH:MM)"),
        }
        
        for key, (en, hi) in labels.items():
            if key in self.form_labels:
                self.form_labels[key].setText(hi if self.lang == "hi" else en)
    
    # ---------- Chart Generation ----------
    
    def _on_generate(self):
        try:
            name = self.name_input.text().strip() or "—"
            date_str = self.date_input.text().strip()
            time_str = self.time_input.text().strip()
            
            if not date_str or not time_str:
                self.positions_box.setPlainText("Please enter birth date and time!")
                return
            
            lat = self._current_lat
            lon = self._current_lon
            tz = self._current_tz
            
            day, month, year = [int(x) for x in date_str.split("-")]
            hour, minute = [int(x) for x in time_str.split(":")]
            dt_local = datetime(year, month, day, hour, minute)
        except Exception as e:
            self.positions_box.setPlainText(f"Error: {e}\n\nPlease check date (DD-MM-YYYY) and time (HH:MM)")
            return
        
        try:
            chart = compute_chart(dt_local, tz, lat, lon, system=self.system, ayanamsa=self.ayanamsa)
            self.current_chart = chart
            self.wheel.set_chart(chart, self.lang)
            self._render_positions()
            self.statusBar().showMessage(f"✅ Chart generated successfully! (Ayanamsa: {self.ayanamsa})")
            
            # Check notifications
            self._check_notifications()
            
        except Exception as e:
            self.positions_box.setPlainText(f"Error computing chart: {e}")
            self.statusBar().showMessage("❌ Chart generation failed!")
    
    def _render_positions(self):
        chart = self.current_chart
        if not chart:
            return
        
        lines = []
        lines.append(f"⭐ {planet_name('ascendant', self.lang).upper()}: {sign_name(chart.ascendant.sign_index, self.lang)} {chart.ascendant.degree_in_sign:.1f}°")
        
        for p in chart.planets:
            retro = " ℞" if p.retrograde else ""
            lines.append(f"{planet_name(p.key, self.lang)}: {sign_name(p.sign_index, self.lang)} {p.degree_in_sign:.1f}°{retro} (H{p.house})")
        
        if chart.system == "vedic":
            lines.append(f"\n🌙 {nakshatra_name(chart.nakshatra_index, self.lang)} (Pada {chart.nakshatra_pada})")
            lines.append(f"📌 Ayanamsa: {chart.ayanamsa}")
        
        if chart.yogas:
            lines.append("\n🌟 Yogas Detected:")
            for yoga in chart.yogas[:3]:
                lines.append(f"  • {yoga['name']}")
        
        self.positions_box.setPlainText("\n".join(lines))
    
    # ---------- Predictions ----------
    
    def _generate_predictions(self):
        if not self.current_chart:
            self.statusBar().showMessage("⚠️ Please generate a chart first!")
            QMessageBox.warning(self, "No Chart", "Please generate a chart first!")
            return
        
        chart = self.current_chart
        categories = {
            "face": "Face",
            "career": "Career",
            "marriage": "Marriage",
            "children": "Children",
            "success": "Success",
            "personality": "Personality"
        }
        
        for key, label in categories.items():
            pred = get_prediction(chart, key)
            
            if pred:
                text = f"""
<b>{label}</b>
━━━━━━━━━━━━━━━━━━━━━
"""
                for k, v in pred.items():
                    if k not in ["category"]:
                        key_display = k.replace('_', ' ').capitalize()
                        text += f"<b>{key_display}:</b> {v}\n"
                
                self.prediction_cards[key].setHtml(text)
        
        self.statusBar().showMessage("✅ Predictions generated!")
    
    # ---------- Yogas ----------
    
    def _detect_yogas(self):
        if not self.current_chart:
            self.statusBar().showMessage("⚠️ Please generate a chart first!")
            QMessageBox.warning(self, "No Chart", "Please generate a chart first!")
            return
        
        detector = YogaDetector(self.current_chart)
        yogas = detector.detect_all_yogas()
        
        if not yogas:
            self.yoga_box.setPlainText("No significant yogas detected in this chart.")
            return
        
        text = "🌟 ADVANCED YOGAS DETECTED 🌟\n"
        text += "═" * 50 + "\n\n"
        
        benefic = [y for y in yogas if y.type == "Benefic"]
        neutral = [y for y in yogas if y.type == "Neutral"]
        malefic = [y for y in yogas if y.type == "Malefic"]
        
        for group, label in [(benefic, "✨ Benefic Yogas"), (neutral, "⚖️ Neutral Yogas"), (malefic, "⚠️ Malefic Yogas")]:
            if group:
                text += f"\n{label}:\n"
                text += "─" * 40 + "\n"
                for yoga in group:
                    text += f"\n🔮 {yoga.name}\n"
                    text += f"   Type: {yoga.type}\n"
                    text += f"   Strength: {yoga.strength}\n"
                    text += f"   {yoga.description}\n"
                    if yoga.planets:
                        text += f"   Planets: {', '.join(yoga.planets)}\n"
                    if yoga.houses:
                        text += f"   Houses: {', '.join(str(h) for h in yoga.houses)}\n"
        
        self.yoga_box.setPlainText(text)
        self.statusBar().showMessage(f"✅ {len(yogas)} yogas detected!")
    
    # ---------- Panchang ----------
    
    def _get_panchang(self):
        date = self.panchang_date.date().toPyDate()
        panchang = Panchang(date, self._current_lat, self._current_lon, self._current_tz)
        data = panchang.get_panchang_dict()
        
        text = "📅 PANCHANG\n"
        text += "═" * 50 + "\n\n"
        
        text += f"📆 Date: {data['date']}\n\n"
        
        text += "🌙 TITHI\n"
        text += f"   Name: {data['tithi']['name']}\n"
        text += f"   Number: {data['tithi']['number']}\n"
        text += f"   Ends at: {data['tithi']['end_time']}\n\n"
        
        text += "📅 VARA (Weekday)\n"
        text += f"   Name: {data['vara']['name']}\n"
        text += f"   Lord: {data['vara']['lord']}\n\n"
        
        text += "⭐ NAKSHATRA\n"
        text += f"   Name: {data['nakshatra']['name']}\n"
        text += f"   Lord: {data['nakshatra']['lord']}\n"
        text += f"   Number: {data['nakshatra']['number']}\n\n"
        
        text += "🕉️ YOGA\n"
        text += f"   Name: {data['yoga']['name']}\n"
        text += f"   Number: {data['yoga']['number']}\n\n"
        
        text += "⚡ KARANA\n"
        text += f"   Name: {data['karana']['name']}\n"
        text += f"   Number: {data['karana']['number']}\n\n"
        
        text += "☀️ SUN\n"
        text += f"   Rise: {data['sun']['rise']}\n"
        text += f"   Set: {data['sun']['set']}\n\n"
        
        text += "🚫 INAUSPICIOUS PERIODS\n"
        text += f"   Rahu Kaal: {data['inauspicious_periods']['rahu_kaal']['start']} - {data['inauspicious_periods']['rahu_kaal']['end']}\n"
        text += f"   Gulika Kaal: {data['inauspicious_periods']['gulika_kaal']['start']} - {data['inauspicious_periods']['gulika_kaal']['end']}\n"
        text += f"   Yamaganda: {data['inauspicious_periods']['yamaganda']['start']} - {data['inauspicious_periods']['yamaganda']['end']}\n\n"
        
        if data['auspicious_periods']:
            text += "✨ AUSPICIOUS PERIODS\n"
            for p in data['auspicious_periods']:
                text += f"   {p['name']}: {p['start']} - {p['end']}\n"
                text += f"   {p['description']}\n\n"
        
        self.panchang_box.setPlainText(text)
        self.statusBar().showMessage("✅ Panchang generated!")
    
    # ---------- Muhurta ----------
    
    def _find_muhurta(self):
        date = datetime.now()
        muhurta = Muhurta(date, self._current_lat, self._current_lon, self._current_tz)
        
        event_map = {
            "Wedding 💍": "wedding",
            "Business 🏢": "business",
            "Travel ✈️": "travel"
        }
        event_type = event_map.get(self.event_combo.currentText(), "wedding")
        
        if event_type == "wedding":
            result = muhurta.check_wedding_muhurta()
        elif event_type == "business":
            result = muhurta.check_business_muhurta()
        else:
            result = muhurta.check_travel_muhurta()
        
        text = f"🎯 MUHURTA ANALYSIS\n"
        text += "═" * 50 + "\n\n"
        
        text += f"📅 Date: {result['date']}\n"
        text += f"📊 Score: {result['score']}/{result['max_score']}\n"
        text += f"💫 Verdict: {result['verdict']}\n\n"
        
        text += "📋 DETAILS\n"
        text += "─" * 40 + "\n"
        for detail in result['details']:
            text += f"   {detail}\n"
        
        text += f"\n💡 Recommendation: {result.get('recommendation', '')}\n"
        
        text += "\n\n🔮 BEST DATES IN NEXT 30 DAYS\n"
        text += "─" * 40 + "\n"
        
        best_dates = muhurta.get_best_muhurta(event_type, 30)
        if best_dates:
            for d in best_dates[:5]:
                text += f"   📅 {d['date']} - Score: {d['score']} - {d['verdict']}\n"
        else:
            text += "   No highly auspicious dates found in next 30 days.\n"
        
        self.muhurta_box.setPlainText(text)
        self.statusBar().showMessage("✅ Muhurta analysis complete!")
    
    # ---------- Transits ----------
    
    def _analyze_transits(self):
        if not self.current_chart:
            self.statusBar().showMessage("⚠️ Please generate a chart first!")
            QMessageBox.warning(self, "No Chart", "Please generate a chart first!")
            return
        
        analyzer = TransitAnalyzer(self.current_chart, self._current_lat, self._current_lon, self._current_tz)
        
        text = "🌊 CURRENT TRANSIT ANALYSIS\n"
        text += "═" * 50 + "\n\n"
        
        effects = analyzer.get_transit_effects()
        text += "📊 TRANSIT EFFECTS BY PLANET\n"
        text += "─" * 40 + "\n"
        
        for planet, data in effects.items():
            text += f"\n🔮 {planet.capitalize()}\n"
            text += f"   Natal: {data['natal_position']}\n"
            text += f"   Transit: {data['transit_position']}\n"
            if data['aspects']:
                text += f"   Aspects: {', '.join(data['aspects'])}\n"
            text += f"   Effect: {data['effect']}\n"
            text += f"   Significance: {data['significance']}\n"
        
        text += "\n\n🏠 HOUSE PREDICTIONS\n"
        text += "─" * 40 + "\n"
        
        predictions = analyzer.get_current_transit_predictions()
        for house, data in predictions.items():
            text += f"\n🏠 House {house}\n"
            text += f"   Planets: {', '.join(data['planets'])}\n"
            text += f"   {data['house_meaning']}\n"
            text += f"   Prediction: {data['prediction']}\n"
        
        self.transit_box.setPlainText(text)
        self.statusBar().showMessage("✅ Transit analysis complete!")
    
    def _get_forecast(self):
        if not self.current_chart:
            self.statusBar().showMessage("⚠️ Please generate a chart first!")
            QMessageBox.warning(self, "No Chart", "Please generate a chart first!")
            return
        
        analyzer = TransitAnalyzer(self.current_chart, self._current_lat, self._current_lon, self._current_tz)
        forecast = analyzer.get_yearly_forecast()
        
        text = "📈 YEARLY FORECAST\n"
        text += "═" * 50 + "\n\n"
        
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        for month, prediction in forecast.items():
            text += f"📅 {month_names[month-1]}\n"
            text += f"   {prediction}\n\n"
        
        self.transit_box.setPlainText(text)
        self.statusBar().showMessage("✅ Yearly forecast generated!")
    
    # ---------- Matchmaking ----------
    
    def _do_matchmaking(self):
        try:
            name1 = self.name1_input.text().strip() or "Person 1"
            date1 = self.date1_input.text().strip()
            time1 = self.time1_input.text().strip()
            
            name2 = self.name2_input.text().strip() or "Person 2"
            date2 = self.date2_input.text().strip()
            time2 = self.time2_input.text().strip()
            
            if not date1 or not time1 or not date2 or not time2:
                self.match_box.setPlainText("Please enter both persons' birth details!")
                return
            
            d1_day, d1_month, d1_year = [int(x) for x in date1.split("-")]
            d1_hour, d1_minute = [int(x) for x in time1.split(":")]
            dt1 = datetime(d1_year, d1_month, d1_day, d1_hour, d1_minute)
            
            d2_day, d2_month, d2_year = [int(x) for x in date2.split("-")]
            d2_hour, d2_minute = [int(x) for x in time2.split(":")]
            dt2 = datetime(d2_year, d2_month, d2_day, d2_hour, d2_minute)
            
            chart1 = compute_chart(dt1, self._current_tz, self._current_lat, self._current_lon, 
                                  system=self.system, ayanamsa=self.ayanamsa)
            chart2 = compute_chart(dt2, self._current_tz, self._current_lat, self._current_lon,
                                  system=self.system, ayanamsa=self.ayanamsa)
            
            result = kundali_milan(chart1, chart2)
            
            text = f"💕 KUNDALI MILAN RESULTS\n"
            text += "═" * 50 + "\n\n"
            
            text += f"👤 {name1}\n"
            text += f"   Date: {date1} {time1}\n\n"
            text += f"👤 {name2}\n"
            text += f"   Date: {date2} {time2}\n\n"
            
            text += "📊 SCORE\n"
            text += "─" * 40 + "\n"
            text += f"   Score: {result['score']}/{result['total']}\n"
            text += f"   Percentage: {result['percentage']:.1f}%\n"
            text += f"   Level: {result['level']}\n"
            text += f"   Compatible: {'✅ Yes' if result['compatible'] else '❌ No'}\n\n"
            
            text += "📋 DETAILED BREAKDOWN\n"
            text += "─" * 40 + "\n"
            for detail in result['details']:
                for key, value in detail.items():
                    text += f"   {key}: {value}\n"
            
            text += "\n💡 RECOMMENDATION\n"
            text += "─" * 40 + "\n"
            if result['compatible']:
                text += "   ✅ This is a good match. Both charts show compatibility.\n"
                text += "   Proceed with confidence.\n"
            else:
                text += "   ⚠️ This match needs careful consideration.\n"
                text += "   Consult an expert for detailed analysis.\n"
            
            self.match_box.setPlainText(text)
            self.statusBar().showMessage(f"✅ Matchmaking complete! Score: {result['score']}/{result['total']}")
            
        except Exception as e:
            self.match_box.setPlainText(f"Error: {e}\n\nPlease check the date/time format (DD-MM-YYYY, HH:MM)")
            self.statusBar().showMessage("❌ Matchmaking failed!")
    
    # ---------- AI Reading ----------
    
    def _generate_ai_reading(self):
        if not self.current_chart:
            self.statusBar().showMessage("⚠️ Please generate a chart first!")
            QMessageBox.warning(self, "No Chart", "Please generate a chart first!")
            return
        
        name = self.name_input.text().strip() or "—"
        self.reading_box.setPlainText("🤔 Generating AI reading... Please wait...")
        self.statusBar().showMessage("📖 Generating AI reading...")
        
        self.worker = HoroscopeWorker(self.current_chart, name, self.lang, self.ai_source)
        self.worker.result_ready.connect(self._on_ai_reading_done)
        self.worker.status_update.connect(self.statusBar().showMessage)
        self.worker.start()
    
    def _on_ai_reading_done(self, reading):
        self.reading_box.setPlainText(reading)
        self.statusBar().showMessage("✅ AI reading generated!")
    
    # ---------- Astrocartography ----------
    
    def _show_astrocartography(self):
        if not self.current_chart:
            self.statusBar().showMessage("⚠️ Please generate a chart first!")
            QMessageBox.warning(self, "No Chart", "Please generate a chart first!")
            return
        
        category = self.astro_category.currentText().lower()
        astro = Astrocartographer(self.current_chart)
        locations = astro.recommend_cities(category)
        
        text = f"🌍 RECOMMENDED CITIES FOR {category.upper()}\n"
        text += "═" * 50 + "\n\n"
        
        if locations:
            for loc in locations[:10]:
                text += f"📍 {loc['city']}\n"
                text += f"   Direction: {loc['direction']}\n"
                text += f"   Planet: {loc['planet'].capitalize()}\n"
                text += f"   Strength: {loc['strength']}\n"
                text += f"   Coordinates: {loc['coordinates']}\n\n"
        else:
            text += "No recommendations found. Try another category.\n"
        
        self.astro_box.setPlainText(text)
        self.statusBar().showMessage("✅ Astrocartography results generated!")
    
    # ---------- PDF Export ----------
    
    def _export_pdf(self):
        if not self.current_chart:
            QMessageBox.warning(self, "No Chart", "Please generate a chart first!")
            return
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save PDF Report", 
                f"skytrail_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", 
                "PDF (*.pdf)"
            )
            
            if not file_path:
                return
            
            # Prepare predictions
            predictions = {}
            for category in ["face", "career", "marriage", "children", "success", "personality"]:
                predictions[category] = get_prediction(self.current_chart, category)
            
            # Get yogas
            detector = YogaDetector(self.current_chart)
            yogas = detector.detect_all_yogas()
            
            # Generate PDF
            exporter = PDFExporter(
                chart=self.current_chart,
                predictions=predictions,
                yogas=yogas[:15],
                panchang={},
                muhurta={}
            )
            
            exporter.generate_report(file_path)
            self.statusBar().showMessage(f"✅ PDF saved: {file_path}")
            QMessageBox.information(self, "PDF Saved", f"Report saved to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF: {str(e)}")
    
    # ---------- Screenshot ----------
    
    def _take_screenshot(self):
        """Take screenshot of the application"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Screenshot",
                f"skytrail_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                "PNG Image (*.png);;JPEG Image (*.jpg)"
            )
            
            if not file_path:
                return
            
            screen = self.grab()
            screen.save(file_path, "PNG")
            
            self.statusBar().showMessage(f"✅ Screenshot saved: {file_path}")
            QMessageBox.information(self, "Screenshot Saved", 
                f"Screenshot saved successfully!\n\n{file_path}")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save screenshot: {str(e)}")
    
    # ---------- Theme ----------
    
    def _change_theme(self, theme_name):
        """Change application theme"""
        self.current_theme = theme_name
        apply_theme(self, theme_name)
        
        # Get theme display name
        display_name = THEMES.get(theme_name, {}).get("name", theme_name.capitalize())
        self.statusBar().showMessage(f"Theme changed to: {display_name}")
    
    # ---------- Notifications ----------
    
    def _check_notifications(self):
        """Check for notifications"""
        if self.current_chart:
            count = self.notification_manager.get_notification_count(self.current_chart)
            if count > 0:
                self.statusBar().showMessage(f"🔔 You have {count} notification(s)!")
    
    def _open_notifications(self):
        """Open notification settings dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Notifications")
        dialog.setMinimumSize(500, 450)
        dialog.setStyleSheet(f"background-color: {PANEL_BG}; color: {CYAN};")
        
        layout = QVBoxLayout(dialog)
        
        title = QLabel("🔔 Notification Settings")
        title.setStyleSheet(f"color: {CYAN}; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        settings = self.notification_manager.get_all_settings()
        
        checkboxes = {}
        items = [
            ("daily_horoscope", "Daily Horoscope"),
            ("transit_alerts", "Transit Alerts"),
            ("eclipse_alerts", "Eclipse Alerts"),
            ("planetary_ingress", "Planetary Ingress"),
            ("birthday_reminders", "Birthday Reminders"),
        ]
        
        for key, label in items:
            cb = QCheckBox(label)
            cb.setChecked(settings.get(key, True))
            cb.setStyleSheet(f"color: {CYAN}; font-size: 12px;")
            cb.stateChanged.connect(lambda checked, k=key, c=cb: self._update_notification_setting(k, c.isChecked()))
            layout.addWidget(cb)
            checkboxes[key] = cb
        
        # Enable/Disable all
        enable_cb = QCheckBox("Enable All Notifications")
        enable_cb.setChecked(settings.get("enabled", True))
        enable_cb.setStyleSheet(f"color: {AMBER}; font-size: 13px; font-weight: bold;")
        enable_cb.stateChanged.connect(lambda checked: self._update_notification_setting("enabled", enable_cb.isChecked()))
        layout.addWidget(enable_cb)
        
        layout.addSpacing(10)
        
        # Preview
        preview_label = QLabel("📬 Notification Preview:")
        preview_label.setStyleSheet(f"color: {CYAN}; font-weight: bold;")
        layout.addWidget(preview_label)
        
        preview_box = QTextEdit()
        preview_box.setReadOnly(True)
        preview_box.setMaximumHeight(120)
        preview_box.setStyleSheet(f"background-color: {DARK_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; border-radius: 6px; padding: 8px;")
        if self.current_chart:
            preview_box.setPlainText(self.notification_manager.get_notification_summary(self.current_chart))
        else:
            preview_box.setPlainText("Generate a chart to see notifications.")
        layout.addWidget(preview_box)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(
            f"background-color: {CYAN}; color: {DARK_BG}; border-radius: 6px; padding: 10px; "
            "font-family: Consolas, monospace; font-weight: bold;"
        )
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def _update_notification_setting(self, key, value):
        self.notification_manager.update_settings(key, value)
        self.statusBar().showMessage(f"Notification setting updated: {key} = {value}")
    
    # ---------- Birth Time Rectification ----------
    
    def _open_rectification(self):
        """Open birth time rectification dialog"""
        if not self.current_chart:
            QMessageBox.warning(self, "No Chart", "Please generate a chart first!")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Birth Time Rectification")
        dialog.setMinimumSize(600, 500)
        dialog.setStyleSheet(f"background-color: {PANEL_BG}; color: {CYAN};")
        
        layout = QVBoxLayout(dialog)
        
        title = QLabel("🔧 Birth Time Rectification")
        title.setStyleSheet(f"color: {AMBER}; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        desc = QLabel(
            "Add your life events to correct birth time.\n"
            "Format: YYYY-MM-DD, Type, Description\n"
            "Types: marriage, career, education, spiritual, health, travel"
        )
        desc.setStyleSheet(f"color: {CYAN_DIM}; font-size: 11px;")
        layout.addWidget(desc)
        
        events_box = QTextEdit()
        events_box.setPlaceholderText(
            "2020-06-15, marriage, Got married\n"
            "2018-04-10, career, Started new job\n"
            "2019-09-20, education, Graduated from university"
        )
        events_box.setStyleSheet(
            f"background-color: {DARK_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
            "border-radius: 6px; padding: 10px; font-family: Consolas, monospace; min-height: 150px;"
        )
        layout.addWidget(events_box)
        
        result_box = QTextEdit()
        result_box.setReadOnly(True)
        result_box.setPlaceholderText("Rectification results will appear here...")
        result_box.setStyleSheet(
            f"background-color: {DARK_BG}; color: {CYAN}; border: 1px solid {CYAN_DIM}; "
            "border-radius: 6px; padding: 10px; font-family: Segoe UI, sans-serif; min-height: 150px;"
        )
        layout.addWidget(result_box)
        
        btn_layout = QHBoxLayout()
        
        def do_rectification():
            events = []
            for line in events_box.toPlainText().strip().split('\n'):
                if line.strip():
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 2:
                        try:
                            event_date = datetime.strptime(parts[0], "%Y-%m-%d")
                            event_type = parts[1].lower()
                            desc = parts[2] if len(parts) > 2 else ""
                            events.append({"date": event_date, "type": event_type, "description": desc})
                        except:
                            pass
            
            if len(events) < 3:
                result_box.setPlainText("⚠️ Please add at least 3 events for accurate rectification.")
                return
            
            rectifier = BirthTimeRectifier(self.current_chart, events)
            report = rectifier.get_rectification_report()
            
            text = f"""
🚀 RECTIFICATION REPORT
═══════════════════════════════════════

📊 Confidence Score: {report['confidence']*100:.1f}%
📝 Events Used: {report['number_of_events']}

📋 RECOMMENDATIONS:
{chr(10).join(f'   • {r}' for r in report['recommendations'])}

⏰ Adjusted Time: {report['rectification'].get('adjusted_time', 0):.1f} hours
🔧 Method: {report['rectification'].get('method', 'unknown')}
✅ Success: {report['rectification'].get('success', False)}

📅 EVENTS ANALYZED:
"""
            for event in events:
                text += f"   • {event['date'].strftime('%Y-%m-%d')} - {event['type']}: {event['description']}\n"
            
            result_box.setPlainText(text)
            self.statusBar().showMessage("✅ Rectification complete!")
        
        rect_btn = QPushButton("🔧 Rectify Birth Time")
        rect_btn.setStyleSheet(
            f"background-color: {PURPLE}; color: {DARK_BG}; border-radius: 6px; padding: 10px; "
            "font-family: Consolas, monospace; font-weight: bold; font-size: 13px;"
        )
        rect_btn.clicked.connect(do_rectification)
        btn_layout.addWidget(rect_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(
            f"background-color: {CYAN}; color: {DARK_BG}; border-radius: 6px; padding: 10px; "
            "font-family: Consolas, monospace; font-weight: bold;"
        )
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    # ---------- Settings ----------
    
    def open_api_settings(self):
        dialog = APISettingsDialog(self)
        dialog.exec()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SkyTrailWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()