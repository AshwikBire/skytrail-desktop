"""
API Settings Dialog for SkyTrail Desktop
Allows users to configure Nemotron API key
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QCheckBox,
    QGroupBox, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from api_key_manager import key_manager

class APISettingsDialog(QDialog):
    """Dialog for managing API keys"""
    
    keys_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SkyTrail - API Settings")
        self.setFixedSize(500, 400)
        self.setup_ui()
        self.load_current_keys()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🔑 API Key Management")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        layout.addWidget(QLabel("Configure your API keys for AI services."))
        layout.addSpacing(10)
        
        # Nemotron Section
        nemotron_group = QGroupBox("Nemotron (NVIDIA Cloud AI)")
        nemotron_layout = QVBoxLayout()
        
        # Description
        desc = QLabel(
            "Get your free API key from NVIDIA Build:\n"
            "https://build.nvidia.com"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; font-size: 11px;")
        nemotron_layout.addWidget(desc)
        
        # API Key input
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("nvapi-xxxxxxxxxxxxxxxxxxxx")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        key_layout.addWidget(self.key_input)
        nemotron_layout.addLayout(key_layout)
        
        # Show/Hide toggle
        show_layout = QHBoxLayout()
        self.show_key_checkbox = QCheckBox("Show API Key")
        self.show_key_checkbox.stateChanged.connect(self.toggle_key_visibility)
        show_layout.addWidget(self.show_key_checkbox)
        show_layout.addStretch()
        nemotron_layout.addLayout(show_layout)
        
        # Current status
        self.status_label = QLabel()
        self.status_label.setStyleSheet("font-size: 11px; padding: 5px;")
        nemotron_layout.addWidget(self.status_label)
        
        # Buttons for Nemotron
        btn_layout = QHBoxLayout()
        self.test_btn = QPushButton("Test Key")
        self.test_btn.clicked.connect(self.test_nemotron_key)
        self.save_btn = QPushButton("Save Key")
        self.save_btn.clicked.connect(self.save_nemotron_key)
        self.delete_btn = QPushButton("Delete Key")
        self.delete_btn.clicked.connect(self.delete_nemotron_key)
        self.delete_btn.setStyleSheet("color: #d9534f;")
        
        btn_layout.addWidget(self.test_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.delete_btn)
        nemotron_layout.addLayout(btn_layout)
        
        nemotron_group.setLayout(nemotron_layout)
        layout.addWidget(nemotron_group)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setFixedWidth(100)
        
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)
    
    def load_current_keys(self):
        """Load and display current API keys"""
        has_key = key_manager.has_key("nemotron")
        if has_key:
            self.status_label.setText("✅ Nemotron API key is configured")
            self.status_label.setStyleSheet("color: #28a745; font-size: 11px; padding: 5px;")
            self.delete_btn.setEnabled(True)
            self.key_input.setPlaceholderText("••••••••••••••••••••••••")
        else:
            self.status_label.setText("❌ No Nemotron API key configured")
            self.status_label.setStyleSheet("color: #dc3545; font-size: 11px; padding: 5px;")
            self.delete_btn.setEnabled(False)
            self.key_input.setPlaceholderText("nvapi-xxxxxxxxxxxxxxxxxxxx")
    
    def toggle_key_visibility(self, state):
        """Toggle API key visibility"""
        if state == Qt.CheckState.Checked:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def save_nemotron_key(self):
        """Save Nemotron API key"""
        key = self.key_input.text().strip()
        
        if not key:
            QMessageBox.warning(self, "Error", "Please enter an API key")
            return
        
        if not key.startswith("nvapi-"):
            QMessageBox.warning(self, "Invalid Key", 
                "Nemotron API key should start with 'nvapi-'\n"
                "Get your key from: https://build.nvidia.com")
            return
        
        try:
            # Save the key
            key_manager.save_nemotron_key(key)
            
            # Update UI
            self.load_current_keys()
            self.key_input.clear()
            
            QMessageBox.information(self, "Success", 
                "✅ Nemotron API key saved successfully!\n\n"
                "You can now use AI: NEMOTRON for cloud-based readings.")
            
            self.keys_updated.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save key: {str(e)}")
    
    def delete_nemotron_key(self):
        """Delete Nemotron API key"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete your Nemotron API key?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            key_manager.delete_nemotron_key()
            self.load_current_keys()
            self.key_input.clear()
            QMessageBox.information(self, "Deleted", "Nemotron API key deleted.")
            self.keys_updated.emit()
    
    def test_nemotron_key(self):
        """Test the Nemotron API key"""
        key = self.key_input.text().strip()
        if not key and not key_manager.has_key("nemotron"):
            QMessageBox.warning(self, "Error", "No API key to test. Please enter or save one first.")
            return
        
        # Use entered key or saved key
        if key:
            test_key = key
        else:
            test_key = key_manager.get_nemotron_key()
        
        if not test_key:
            QMessageBox.warning(self, "Error", "No API key found.")
            return
        
        # Test the key
        from horoscope_ai import test_nemotron_key
        result = test_nemotron_key(test_key)
        
        if result["success"]:
            QMessageBox.information(self, "Success", 
                f"✅ Nemotron API key is valid!\n\n"
                f"Model: {result.get('model', 'NVIDIA Nemotron')}\n"
                f"Response time: {result.get('response_time', 0):.2f}s")
        else:
            QMessageBox.critical(self, "Error", 
                f"❌ Nemotron API key is invalid!\n\n"
                f"Error: {result.get('error', 'Unknown error')}\n\n"
                f"Please check your key and try again.\n"
                f"Get a key from: https://build.nvidia.com")