"""
Panchang - Vedic Calendar System
Tithi, Vara, Nakshatra, Yoga, Karana for any date
"""

from datetime import datetime, timedelta
import math

class Panchang:
    """Vedic Panchang calculator"""
    
    def __init__(self, date: datetime, latitude: float, longitude: float, tz_offset: float):
        self.date = date
        self.latitude = latitude
        self.longitude = longitude
        self.tz_offset = tz_offset
        self._calculate_panchang()
    
    def _calculate_panchang(self):
        """Calculate all Panchang components"""
        # Convert to Julian Day
        jd = self._to_julian_day(self.date)
        
        # Calculate Tithi (Lunar day)
        self.tithi = self._calculate_tithi(jd)
        self.tithi_name = self._get_tithi_name(self.tithi)
        self.tithi_end = self._calculate_tithi_end(jd)
        
        # Calculate Vara (Weekday)
        self.vara = self.date.weekday()
        self.vara_name = self._get_vara_name(self.vara)
        self.vara_lord = self._get_vara_lord(self.vara)
        
        # Calculate Nakshatra
        self.nakshatra = self._calculate_nakshatra(jd)
        self.nakshatra_name = self._get_nakshatra_name(self.nakshatra)
        self.nakshatra_lord = self._get_nakshatra_lord(self.nakshatra)
        
        # Calculate Yoga
        self.yoga = self._calculate_yoga(jd)
        self.yoga_name = self._get_yoga_name(self.yoga)
        
        # Calculate Karana
        self.karana = self._calculate_karana(jd)
        self.karana_name = self._get_karana_name(self.karana)
        
        # Sunrise/Sunset
        self.sunrise = self._calculate_sunrise()
        self.sunset = self._calculate_sunset()
        
        # Rahu Kaal
        self.rahu_kaal = self._calculate_rahu_kaal()
        
        # Gulika Kaal
        self.gulika_kaal = self._calculate_gulika_kaal()
        
        # Yamaganda
        self.yamaganda = self._calculate_yamaganda()
        
        # Auspicious periods
        self.auspicious_periods = self._calculate_auspicious_periods()
    
    def _to_julian_day(self, date: datetime) -> float:
        """Convert datetime to Julian Day"""
        year = date.year
        month = date.month
        day = date.day + date.hour/24 + date.minute/1440
        
        if month <= 2:
            year -= 1
            month += 12
        
        a = year // 100
        b = 2 - a + a // 4
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
        return jd
    
    def _calculate_tithi(self, jd: float) -> int:
        """Calculate Tithi (1-30)"""
        # Simplified: using lunar cycle
        # New Moon = 0, Full Moon = 15
        lunar_day = (jd - 2451550.1) / 29.530587981
        tithi = int((lunar_day % 1) * 30) + 1
        return tithi
    
    def _get_tithi_name(self, tithi: int) -> str:
        """Get Tithi name"""
        tithi_names = {
            1: "Pratipada", 2: "Dwitiya", 3: "Tritiya", 4: "Chaturthi",
            5: "Panchami", 6: "Shashthi", 7: "Saptami", 8: "Ashtami",
            9: "Navami", 10: "Dashami", 11: "Ekadashi", 12: "Dwadashi",
            13: "Trayodashi", 14: "Chaturdashi", 15: "Amavasya/Purnima",
            16: "Pratipada", 17: "Dwitiya", 18: "Tritiya", 19: "Chaturthi",
            20: "Panchami", 21: "Shashthi", 22: "Saptami", 23: "Ashtami",
            24: "Navami", 25: "Dashami", 26: "Ekadashi", 27: "Dwadashi",
            28: "Trayodashi", 29: "Chaturdashi", 30: "Purnima/Amavasya"
        }
        return tithi_names.get(tithi, "Unknown")
    
    def _calculate_tithi_end(self, jd: float) -> datetime:
        """Calculate when Tithi ends"""
        # Simplified: add ~3-4 hours
        return self.date + timedelta(hours=3.5)
    
    def _get_vara_name(self, vara: int) -> str:
        """Get Vara (weekday) name"""
        vara_names = {
            0: "Ravivar (Sunday)",
            1: "Somvar (Monday)",
            2: "Mangalvar (Tuesday)",
            3: "Budhvar (Wednesday)",
            4: "Guruvar (Thursday)",
            5: "Shukravar (Friday)",
            6: "Shanivar (Saturday)"
        }
        return vara_names.get(vara, "Unknown")
    
    def _get_vara_lord(self, vara: int) -> str:
        """Get Vara lord"""
        vara_lords = {
            0: "Sun", 1: "Moon", 2: "Mars", 3: "Mercury",
            4: "Jupiter", 5: "Venus", 6: "Saturn"
        }
        return vara_lords.get(vara, "Unknown")
    
    def _calculate_nakshatra(self, jd: float) -> int:
        """Calculate Nakshatra (0-26)"""
        # 27 Nakshatras, each 13°20'
        moon_longitude = self._calculate_moon_longitude(jd)
        nakshatra = int(moon_longitude / 13.3333) % 27
        return nakshatra
    
    def _calculate_moon_longitude(self, jd: float) -> float:
        """Calculate Moon's longitude (simplified)"""
        # Rough approximation
        moon_cycle = (jd - 2451550.1) / 29.530587981
        return (moon_cycle % 1) * 360
    
    def _get_nakshatra_name(self, nakshatra: int) -> str:
        """Get Nakshatra name"""
        nakshatra_names = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
            "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
            "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra",
            "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
            "Purva Ashadha", "Uttara Ashadha", "Shravana",
            "Dhanishtha", "Shatabhisha", "Purva Bhadrapada",
            "Uttara Bhadrapada", "Revati"
        ]
        return nakshatra_names[nakshatra % 27]
    
    def _get_nakshatra_lord(self, nakshatra: int) -> str:
        """Get Nakshatra lord"""
        lords = [
            "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
            "Jupiter", "Saturn", "Mercury", "Ketu", "Venus",
            "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn",
            "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars",
            "Rahu", "Jupiter", "Saturn", "Mercury"
        ]
        return lords[nakshatra % 27]
    
    def _calculate_yoga(self, jd: float) -> int:
        """Calculate Yoga (0-26)"""
        # Simplified: sum of sun and moon longitudes
        sun_lon = self._calculate_sun_longitude(jd)
        moon_lon = self._calculate_moon_longitude(jd)
        sum_lon = (sun_lon + moon_lon) % 360
        return int(sum_lon / 13.3333) % 27
    
    def _calculate_sun_longitude(self, jd: float) -> float:
        """Calculate Sun's longitude (simplified)"""
        days_since_equinox = (jd - 2451550.1) % 365.25
        return (days_since_equinox / 365.25) * 360
    
    def _get_yoga_name(self, yoga: int) -> str:
        """Get Yoga name"""
        yoga_names = [
            "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
            "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
            "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
            "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
            "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
            "Indra", "Vaidhriti"
        ]
        return yoga_names[yoga % 27]
    
    def _calculate_karana(self, jd: float) -> int:
        """Calculate Karana (0-10)"""
        # 11 Karanas
        tithi = self._calculate_tithi(jd)
        if tithi % 2 == 0:
            karana = tithi // 2
        else:
            karana = tithi // 2 + 1
        return karana % 11
    
    def _get_karana_name(self, karana: int) -> str:
        """Get Karana name"""
        karana_names = [
            "Bava", "Balava", "Kaulava", "Taitila", "Gara",
            "Vanija", "Vishti", "Shakuni", "Chatushpada",
            "Naga", "Kimstughna"
        ]
        return karana_names[karana % 11]
    
    def _calculate_sunrise(self) -> datetime:
        """Calculate sunrise time"""
        # Simplified: 6 AM for demo
        return self.date.replace(hour=6, minute=0)
    
    def _calculate_sunset(self) -> datetime:
        """Calculate sunset time"""
        # Simplified: 6 PM for demo
        return self.date.replace(hour=18, minute=0)
    
    def _calculate_rahu_kaal(self) -> dict:
        """Calculate Rahu Kaal periods"""
        # Simplified: 8 periods per day
        rahu_periods = {
            0: (4, 6),  # Sunday
            1: (6, 8),  # Monday
            2: (8, 10), # Tuesday
            3: (10, 12),# Wednesday
            4: (12, 14),# Thursday
            5: (14, 16),# Friday
            6: (16, 18) # Saturday
        }
        start, end = rahu_periods.get(self.vara, (6, 8))
        return {
            "start": self.date.replace(hour=start, minute=0),
            "end": self.date.replace(hour=end, minute=0),
            "duration": end - start
        }
    
    def _calculate_gulika_kaal(self) -> dict:
        """Calculate Gulika Kaal"""
        # Simplified: 90 minutes after sunrise
        start = self.sunrise + timedelta(hours=1.5)
        return {
            "start": start,
            "end": start + timedelta(hours=1.5),
            "duration": 1.5
        }
    
    def _calculate_yamaganda(self) -> dict:
        """Calculate Yamaganda"""
        # Simplified: 2 hours after sunrise
        start = self.sunrise + timedelta(hours=2)
        return {
            "start": start,
            "end": start + timedelta(hours=1.5),
            "duration": 1.5
        }
    
    def _calculate_auspicious_periods(self) -> list:
        """Calculate auspicious periods"""
        # Simplified: Abhijit Muhurta (11:45 AM - 12:30 PM)
        periods = [
            {
                "name": "Abhijit Muhurta",
                "start": self.date.replace(hour=11, minute=45),
                "end": self.date.replace(hour=12, minute=30),
                "description": "Most auspicious period of the day"
            },
            {
                "name": "Brahma Muhurta",
                "start": self.date.replace(hour=4, minute=30),
                "end": self.date.replace(hour=5, minute=30),
                "description": "Best for meditation and spiritual practices"
            }
        ]
        return periods
    
    def get_panchang_dict(self) -> dict:
        """Get complete Panchang as dictionary"""
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "tithi": {
                "name": self.tithi_name,
                "number": self.tithi,
                "end_time": self.tithi_end.strftime("%H:%M")
            },
            "vara": {
                "name": self.vara_name,
                "lord": self.vara_lord
            },
            "nakshatra": {
                "name": self.nakshatra_name,
                "lord": self.nakshatra_lord,
                "number": self.nakshatra
            },
            "yoga": {
                "name": self.yoga_name,
                "number": self.yoga
            },
            "karana": {
                "name": self.karana_name,
                "number": self.karana
            },
            "sun": {
                "rise": self.sunrise.strftime("%H:%M"),
                "set": self.sunset.strftime("%H:%M")
            },
            "inauspicious_periods": {
                "rahu_kaal": {
                    "start": self.rahu_kaal["start"].strftime("%H:%M"),
                    "end": self.rahu_kaal["end"].strftime("%H:%M")
                },
                "gulika_kaal": {
                    "start": self.gulika_kaal["start"].strftime("%H:%M"),
                    "end": self.gulika_kaal["end"].strftime("%H:%M")
                },
                "yamaganda": {
                    "start": self.yamaganda["start"].strftime("%H:%M"),
                    "end": self.yamaganda["end"].strftime("%H:%M")
                }
            },
            "auspicious_periods": [
                {
                    "name": p["name"],
                    "start": p["start"].strftime("%H:%M"),
                    "end": p["end"].strftime("%H:%M"),
                    "description": p["description"]
                } for p in self.auspicious_periods
            ]
        }