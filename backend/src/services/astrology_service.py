import swisseph as swe
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Any, Optional
import math
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
import logging

logger = logging.getLogger(__name__)


class AstrologyService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="astrologer-bot")
        self.tf = TimezoneFinder()
        
        # Planet constants
        self.PLANETS = {
            swe.SUN: "Sun",
            swe.MOON: "Moon", 
            swe.MERCURY: "Mercury",
            swe.VENUS: "Venus",
            swe.MARS: "Mars",
            swe.JUPITER: "Jupiter",
            swe.SATURN: "Saturn",
            swe.URANUS: "Uranus",
            swe.NEPTUNE: "Neptune",
            swe.PLUTO: "Pluto"
        }
        
        # Zodiac signs
        self.SIGNS = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        
        # Houses
        self.HOUSES = [
            "1st House", "2nd House", "3rd House", "4th House", "5th House", "6th House",
            "7th House", "8th House", "9th House", "10th House", "11th House", "12th House"
        ]
    
    async def get_coordinates(self, location: str) -> Tuple[float, float]:
        """Get latitude and longitude for a location"""
        try:
            location_data = self.geolocator.geocode(location)
            if location_data:
                return location_data.latitude, location_data.longitude
            else:
                raise ValueError(f"Location not found: {location}")
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            raise
    
    def get_timezone(self, latitude: float, longitude: float) -> str:
        """Get timezone for coordinates"""
        try:
            tz_name = self.tf.timezone_at(lat=latitude, lng=longitude)
            return tz_name or "UTC"
        except Exception as e:
            logger.error(f"Timezone lookup error: {e}")
            return "UTC"
    
    def calculate_julian_day(self, dt: datetime, latitude: float, longitude: float) -> float:
        """Calculate Julian Day Number for given datetime and location"""
        try:
            # Convert to UTC if timezone aware
            if dt.tzinfo:
                dt_utc = dt.astimezone(timezone.utc)
            else:
                dt_utc = dt.replace(tzinfo=timezone.utc)
            
            # Calculate Julian Day
            jd = swe.julday(
                dt_utc.year, dt_utc.month, dt_utc.day,
                dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
            )
            
            return jd
        except Exception as e:
            logger.error(f"Julian day calculation error: {e}")
            raise
    
    def calculate_natal_chart(
        self, 
        birth_date: datetime, 
        latitude: float, 
        longitude: float
    ) -> Dict[str, Any]:
        """Calculate complete natal chart"""
        try:
            jd = self.calculate_julian_day(birth_date, latitude, longitude)
            
            # Calculate planetary positions
            planets = {}
            for planet_id, planet_name in self.PLANETS.items():
                try:
                    pos, _ = swe.calc_ut(jd, planet_id)
                    longitude_deg = pos[0]
                    
                    # Calculate sign and degree
                    sign_index = int(longitude_deg // 30)
                    degree_in_sign = longitude_deg % 30
                    
                    planets[planet_name] = {
                        "longitude": longitude_deg,
                        "sign": self.SIGNS[sign_index],
                        "degree": degree_in_sign,
                        "formatted": f"{degree_in_sign:.1f}° {self.SIGNS[sign_index]}"
                    }
                except Exception as e:
                    logger.error(f"Error calculating {planet_name}: {e}")
                    continue
            
            # Calculate houses using Placidus system
            houses = self.calculate_houses(jd, latitude, longitude)
            
            # Calculate aspects
            aspects = self.calculate_aspects(planets)
            
            return {
                "planets": planets,
                "houses": houses,
                "aspects": aspects,
                "birth_info": {
                    "date": birth_date.isoformat(),
                    "latitude": latitude,
                    "longitude": longitude,
                    "julian_day": jd
                }
            }
            
        except Exception as e:
            logger.error(f"Natal chart calculation error: {e}")
            raise
    
    def calculate_houses(self, jd: float, latitude: float, longitude: float) -> Dict[str, Any]:
        """Calculate house cusps using Placidus system"""
        try:
            # Calculate houses
            cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')  # Placidus system
            
            houses = {}
            for i, cusp in enumerate(cusps):
                if i < 12:  # Only 12 houses
                    sign_index = int(cusp // 30)
                    degree_in_sign = cusp % 30
                    
                    houses[self.HOUSES[i]] = {
                        "cusp": cusp,
                        "sign": self.SIGNS[sign_index],
                        "degree": degree_in_sign,
                        "formatted": f"{degree_in_sign:.1f}° {self.SIGNS[sign_index]}"
                    }
            
            # Add important points
            houses["Ascendant"] = {
                "cusp": ascmc[0],
                "sign": self.SIGNS[int(ascmc[0] // 30)],
                "degree": ascmc[0] % 30,
                "formatted": f"{ascmc[0] % 30:.1f}° {self.SIGNS[int(ascmc[0] // 30)]}"
            }
            
            houses["Midheaven"] = {
                "cusp": ascmc[1],
                "sign": self.SIGNS[int(ascmc[1] // 30)],
                "degree": ascmc[1] % 30,
                "formatted": f"{ascmc[1] % 30:.1f}° {self.SIGNS[int(ascmc[1] // 30)]}"
            }
            
            return houses
            
        except Exception as e:
            logger.error(f"House calculation error: {e}")
            return {}
    
    def calculate_aspects(self, planets: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Calculate major aspects between planets"""
        aspects = []
        aspect_orbs = {
            "Conjunction": (0, 8),
            "Opposition": (180, 8),
            "Trine": (120, 8),
            "Square": (90, 8),
            "Sextile": (60, 6)
        }
        
        planet_names = list(planets.keys())
        
        for i, planet1 in enumerate(planet_names):
            for planet2 in planet_names[i+1:]:
                try:
                    lon1 = planets[planet1]["longitude"]
                    lon2 = planets[planet2]["longitude"]
                    
                    # Calculate angular difference
                    diff = abs(lon1 - lon2)
                    if diff > 180:
                        diff = 360 - diff
                    
                    # Check for aspects
                    for aspect_name, (aspect_angle, orb) in aspect_orbs.items():
                        if abs(diff - aspect_angle) <= orb:
                            aspects.append({
                                "planet1": planet1,
                                "planet2": planet2,
                                "aspect": aspect_name,
                                "angle": diff,
                                "orb": abs(diff - aspect_angle),
                                "exact_angle": aspect_angle
                            })
                            break
                            
                except Exception as e:
                    logger.error(f"Aspect calculation error for {planet1}-{planet2}: {e}")
                    continue
        
        return aspects
    
    def get_current_transits(self, natal_planets: Dict[str, Dict]) -> Dict[str, Any]:
        """Get current planetary transits"""
        try:
            now = datetime.now(timezone.utc)
            jd = self.calculate_julian_day(now, 0, 0)  # Use UTC coordinates
            
            current_planets = {}
            for planet_id, planet_name in self.PLANETS.items():
                try:
                    pos, _ = swe.calc_ut(jd, planet_id)
                    longitude_deg = pos[0]
                    
                    sign_index = int(longitude_deg // 30)
                    degree_in_sign = longitude_deg % 30
                    
                    current_planets[planet_name] = {
                        "longitude": longitude_deg,
                        "sign": self.SIGNS[sign_index],
                        "degree": degree_in_sign,
                        "formatted": f"{degree_in_sign:.1f}° {self.SIGNS[sign_index]}"
                    }
                except Exception as e:
                    logger.error(f"Transit calculation error for {planet_name}: {e}")
                    continue
            
            # Calculate transits to natal planets
            transits = []
            for transit_planet, transit_data in current_planets.items():
                for natal_planet, natal_data in natal_planets.items():
                    try:
                        transit_lon = transit_data["longitude"]
                        natal_lon = natal_data["longitude"]
                        
                        diff = abs(transit_lon - natal_lon)
                        if diff > 180:
                            diff = 360 - diff
                        
                        # Check for major transiting aspects
                        if diff <= 2:  # Conjunction
                            transits.append({
                                "transit_planet": transit_planet,
                                "natal_planet": natal_planet,
                                "aspect": "Conjunction",
                                "orb": diff
                            })
                        elif abs(diff - 180) <= 2:  # Opposition
                            transits.append({
                                "transit_planet": transit_planet,
                                "natal_planet": natal_planet,
                                "aspect": "Opposition",
                                "orb": abs(diff - 180)
                            })
                        elif abs(diff - 90) <= 2:  # Square
                            transits.append({
                                "transit_planet": transit_planet,
                                "natal_planet": natal_planet,
                                "aspect": "Square",
                                "orb": abs(diff - 90)
                            })
                        elif abs(diff - 120) <= 2:  # Trine
                            transits.append({
                                "transit_planet": transit_planet,
                                "natal_planet": natal_planet,
                                "aspect": "Trine",
                                "orb": abs(diff - 120)
                            })
                            
                    except Exception as e:
                        logger.error(f"Transit aspect calculation error: {e}")
                        continue
            
            return {
                "current_planets": current_planets,
                "transits": transits,
                "date": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Transit calculation error: {e}")
            return {}
    
    def get_daily_aspects(self, date: datetime) -> List[Dict[str, Any]]:
        """Get daily aspects for horoscope generation"""
        try:
            jd = self.calculate_julian_day(date, 0, 0)
            
            # Calculate planetary positions for the day
            planets = {}
            for planet_id, planet_name in self.PLANETS.items():
                try:
                    pos, _ = swe.calc_ut(jd, planet_id)
                    planets[planet_name] = pos[0]
                except Exception as e:
                    logger.error(f"Daily aspect calculation error for {planet_name}: {e}")
                    continue
            
            # Find aspects forming on this day
            aspects = []
            planet_names = list(planets.keys())
            
            for i, planet1 in enumerate(planet_names):
                for planet2 in planet_names[i+1:]:
                    try:
                        lon1 = planets[planet1]
                        lon2 = planets[planet2]
                        
                        diff = abs(lon1 - lon2)
                        if diff > 180:
                            diff = 360 - diff
                        
                        # Check for exact aspects (within 1 degree)
                        major_aspects = [0, 60, 90, 120, 180]
                        for aspect_angle in major_aspects:
                            if abs(diff - aspect_angle) <= 1:
                                aspect_names = {0: "Conjunction", 60: "Sextile", 90: "Square", 
                                              120: "Trine", 180: "Opposition"}
                                aspects.append({
                                    "planet1": planet1,
                                    "planet2": planet2,
                                    "aspect": aspect_names[aspect_angle],
                                    "orb": abs(diff - aspect_angle)
                                })
                                break
                                
                    except Exception as e:
                        logger.error(f"Daily aspect error for {planet1}-{planet2}: {e}")
                        continue
            
            return aspects
            
        except Exception as e:
            logger.error(f"Daily aspects calculation error: {e}")
            return []


# Global astrology service instance
astrology_service = AstrologyService()
