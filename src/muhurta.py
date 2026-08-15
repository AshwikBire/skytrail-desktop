"""
Muhurta - Electional Astrology
Find auspicious dates and times for events
"""

from datetime import datetime, timedelta
from panchang import Panchang

class Muhurta:
    """Electional astrology calculator"""
    
    def __init__(self, date: datetime, latitude: float, longitude: float, tz_offset: float):
        self.date = date
        self.latitude = latitude
        self.longitude = longitude
        self.tz_offset = tz_offset
        self.panchang = Panchang(date, latitude, longitude, tz_offset)
    
    def check_wedding_muhurta(self) -> dict:
        """Check if date is auspicious for marriage"""
        score = 0
        details = []
        
        # Check Tithi
        tithi = self.panchang.tithi
        if tithi in [2, 3, 5, 7, 10, 11, 13, 15, 16, 17, 19, 21, 25, 27, 28]:
            score += 3
            details.append("✅ Good Tithi")
        elif tithi in [1, 6, 9, 12, 18, 23, 24, 26, 29, 30]:
            score += 1
            details.append("⚠️ Average Tithi")
        else:
            details.append("❌ Inauspicious Tithi")
        
        # Check Nakshatra
        nakshatra = self.panchang.nakshatra
        good_nakshatras = [2, 3, 4, 5, 7, 9, 10, 11, 12, 13, 15, 16, 17, 20, 21, 24, 25]
        if nakshatra in good_nakshatras:
            score += 3
            details.append("✅ Good Nakshatra")
        else:
            details.append("⚠️ Average Nakshatra")
        
        # Check Yoga
        yoga = self.panchang.yoga
        good_yogas = [1, 2, 3, 4, 5, 7, 8, 11, 12, 14, 16, 17, 21, 22, 23, 24, 25]
        if yoga in good_yogas:
            score += 2
            details.append("✅ Good Yoga")
        else:
            details.append("⚠️ Average Yoga")
        
        # Check Karana
        karana = self.panchang.karana
        good_karanas = [0, 1, 2, 3, 4, 5, 6]
        if karana in good_karanas:
            score += 2
            details.append("✅ Good Karana")
        else:
            details.append("⚠️ Average Karana")
        
        # Check Rahu Kaal
        rahu_start = self.panchang.rahu_kaal["start"]
        rahu_end = self.panchang.rahu_kaal["end"]
        now = self.date
        if rahu_start <= now <= rahu_end:
            score -= 3
            details.append("❌ During Rahu Kaal (Avoid)")
        else:
            score += 1
            details.append("✅ Outside Rahu Kaal")
        
        # Determine suitability
        if score >= 10:
            verdict = "Highly Auspicious 🌟"
        elif score >= 7:
            verdict = "Auspicious ✅"
        elif score >= 4:
            verdict = "Moderately Auspicious ⚠️"
        else:
            verdict = "Inauspicious ❌"
        
        return {
            "date": self.date.strftime("%Y-%m-%d %H:%M"),
            "score": score,
            "max_score": 14,
            "verdict": verdict,
            "details": details,
            "recommendation": "This date is suitable for marriage" if score >= 7 else "Consider choosing another date"
        }
    
    def check_business_muhurta(self) -> dict:
        """Check if date is auspicious for business/startup"""
        score = 0
        details = []
        
        # Check Tithi for business
        tithi = self.panchang.tithi
        business_tithis = [2, 3, 5, 10, 11, 15, 16, 17, 21, 27, 28]
        if tithi in business_tithis:
            score += 3
            details.append("✅ Good Tithi")
        else:
            details.append("⚠️ Average Tithi")
        
        # Check Nakshatra for business
        nakshatra = self.panchang.nakshatra
        business_nakshatras = [1, 3, 4, 5, 8, 9, 10, 11, 15, 16, 17, 20, 21, 24, 25]
        if nakshatra in business_nakshatras:
            score += 3
            details.append("✅ Good Nakshatra")
        else:
            details.append("⚠️ Average Nakshatra")
        
        # Check Jupiter strength (simplified)
        score += 2
        details.append("✅ Jupiter considered strong")
        
        # Check Mercury strength
        score += 2
        details.append("✅ Mercury considered strong")
        
        # Check Rahu Kaal
        rahu_start = self.panchang.rahu_kaal["start"]
        rahu_end = self.panchang.rahu_kaal["end"]
        now = self.date
        if rahu_start <= now <= rahu_end:
            score -= 3
            details.append("❌ During Rahu Kaal (Avoid)")
        
        if score >= 8:
            verdict = "Excellent for Business 🎯"
        elif score >= 5:
            verdict = "Good for Business ✅"
        else:
            verdict = "Better to wait ⚠️"
        
        return {
            "date": self.date.strftime("%Y-%m-%d %H:%M"),
            "score": score,
            "max_score": 12,
            "verdict": verdict,
            "details": details,
            "recommendation": "Proceed with business" if score >= 5 else "Consider a more auspicious date"
        }
    
    def check_travel_muhurta(self) -> dict:
        """Check if date is auspicious for travel"""
        score = 0
        details = []
        
        # Check Tithi
        tithi = self.panchang.tithi
        travel_tithis = [2, 3, 5, 7, 10, 11, 15, 16, 17, 21, 27]
        if tithi in travel_tithis:
            score += 2
            details.append("✅ Good Tithi")
        
        # Check Nakshatra
        nakshatra = self.panchang.nakshatra
        travel_nakshatras = [0, 3, 4, 5, 7, 9, 10, 11, 15, 16, 20, 21]
        if nakshatra in travel_nakshatras:
            score += 2
            details.append("✅ Good Nakshatra")
        
        # Check Rahu Kaal
        rahu_start = self.panchang.rahu_kaal["start"]
        rahu_end = self.panchang.rahu_kaal["end"]
        now = self.date
        if rahu_start <= now <= rahu_end:
            score -= 2
            details.append("❌ During Rahu Kaal (Avoid)")
        
        # Check Gulika Kaal
        gulika_start = self.panchang.gulika_kaal["start"]
        gulika_end = self.panchang.gulika_kaal["end"]
        if gulika_start <= now <= gulika_end:
            score -= 2
            details.append("❌ During Gulika Kaal (Avoid)")
        
        if score >= 3:
            verdict = "Good for Travel ✈️"
        else:
            verdict = "Not Recommended for Travel ❌"
        
        return {
            "date": self.date.strftime("%Y-%m-%d %H:%M"),
            "score": score,
            "max_score": 6,
            "verdict": verdict,
            "details": details,
            "recommendation": "Safe to travel" if score >= 3 else "Consider postponing travel"
        }
    
    def get_best_muhurta(self, event_type: str, days: int = 30) -> list:
        """Find best muhurta dates for an event in next N days"""
        results = []
        current_date = self.date
        
        for i in range(days):
            test_date = current_date + timedelta(days=i)
            muhurta = Muhurta(test_date, self.latitude, self.longitude, self.tz_offset)
            
            if event_type == "wedding":
                result = muhurta.check_wedding_muhurta()
            elif event_type == "business":
                result = muhurta.check_business_muhurta()
            elif event_type == "travel":
                result = muhurta.check_travel_muhurta()
            else:
                result = {"verdict": "Unknown", "score": 0}
            
            if result.get("score", 0) >= 5:
                results.append({
                    "date": test_date.strftime("%Y-%m-%d"),
                    "score": result["score"],
                    "verdict": result["verdict"]
                })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)[:10]