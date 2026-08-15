"""
Transits & Predictions
Current planet positions and their effects on natal chart
"""

from datetime import datetime, timedelta
from astro_calc import compute_chart

class TransitAnalyzer:
    """Analyze planetary transits and predict effects"""
    
    def __init__(self, birth_chart, latitude: float, longitude: float, tz_offset: float):
        self.birth_chart = birth_chart
        self.latitude = latitude
        self.longitude = longitude
        self.tz_offset = tz_offset
        self.current_chart = None
        self._get_current_transits()
    
    def _get_current_transits(self):
        """Get current planet positions"""
        now = datetime.now()
        self.current_chart = compute_chart(now, self.tz_offset, self.latitude, self.longitude, self.birth_chart.system)
    
    def get_transit_effects(self) -> dict:
        """Get effects of all current transits"""
        effects = {}
        
        for natal_planet in self.birth_chart.planets:
            if natal_planet.key == "rahu" or natal_planet.key == "ketu":
                continue
            
            # Find transit position
            transit_planet = next((p for p in self.current_chart.planets if p.key == natal_planet.key), None)
            if not transit_planet:
                continue
            
            # Check house transit
            natal_house = natal_planet.house
            transit_house = transit_planet.house
            
            # Aspect check
            aspects = self._get_aspects(natal_planet, transit_planet)
            
            # Determine effect
            effect = self._determine_effect(natal_planet, transit_planet, aspects)
            
            effects[natal_planet.key] = {
                "natal_position": f"House {natal_house}, Sign {natal_planet.sign_index}",
                "transit_position": f"House {transit_house}, Sign {transit_planet.sign_index}",
                "aspects": aspects,
                "effect": effect,
                "significance": self._get_significance(natal_planet.key, transit_house)
            }
        
        return effects
    
    def _get_aspects(self, natal_planet, transit_planet) -> list:
        """Get aspects between natal and transit planets"""
        aspects = []
        
        # Check conjunction (0°)
        if abs(natal_planet.longitude - transit_planet.longitude) < 8:
            aspects.append("Conjunction (0°)")
        # Check opposition (180°)
        elif abs(abs(natal_planet.longitude - transit_planet.longitude) - 180) < 8:
            aspects.append("Opposition (180°)")
        # Check trine (120°)
        elif abs(abs(natal_planet.longitude - transit_planet.longitude) - 120) < 8:
            aspects.append("Trine (120°)")
        # Check square (90°)
        elif abs(abs(natal_planet.longitude - transit_planet.longitude) - 90) < 8:
            aspects.append("Square (90°)")
        # Check sextile (60°)
        elif abs(abs(natal_planet.longitude - transit_planet.longitude) - 60) < 8:
            aspects.append("Sextile (60°)")
        
        return aspects
    
    def _determine_effect(self, natal_planet, transit_planet, aspects) -> str:
        """Determine effect of transit"""
        if "Conjunction" in aspects:
            return "Strong activation"
        elif "Opposition" in aspects:
            return "Challenge and growth"
        elif "Square" in aspects:
            return "Tension and learning"
        elif "Trine" in aspects:
            return "Opportunity and ease"
        elif "Sextile" in aspects:
            return "Positive opportunities"
        else:
            return "Neutral"
    
    def _get_significance(self, planet_key: str, house: int) -> str:
        """Get significance of transit"""
        significance = {
            "sun": "Career, authority, health, self-expression",
            "moon": "Emotions, mind, relationships, mental health",
            "mercury": "Communication, intellect, business, travel",
            "venus": "Relationships, wealth, luxury, creativity",
            "mars": "Energy, courage, action, conflicts",
            "jupiter": "Growth, fortune, wisdom, opportunity",
            "saturn": "Discipline, karma, challenges, structure"
        }
        
        house_meaning = {
            1: "Self, personality, identity",
            2: "Wealth, values, speech, family",
            3: "Courage, communication, siblings",
            4: "Home, mother, vehicles, happiness",
            5: "Education, children, creativity, intelligence",
            6: "Health, enemies, diseases, service",
            7: "Marriage, partnerships, business",
            8: "Transformation, longevity, death, secrets",
            9: "Fortune, spirituality, dharma, father",
            10: "Career, karma, status, authority",
            11: "Gains, wishes, friends, community",
            12: "Loss, liberation, foreign travel, isolation"
        }
        
        base = significance.get(planet_key, "")
        house_meaning_text = house_meaning.get(house, "")
        return f"{base} - {house_meaning_text}"
    
    def get_current_transit_predictions(self) -> dict:
        """Get transit predictions for all houses"""
        predictions = {}
        
        for house in range(1, 13):
            # Find planets transiting this house
            transiting_planets = [p for p in self.current_chart.planets if p.house == house]
            
            if transiting_planets:
                # Get house significance
                house_meaning = {
                    1: "You're entering a new phase of self-discovery.",
                    2: "Focus on your values and financial stability.",
                    3: "Important communications and learning opportunities.",
                    4: "Home and family matters come into focus.",
                    5: "Creative expression and romance are highlighted.",
                    6: "Health and daily routines need attention.",
                    7: "Important relationships and partnerships are key.",
                    8: "Transformation and deep changes are happening.",
                    9: "Expansion through travel and education.",
                    10: "Career and public status are important.",
                    11: "Social networks and goal achievement.",
                    12: "Spiritual growth and letting go."
                }
                
                predictions[house] = {
                    "planets": [p.key for p in transiting_planets],
                    "house_meaning": house_meaning.get(house, ""),
                    "prediction": self._generate_prediction(house, transiting_planets)
                }
        
        return predictions
    
    def _generate_prediction(self, house: int, planets: list) -> str:
        """Generate a prediction for a house based on transiting planets"""
        planet_names = [p.key for p in planets]
        planet_str = ", ".join(planet_names)
        
        predictions = {
            1: f"Planets {planet_str} are transiting your 1st house. This is a time for personal transformation.",
            2: f"With {planet_str} in your 2nd house, focus on your values and financial growth.",
            3: f"{planet_str} are highlighting communication and learning. Express yourself!",
            4: f"{planet_str} in the 4th house brings focus to home, family, and emotional stability.",
            5: f"{planet_str} are activating your 5th house of creativity and romance.",
            6: f"Health and service are highlighted with {planet_str} in your 6th house.",
            7: f"Relationships and partnerships are in focus with {planet_str} in the 7th house.",
            8: f"Transformation and deep healing are possible with {planet_str} in the 8th house.",
            9: f"{planet_str} are bringing opportunities for growth and expansion in your 9th house.",
            10: f"Career and life direction are important now with {planet_str} in the 10th house.",
            11: f"Social connections and goals are highlighted with {planet_str} in the 11th house.",
            12: f"{planet_str} are activating your 12th house of spirituality and letting go."
        }
        
        return predictions.get(house, f"Transiting planets {planet_str} are influencing your {house}th house.")
    
    def get_yearly_forecast(self) -> dict:
        """Get yearly forecast based on transits"""
        forecast = {}
        
        for month in range(1, 13):
            # Simulate monthly changes
            month_date = datetime.now().replace(month=month, day=1)
            
            if month in [1, 4, 7, 10]:
                forecast[month] = "Major transitions and changes"
            elif month in [2, 5, 8, 11]:
                forecast[month] = "Growth and opportunities"
            elif month in [3, 6, 9, 12]:
                forecast[month] = "Reflection and preparation"
            else:
                forecast[month] = "Stable period"
        
        return forecast