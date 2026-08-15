"""
Push Notifications for SkyTrail Desktop
"""

import json
import os
from datetime import datetime
from pathlib import Path


class NotificationManager:
    """Manage notifications and alerts"""
    
    def __init__(self):
        self.app_dir = Path(os.path.expanduser("~/.skytrail"))
        self.app_dir.mkdir(exist_ok=True)
        self.settings_file = self.app_dir / "notifications.json"
        self.settings = self._default_settings()
        self._load_settings()
    
    def _load_settings(self):
        """Load notification settings"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except:
                pass
    
    def _default_settings(self):
        """Get default notification settings"""
        return {
            "daily_horoscope": True,
            "transit_alerts": True,
            "eclipse_alerts": True,
            "planetary_ingress": True,
            "birthday_reminders": True,
            "notification_time": "08:00",
            "enabled": True
        }
    
    def _save_settings(self):
        """Save notification settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except:
            return False
    
    def update_settings(self, key: str, value):
        """Update a notification setting"""
        self.settings[key] = value
        return self._save_settings()
    
    def get_all_settings(self) -> dict:
        """Get all notification settings"""
        return self.settings
    
    def check_notifications(self, chart) -> list:
        """Check for notifications based on chart"""
        notifications = []
        
        if not self.settings.get("enabled", True):
            return notifications
        
        # Daily Horoscope
        if self.settings.get("daily_horoscope", True):
            notifications.append({
                "type": "daily_horoscope",
                "title": "Daily Horoscope",
                "message": "Your daily horoscope is ready for today!",
                "time": datetime.now().strftime("%H:%M")
            })
        
        # Transit Alerts
        if self.settings.get("transit_alerts", True) and chart:
            try:
                from transits import TransitAnalyzer
                analyzer = TransitAnalyzer(chart, 0, 0, 5.5)
                effects = analyzer.get_transit_effects()
                
                for planet, data in effects.items():
                    aspects = " ".join(data.get("aspects", []))
                    if "Square" in aspects or "Opposition" in aspects:
                        notifications.append({
                            "type": "transit_alert",
                            "title": f"Transit Alert: {planet.capitalize()}",
                            "message": f"{planet.capitalize()} is currently {data.get('effect', '')}.",
                            "time": datetime.now().strftime("%H:%M")
                        })
                        break
            except:
                pass
        
        return notifications
    
    def get_notification_count(self, chart) -> int:
        """Get number of active notifications"""
        return len(self.check_notifications(chart))
    
    def get_notification_summary(self, chart) -> str:
        """Get notification summary text"""
        notifications = self.check_notifications(chart)
        
        if not notifications:
            return "No new notifications"
        
        summary = f"You have {len(notifications)} notification(s):\n\n"
        for n in notifications[:5]:
            summary += f"- {n['title']}\n  {n['message']}\n\n"
        
        return summary


# Create singleton instance
notification_manager = NotificationManager()