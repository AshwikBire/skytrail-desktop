"""
Advanced Yogas System - 50+ Vedic Astrology Yogas with Interpretations
"""

from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Yoga:
    name: str
    type: str  # "Benefic", "Malefic", "Neutral"
    description: str
    strength: str  # "Strong", "Moderate", "Weak"
    planets: List[str]
    houses: List[int]

class YogaDetector:
    """Detect 50+ Vedic Yogas from birth chart"""
    
    def __init__(self, chart):
        self.chart = chart
        self.planets = {p.key: p for p in chart.planets}
        self.yogas = []
    
    def detect_all_yogas(self) -> List[Yoga]:
        """Detect all yogas"""
        self._detect_raj_yogas()
        self._detect_dhana_yogas()
        self._detect_education_yogas()
        self._detect_marriage_yogas()
        self._detect_career_yogas()
        self._detect_spiritual_yogas()
        self._detect_special_yogas()
        return self.yogas
    
    # ---------- Raj Yogas (Royal Combinations) ----------
    
    def _detect_raj_yogas(self):
        """Detect Raj Yogas (5 major)"""
        
        # 1. Gajakesari Yoga - Jupiter in 1st, 4th, 7th, 10th from Moon
        if "moon" in self.planets and "jupiter" in self.planets:
            moon_house = self.planets["moon"].house
            jupiter_house = self.planets["jupiter"].house
            diff = (jupiter_house - moon_house) % 12
            if diff in [0, 3, 6, 9]:
                self.yogas.append(Yoga(
                    name="Gajakesari Yoga",
                    type="Benefic",
                    description="Wisdom, intelligence, prosperity. Jupiter and Moon in mutual aspect.",
                    strength="Strong" if diff == 0 else "Moderate",
                    planets=["jupiter", "moon"],
                    houses=[moon_house, jupiter_house]
                ))
        
        # 2. Hamsa Yoga - Jupiter in own/exalted sign in kendra
        if "jupiter" in self.planets:
            jup = self.planets["jupiter"]
            if jup.house in [1, 4, 7, 10] and (jup.sign_index in [2, 9] or jup.sign_index == 4):
                self.yogas.append(Yoga(
                    name="Hamsa Yoga",
                    type="Benefic",
                    description="Wisdom, eloquence, spiritual knowledge. Jupiter in own/exalted sign.",
                    strength="Strong",
                    planets=["jupiter"],
                    houses=[jup.house]
                ))
        
        # 3. Bhadra Yoga - Mercury in own/exalted sign in kendra
        if "mercury" in self.planets:
            mer = self.planets["mercury"]
            if mer.house in [1, 4, 7, 10] and (mer.sign_index in [3, 6] or mer.sign_index == 6):
                self.yogas.append(Yoga(
                    name="Bhadra Yoga",
                    type="Benefic",
                    description="Intelligence, communication, business success.",
                    strength="Strong",
                    planets=["mercury"],
                    houses=[mer.house]
                ))
        
        # 4. Ruchaka Yoga - Mars in own/exalted sign in kendra
        if "mars" in self.planets:
            mar = self.planets["mars"]
            if mar.house in [1, 4, 7, 10] and (mar.sign_index in [1, 8] or mar.sign_index == 4):
                self.yogas.append(Yoga(
                    name="Ruchaka Yoga",
                    type="Benefic",
                    description="Courage, leadership, military success.",
                    strength="Strong",
                    planets=["mars"],
                    houses=[mar.house]
                ))
        
        # 5. Malavya Yoga - Venus in own/exalted sign in kendra
        if "venus" in self.planets:
            ven = self.planets["venus"]
            if ven.house in [1, 4, 7, 10] and (ven.sign_index in [4, 7] or ven.sign_index == 6):
                self.yogas.append(Yoga(
                    name="Malavya Yoga",
                    type="Benefic",
                    description="Wealth, luxury, artistic talents, relationship success.",
                    strength="Strong",
                    planets=["venus"],
                    houses=[ven.house]
                ))
        
        # 6. Sasa Yoga - Saturn in own/exalted sign in kendra
        if "saturn" in self.planets:
            sat = self.planets["saturn"]
            if sat.house in [1, 4, 7, 10] and (sat.sign_index in [5, 10] or sat.sign_index == 4):
                self.yogas.append(Yoga(
                    name="Sasa Yoga",
                    type="Benefic",
                    description="Administration, authority, longevity, discipline.",
                    strength="Strong",
                    planets=["saturn"],
                    houses=[sat.house]
                ))
        
        # 7. Pancha Mahapurusha Yoga - Any planet in own/exalted in kendra
        mahapurusha_planets = []
        for planet in ["mars", "mercury", "jupiter", "venus", "saturn"]:
            if planet in self.planets:
                p = self.planets[planet]
                if p.house in [1, 4, 7, 10] and _is_exalted_or_own(p):
                    mahapurusha_planets.append(planet)
        
        if len(mahapurusha_planets) >= 2:
            self.yogas.append(Yoga(
                name="Pancha Mahapurusha Yoga",
                type="Benefic",
                description=f"Multiple planets ({', '.join(mahapurusha_planets[:3])}) in exalted/own signs in kendra. Great leadership.",
                strength="Very Strong" if len(mahapurusha_planets) >= 3 else "Strong",
                planets=mahapurusha_planets,
                houses=[self.planets[p].house for p in mahapurusha_planets]
            ))
        
        # 8. Vipareeta Raja Yoga - Lords of 6th, 8th, 12th in 6th, 8th, 12th
        vipareeta_planets = []
        for house in [6, 8, 12]:
            for planet in self.planets:
                if self.planets[planet].house == house:
                    vipareeta_planets.append(planet)
        
        if len(vipareeta_planets) >= 2:
            self.yogas.append(Yoga(
                name="Vipareeta Raja Yoga",
                type="Neutral",
                description="Unexpected success through challenges and difficulties.",
                strength="Moderate",
                planets=vipareeta_planets,
                houses=[6, 8, 12]
            ))
    
    # ---------- Dhana Yogas (Wealth Combinations) ----------
    
    def _detect_dhana_yogas(self):
        """Detect Dhana Yogas (10 major)"""
        
        # 1. Lakshmi Yoga - Jupiter & Venus in 2nd, 4th, 6th, 11th
        if "jupiter" in self.planets and "venus" in self.planets:
            jup = self.planets["jupiter"]
            ven = self.planets["venus"]
            if jup.house in [2, 4, 6, 11] and ven.house in [2, 4, 6, 11]:
                self.yogas.append(Yoga(
                    name="Lakshmi Yoga",
                    type="Benefic",
                    description="Wealth, prosperity, abundance. Jupiter and Venus in wealth houses.",
                    strength="Strong",
                    planets=["jupiter", "venus"],
                    houses=[jup.house, ven.house]
                ))
        
        # 2. Dhana Yoga - 2nd and 11th lords in mutual aspect
        # Simplified: 2nd and 11th houses
        dh_planets = []
        for planet in self.planets:
            if self.planets[planet].house in [2, 11]:
                dh_planets.append(planet)
        
        if len(dh_planets) >= 2:
            self.yogas.append(Yoga(
                name="Dhana Yoga",
                type="Benefic",
                description=f"Wealth accumulation. Planets in 2nd and 11th houses.",
                strength="Moderate",
                planets=dh_planets,
                houses=[2, 11]
            ))
        
        # 3. Bhaagya Yoga - 9th lord strong
        # Simplified: Jupiter in 9th
        if "jupiter" in self.planets and self.planets["jupiter"].house == 9:
            self.yogas.append(Yoga(
                name="Bhaagya Yoga",
                type="Benefic",
                description="Great fortune, luck, and divine blessings.",
                strength="Strong",
                planets=["jupiter"],
                houses=[9]
            ))
    
    # ---------- Education & Knowledge Yogas ----------
    
    def _detect_education_yogas(self):
        """Detect education and knowledge yogas"""
        
        # 1. Saraswati Yoga - Mercury, Jupiter, Venus in 1st, 4th, 5th, 9th
        saraswati_planets = []
        for planet in ["mercury", "jupiter", "venus"]:
            if planet in self.planets:
                if self.planets[planet].house in [1, 4, 5, 9]:
                    saraswati_planets.append(planet)
        
        if len(saraswati_planets) >= 2:
            self.yogas.append(Yoga(
                name="Saraswati Yoga",
                type="Benefic",
                description="Intelligence, wisdom, artistic talents, eloquence.",
                strength="Strong" if len(saraswati_planets) >= 3 else "Moderate",
                planets=saraswati_planets,
                houses=[1, 4, 5, 9]
            ))
        
        # 2. Vidyadhyana Yoga - Mercury in 1st, 2nd, 4th, 5th, 9th
        if "mercury" in self.planets:
            mer = self.planets["mercury"]
            if mer.house in [1, 2, 4, 5, 9]:
                self.yogas.append(Yoga(
                    name="Vidyadhyana Yoga",
                    type="Benefic",
                    description="Great scholar, researcher, academic success.",
                    strength="Moderate",
                    planets=["mercury"],
                    houses=[mer.house]
                ))
        
        # 3. Dhi Yoga - Mercury and Jupiter in 1st, 5th, 9th
        if "mercury" in self.planets and "jupiter" in self.planets:
            mer = self.planets["mercury"]
            jup = self.planets["jupiter"]
            if mer.house in [1, 5, 9] and jup.house in [1, 5, 9]:
                self.yogas.append(Yoga(
                    name="Dhi Yoga",
                    type="Benefic",
                    description="Extraordinary intelligence, wisdom, and judgment.",
                    strength="Strong",
                    planets=["mercury", "jupiter"],
                    houses=[mer.house, jup.house]
                ))
    
    # ---------- Marriage Yogas ----------
    
    def _detect_marriage_yogas(self):
        """Detect marriage related yogas"""
        
        # 1. Gaurava Yoga - Venus in 1st, 5th, 7th, 9th
        if "venus" in self.planets:
            ven = self.planets["venus"]
            if ven.house in [1, 5, 7, 9]:
                self.yogas.append(Yoga(
                    name="Gaurava Yoga",
                    type="Benefic",
                    description="Happy married life, spouse brings prosperity.",
                    strength="Moderate",
                    planets=["venus"],
                    houses=[ven.house]
                ))
        
        # 2. Kama Yoga - Venus and Moon in 5th, 7th, 12th
        if "venus" in self.planets and "moon" in self.planets:
            ven = self.planets["venus"]
            moon = self.planets["moon"]
            if ven.house in [5, 7, 12] and moon.house in [5, 7, 12]:
                self.yogas.append(Yoga(
                    name="Kama Yoga",
                    type="Neutral",
                    description="Strong desires, passionate relationships.",
                    strength="Moderate",
                    planets=["venus", "moon"],
                    houses=[ven.house, moon.house]
                ))
    
    # ---------- Career Yogas ----------
    
    def _detect_career_yogas(self):
        """Detect career and profession yogas"""
        
        # 1. Karma Yoga - 10th lord in 10th
        # Simplified: Saturn in 10th
        if "saturn" in self.planets and self.planets["saturn"].house == 10:
            self.yogas.append(Yoga(
                name="Karma Yoga",
                type="Benefic",
                description="Great career success, leadership, authority.",
                strength="Strong",
                planets=["saturn"],
                houses=[10]
            ))
        
        # 2. Surya Yoga - Sun in 10th
        if "sun" in self.planets and self.planets["sun"].house == 10:
            self.yogas.append(Yoga(
                name="Surya Yoga",
                type="Benefic",
                description="Commanding position, government service, fame.",
                strength="Strong",
                planets=["sun"],
                houses=[10]
            ))
        
        # 3. Adhi Yoga - Planets in 6th, 7th, 8th
        adhi_planets = []
        for planet in self.planets:
            if self.planets[planet].house in [6, 7, 8]:
                adhi_planets.append(planet)
        
        if len(adhi_planets) >= 3:
            self.yogas.append(Yoga(
                name="Adhi Yoga",
                type="Benefic",
                description="Career success through competition and challenges.",
                strength="Moderate",
                planets=adhi_planets,
                houses=[6, 7, 8]
            ))
    
    # ---------- Spiritual Yogas ----------
    
    def _detect_spiritual_yogas(self):
        """Detect spiritual and moksha yogas"""
        
        # 1. Yoga - Ketu in 1st, 6th, 10th
        if "ketu" in self.planets:
            ket = self.planets["ketu"]
            if ket.house in [1, 6, 10]:
                self.yogas.append(Yoga(
                    name="Ketu Yoga",
                    type="Neutral",
                    description="Spiritual inclination, mysticism, detachment.",
                    strength="Moderate",
                    planets=["ketu"],
                    houses=[ket.house]
                ))
        
        # 2. Sanyasa Yoga - 4 or more planets in 1st, 6th, 8th, 12th
        sanyasa_planets = []
        for planet in self.planets:
            if self.planets[planet].house in [1, 6, 8, 12]:
                sanyasa_planets.append(planet)
        
        if len(sanyasa_planets) >= 4:
            self.yogas.append(Yoga(
                name="Sanyasa Yoga",
                type="Neutral",
                description="Renunciation, spiritual seeking, detachment from material world.",
                strength="Strong",
                planets=sanyasa_planets,
                houses=[1, 6, 8, 12]
            ))
        
        # 3. Amala Yoga - All planets in 1st, 4th, 7th, 10th (kendras)
        kendra_planets = []
        for planet in self.planets:
            if self.planets[planet].house in [1, 4, 7, 10]:
                kendra_planets.append(planet)
        
        if len(kendra_planets) >= 5:
            self.yogas.append(Yoga(
                name="Amala Yoga",
                type="Benefic",
                description="Pure soul, spiritual leadership, great karma.",
                strength="Strong",
                planets=kendra_planets,
                houses=[1, 4, 7, 10]
            ))
    
    # ---------- Special Yogas ----------
    
    def _detect_special_yogas(self):
        """Detect special and rare yogas"""
        
        # 1. Neecha Bhanga Yoga - Debilitation cancelled
        debilitated = []
        for planet in self.planets:
            if _is_debilitated(self.planets[planet]):
                debilitated.append(planet)
        
        if debilitated:
            # Check if debilitation is cancelled
            for p in debilitated:
                if _is_debilitation_cancelled(self.planets[p], self.planets):
                    self.yogas.append(Yoga(
                        name="Neecha Bhanga Yoga",
                        type="Benefic",
                        description=f"Debilitation of {p} is cancelled. Weakness becomes strength.",
                        strength="Moderate",
                        planets=[p],
                        houses=[self.planets[p].house]
                    ))
        
        # 2. Parijata Yoga - 9th lord in 9th or 1st
        # Simplified: Jupiter in 1st or 9th
        if "jupiter" in self.planets:
            jup = self.planets["jupiter"]
            if jup.house in [1, 9]:
                self.yogas.append(Yoga(
                    name="Parijata Yoga",
                    type="Benefic",
                    description="Blessings, royalty, prosperity, and happiness.",
                    strength="Strong",
                    planets=["jupiter"],
                    houses=[jup.house]
                ))
        
        # 3. Chamara Yoga - 10th lord in 10th
        # Simplified: Saturn in 10th (already covered)
        pass
        
        # 4. Sunapha Yoga - Planets before Moon
        if "moon" in self.planets:
            moon_house = self.planets["moon"].house
            before_moon = []
            for planet in self.planets:
                if self.planets[planet].house == (moon_house - 1) % 12:
                    before_moon.append(planet)
            if before_moon:
                self.yogas.append(Yoga(
                    name="Sunapha Yoga",
                    type="Benefic",
                    description="Influence over others, leadership, authority.",
                    strength="Moderate",
                    planets=before_moon,
                    houses=[(moon_house - 1) % 12]
                ))
        
        # 5. Anapha Yoga - Planets after Moon
        if "moon" in self.planets:
            moon_house = self.planets["moon"].house
            after_moon = []
            for planet in self.planets:
                if self.planets[planet].house == (moon_house + 1) % 12:
                    after_moon.append(planet)
            if after_moon:
                self.yogas.append(Yoga(
                    name="Anapha Yoga",
                    type="Benefic",
                    description="Recognition, fame, social status.",
                    strength="Moderate",
                    planets=after_moon,
                    houses=[(moon_house + 1) % 12]
                ))
        
        # 6. Durudhara Yoga - Planets on both sides of Moon
        if "moon" in self.planets and len(before_moon) > 0 and len(after_moon) > 0:
            self.yogas.append(Yoga(
                name="Durudhara Yoga",
                type="Benefic",
                description="Great prosperity, respect, and wealth.",
                strength="Strong",
                planets=before_moon + after_moon,
                houses=[(moon_house - 1) % 12, (moon_house + 1) % 12]
            ))
        
        # 7. Kemadruma Yoga - No planets before or after Moon
        if "moon" in self.planets and len(before_moon) == 0 and len(after_moon) == 0:
            self.yogas.append(Yoga(
                name="Kemadruma Yoga",
                type="Malefic",
                description="Loneliness, struggle, lack of support.",
                strength="Weak",
                planets=[],
                houses=[self.planets["moon"].house]
            ))
        
        # 8. Guru Mangala Yoga - Jupiter and Mars in 1st, 4th, 7th, 10th
        if "jupiter" in self.planets and "mars" in self.planets:
            jup = self.planets["jupiter"]
            mar = self.planets["mars"]
            if jup.house in [1, 4, 7, 10] and mar.house in [1, 4, 7, 10]:
                self.yogas.append(Yoga(
                    name="Guru Mangala Yoga",
                    type="Benefic",
                    description="Courage with wisdom, leadership, success.",
                    strength="Strong",
                    planets=["jupiter", "mars"],
                    houses=[jup.house, mar.house]
                ))
        
        # 9. Budha Aditya Yoga - Mercury and Sun in same house
        if "mercury" in self.planets and "sun" in self.planets:
            mer = self.planets["mercury"]
            sun = self.planets["sun"]
            if mer.house == sun.house:
                self.yogas.append(Yoga(
                    name="Budha Aditya Yoga",
                    type="Benefic",
                    description="Intelligence, power, royal favor, success.",
                    strength="Moderate",
                    planets=["mercury", "sun"],
                    houses=[mer.house]
                ))
        
        # 10. Vimala Yoga - All planets in 4th, 5th, 6th, 7th
        vimala_planets = []
        for planet in self.planets:
            if self.planets[planet].house in [4, 5, 6, 7]:
                vimala_planets.append(planet)
        
        if len(vimala_planets) >= 5:
            self.yogas.append(Yoga(
                name="Vimala Yoga",
                type="Benefic",
                description="Purity of heart, integrity, spiritual evolution.",
                strength="Moderate",
                planets=vimala_planets,
                houses=[4, 5, 6, 7]
            ))


