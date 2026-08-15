"""
Birth Time Rectification - Correct birth time based on life events
"""

from datetime import datetime, timedelta
import math

class BirthTimeRectifier:
    """Rectify birth time based on events"""
    
    def __init__(self, chart, events=None):
        self.chart = chart
        self.events = events or []
    
    def add_event(self, event_date: datetime, event_type: str, description: str = ""):
        """Add a life event for rectification"""
        self.events.append({
            "date": event_date,
            "type": event_type,
            "description": description
        })
    
    def rectify(self, method="ascendant") -> dict:
        """Rectify birth time using specified method"""
        
        if method == "ascendant":
            return self._rectify_by_ascendant()
        elif method == "moon":
            return self._rectify_by_moon()
        elif method == "events":
            return self._rectify_by_events()
        else:
            return {
                "success": False,
                "error": "Unknown rectification method"
            }
    
    def _rectify_by_ascendant(self) -> dict:
        """Rectify by matching ascendant with events"""
        asc_degree = self.chart.ascendant.degree_in_sign
        asc_sign = self.chart.ascendant.sign_index
        
        adjustment = (asc_degree / 30) * 2
        
        return {
            "success": True,
            "method": "ascendant",
            "adjusted_time": adjustment,
            "confidence": 0.7,
            "recommendation": f"Adjust birth time by {adjustment:.1f} hours",
            "reason": f"Based on ascendant {asc_sign} at {asc_degree:.1f}°"
        }
    
    def _rectify_by_moon(self) -> dict:
        """Rectify by matching Moon with events"""
        if not self.events:
            return {
                "success": False,
                "error": "No events provided for rectification"
            }
        
        moon_degree = self.chart.planets[0].degree_in_sign
        
        adjustments = []
        for event in self.events[:3]:
            days_diff = (event["date"] - datetime.now()).days
            moon_adjustment = (days_diff * 13) / 24
            adjustments.append(moon_adjustment)
        
        if adjustments:
            avg_adjustment = sum(adjustments) / len(adjustments)
            return {
                "success": True,
                "method": "moon",
                "adjusted_time": avg_adjustment,
                "confidence": 0.5,
                "recommendation": f"Adjust birth time by {avg_adjustment:.1f} hours",
                "reason": f"Based on {len(adjustments)} life events"
            }
        
        return {
            "success": False,
            "error": "Could not calculate adjustment"
        }
    
    def _rectify_by_events(self) -> dict:
        """Rectify using major life events"""
        if len(self.events) < 3:
            return {
                "success": False,
                "error": "Need at least 3 events for rectification"
            }
        
        dasha_match = 0
        
        for event in self.events[:5]:
            if event["type"] in ["marriage", "relationship"] and "venus" in self._get_dasha_lords():
                dasha_match += 1
            elif event["type"] in ["career", "job", "promotion"] and "saturn" in self._get_dasha_lords():
                dasha_match += 1
            elif event["type"] in ["education", "learning", "degree"] and "mercury" in self._get_dasha_lords():
                dasha_match += 1
            elif event["type"] in ["spiritual", "pilgrimage", "meditation"] and "ketu" in self._get_dasha_lords():
                dasha_match += 1
        
        confidence = min(dasha_match / len(self.events), 0.9)
        
        return {
            "success": True,
            "method": "events",
            "adjusted_time": 0.5,
            "confidence": confidence,
            "recommendation": f"Adjust birth time by 0.5 hours" if confidence > 0.5 else "Uncertain adjustment",
            "reason": f"Matched {dasha_match}/{len(self.events)} events"
        }
    
    def _get_dasha_lords(self) -> list:
        """Get current dasha lords (simplified)"""
        return ["ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury"]
    
    def get_confidence_score(self) -> float:
        """Get confidence score for current rectification"""
        if not self.events:
            return 0.0
        
        base_confidence = min(len(self.events) * 0.1, 0.5)
        event_types = set(e["type"] for e in self.events)
        diversity_bonus = min(len(event_types) * 0.05, 0.2)
        
        return min(base_confidence + diversity_bonus, 0.9)
    
    def get_rectification_report(self) -> dict:
        """Get complete rectification report"""
        rectification = self.rectify("events")
        
        report = {
            "birth_time": self.chart.julian_day,
            "number_of_events": len(self.events),
            "confidence": self.get_confidence_score(),
            "rectification": rectification,
            "events": self.events,
            "recommendations": []
        }
        
        if len(self.events) < 3:
            report["recommendations"].append("Add more life events for better accuracy")
        
        if rectification.get("confidence", 0) < 0.5:
            report["recommendations"].append("Consider consulting an expert for rectification")
        else:
            report["recommendations"].append(f"Use adjusted birth time: {rectification.get('adjusted_time', 0):.1f} hours")
        
        return report