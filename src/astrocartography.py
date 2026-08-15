"""
Astrocartography - Astrological Geography
Finding favorable locations based on birth chart
"""

class Astrocartographer:
    """Calculate favorable locations based on astrology"""
    
    def __init__(self, chart):
        self.chart = chart
        self.planet_positions = {p.key: p for p in chart.planets}
    
    def get_favorable_locations(self, category="all") -> dict:
        """Get favorable locations for different life areas"""
        
        locations = {
            "career": self._get_career_locations(),
            "marriage": self._get_marriage_locations(),
            "success": self._get_success_locations(),
            "spiritual": self._get_spiritual_locations(),
            "wealth": self._get_wealth_locations(),
            "education": self._get_education_locations(),
        }
        
        if category != "all":
            return {category: locations.get(category, [])}
        
        return locations
    
    def _get_career_locations(self) -> list:
        """Get locations good for career"""
        locations = []
        
        for planet in ["sun", "saturn", "mercury", "jupiter"]:
            if planet in self.planet_positions:
                p = self.planet_positions[planet]
                if p.house in [1, 5, 9, 10]:
                    locations.append({
                        "planet": planet,
                        "direction": self._get_direction(p.sign_index),
                        "house": p.house,
                        "strength": "Strong",
                        "reason": f"{planet.capitalize()} in favorable house {p.house} for career"
                    })
        
        return locations
    
    def _get_marriage_locations(self) -> list:
        """Get locations good for marriage"""
        locations = []
        
        if "venus" in self.planet_positions:
            ven = self.planet_positions["venus"]
            locations.append({
                "planet": "venus",
                "direction": self._get_direction(ven.sign_index),
                "house": ven.house,
                "strength": "Strong" if ven.house in [1, 5, 7, 9] else "Moderate",
                "reason": "Venus influences relationships and marriage"
            })
        
        if "jupiter" in self.planet_positions:
            jup = self.planet_positions["jupiter"]
            if jup.house in [1, 5, 7, 9]:
                locations.append({
                    "planet": "jupiter",
                    "direction": self._get_direction(jup.sign_index),
                    "house": jup.house,
                    "strength": "Strong",
                    "reason": "Jupiter in 7th house indicates good marriage"
                })
        
        return locations
    
    def _get_success_locations(self) -> list:
        """Get locations good for overall success"""
        locations = []
        
        for planet in ["sun", "jupiter", "mars"]:
            if planet in self.planet_positions:
                p = self.planet_positions[planet]
                if p.house in [1, 5, 9, 10]:
                    locations.append({
                        "planet": planet,
                        "direction": self._get_direction(p.sign_index),
                        "house": p.house,
                        "strength": "Strong",
                        "reason": f"{planet.capitalize()} in house {p.house} brings success"
                    })
        
        return locations
    
    def _get_spiritual_locations(self) -> list:
        """Get locations good for spiritual growth"""
        locations = []
        
        if "ketu" in self.planet_positions:
            ket = self.planet_positions["ketu"]
            locations.append({
                "planet": "ketu",
                "direction": self._get_direction(ket.sign_index),
                "house": ket.house,
                "strength": "Strong" if ket.house in [1, 6, 10] else "Moderate",
                "reason": "Ketu represents spiritual inclinations"
            })
        
        for planet in ["moon", "jupiter"]:
            if planet in self.planet_positions:
                p = self.planet_positions[planet]
                if p.house == 12:
                    locations.append({
                        "planet": planet,
                        "direction": self._get_direction(p.sign_index),
                        "house": 12,
                        "strength": "Strong",
                        "reason": f"{planet.capitalize()} in 12th house for spirituality"
                    })
        
        return locations
    
    def _get_wealth_locations(self) -> list:
        """Get locations good for wealth"""
        locations = []
        
        for planet in ["jupiter", "venus"]:
            if planet in self.planet_positions:
                p = self.planet_positions[planet]
                if p.house in [2, 11]:
                    locations.append({
                        "planet": planet,
                        "direction": self._get_direction(p.sign_index),
                        "house": p.house,
                        "strength": "Strong",
                        "reason": f"{planet.capitalize()} in wealth house {p.house}"
                    })
        
        return locations
    
    def _get_education_locations(self) -> list:
        """Get locations good for education"""
        locations = []
        
        if "mercury" in self.planet_positions:
            mer = self.planet_positions["mercury"]
            locations.append({
                "planet": "mercury",
                "direction": self._get_direction(mer.sign_index),
                "house": mer.house,
                "strength": "Strong" if mer.house in [1, 5, 9] else "Moderate",
                "reason": "Mercury represents learning and communication"
            })
        
        if "jupiter" in self.planet_positions:
            jup = self.planet_positions["jupiter"]
            if jup.house in [1, 5, 9]:
                locations.append({
                    "planet": "jupiter",
                    "direction": self._get_direction(jup.sign_index),
                    "house": jup.house,
                    "strength": "Strong",
                    "reason": "Jupiter in 5th/9th house for education"
                })
        
        return locations
    
    def _get_direction(self, sign_index: int) -> str:
        """Get direction based on sign"""
        directions = {
            0: "East", 1: "East", 2: "South-East", 3: "South",
            4: "South", 5: "South-West", 6: "West", 7: "West",
            8: "North-West", 9: "North", 10: "North", 11: "North-East"
        }
        return directions.get(sign_index, "Unknown")
    
    def get_world_map_data(self) -> dict:
        """Get data for world map visualization"""
        city_coordinates = {
            "New York": (40.7128, -74.0060),
            "London": (51.5074, -0.1278),
            "Tokyo": (35.6762, 139.6503),
            "Sydney": (-33.8688, 151.2093),
            "Dubai": (25.2048, 55.2708),
            "Singapore": (1.3521, 103.8198),
            "Mumbai": (19.0760, 72.8777),
            "Shanghai": (31.2304, 121.4737),
            "Paris": (48.8566, 2.3522),
            "Rome": (41.9028, 12.4964),
            "Los Angeles": (34.0522, -118.2437),
            "Mexico City": (19.4326, -99.1332),
            "Cairo": (30.0444, 31.2357),
            "Moscow": (55.7558, 37.6173),
            "Bangkok": (13.7563, 100.5018),
            "Seoul": (37.5665, 126.9780),
            "Toronto": (43.6532, -79.3832),
            "Berlin": (52.5200, 13.4050),
            "Barcelona": (41.3851, 2.1734),
            "Amsterdam": (52.3676, 4.9041),
            "Vancouver": (49.2827, -123.1207),
            "San Francisco": (37.7749, -122.4194),
            "Chicago": (41.8781, -87.6298),
            "Boston": (42.3601, -71.0589),
        }
        return city_coordinates
    
    def recommend_cities(self, category="career") -> list:
        """Recommend cities for a specific category"""
        # Get locations for the category
        locations_dict = self.get_favorable_locations(category)
        city_coords = self.get_world_map_data()
        
        recommendations = []
        # Get the locations list safely
        locations_list = locations_dict.get(category, []) if isinstance(locations_dict, dict) else []
        
        for loc in locations_list[:10]:
            direction = loc.get("direction", "")
            direction_cities = {
                "East": ["Tokyo", "Shanghai", "Bangkok", "Seoul"],
                "West": ["Los Angeles", "San Francisco", "Vancouver", "Mexico City"],
                "North": ["Moscow", "Berlin", "Toronto"],
                "South": ["Sydney", "Cairo", "Dubai"],
                "North-East": ["New York", "Boston", "London"],
                "South-East": ["Singapore", "Mumbai", "Bangkok"],
                "North-West": ["London", "Paris", "Amsterdam"],
                "South-West": ["Mexico City", "Los Angeles", "San Francisco"],
            }
            
            cities = direction_cities.get(direction, [])
            for city in cities[:3]:
                if city in city_coords:
                    recommendations.append({
                        "city": city,
                        "direction": direction,
                        "planet": loc.get("planet", ""),
                        "strength": loc.get("strength", "Moderate"),
                        "coordinates": city_coords[city]
                    })
        
        # Remove duplicates
        seen = set()
        unique_recommendations = []
        for r in recommendations:
            key = r["city"]
            if key not in seen:
                seen.add(key)
                unique_recommendations.append(r)
        
        return unique_recommendations[:10]


# For backward compatibility
Astrocartographer = Astrocartographer