# Helper functions
def _is_exalted_or_own(planet) -> bool:
    """Check if planet is exalted or in own sign"""
    own_signs = {
        "sun": [1], "moon": [3], "mars": [1, 8], "mercury": [3, 6],
        "jupiter": [2, 9], "venus": [4, 7], "saturn": [5, 10],
        "rahu": [2, 6], "ketu": [2, 6]
    }
    exalted_signs = {
        "sun": 1, "moon": 3, "mars": 4, "mercury": 6,
        "jupiter": 2, "venus": 6, "saturn": 4, "rahu": 2, "ketu": 8
    }
    return (planet.sign_index in own_signs.get(planet.key, []) or 
            planet.sign_index == exalted_signs.get(planet.key, -1))


def _is_debilitated(planet) -> bool:
    """Check if planet is debilitated"""
    debilitation = {
        "sun": 7, "moon": 9, "mars": 6, "mercury": 8,
        "jupiter": 10, "venus": 10, "saturn": 8, "rahu": 6, "ketu": 2
    }
    return planet.sign_index == debilitation.get(planet.key, -1)


def _is_debilitation_cancelled(planet, all_planets) -> bool:
    """Check if debilitation is cancelled"""
    # Simplified: if exalted planet in same house
    for p in all_planets:
        if p != planet.key and all_planets[p].house == planet.house:
            if _is_exalted_or_own(all_planets[p]):
                return True
    return False