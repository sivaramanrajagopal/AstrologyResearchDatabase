#!/usr/bin/env python3
"""
Enhanced Swiss Ephemeris Utilities for Vedic Astrology
Based on CleanAstroApp repository features
"""

import swisseph as swe
from datetime import datetime, date, time
import pytz
import json
from typing import Dict, List, Tuple, Optional
from swiss_ephemeris_utils import get_chart_info

# Set Swiss Ephemeris path
swe.set_ephe_path('ephe')

# Rasi (Zodiac Signs) definitions
RASIS = [
    "Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
    "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"
]

# Nakshatras
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Nakshatra Lords
NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun",
    "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury"
]

# Rasi Lords
RASI_LORDS = {
    "Mesha": "Mars", "Rishaba": "Venus", "Mithuna": "Mercury",
    "Kataka": "Moon", "Simha": "Sun", "Kanni": "Mercury",
    "Thula": "Venus", "Vrischika": "Mars", "Dhanus": "Jupiter",
    "Makara": "Saturn", "Kumbha": "Saturn", "Meena": "Jupiter"
}

# House names
HOUSES = [
    "1st House (Lagna)", "2nd House", "3rd House", "4th House", 
    "5th House", "6th House", "7th House", "8th House",
    "9th House", "10th House", "11th House", "12th House"
]

def get_rasi_from_longitude(longitude: float) -> str:
    """Get rasi from longitude"""
    rasi_index = int(longitude / 30)
    return RASIS[rasi_index]

def get_nakshatra_from_longitude(longitude: float) -> str:
    """Get nakshatra from longitude"""
    nakshatra_index = int(longitude / (360 / 27))
    return NAKSHATRAS[nakshatra_index]

def get_nakshatra_lord(nakshatra: str) -> str:
    """Get lord of nakshatra"""
    if nakshatra in NAKSHATRAS:
        index = NAKSHATRAS.index(nakshatra)
        return NAKSHATRA_LORDS[index]
    return "Unknown"

def get_rasi_lord(rasi: str) -> str:
    """Get lord of rasi"""
    return RASI_LORDS.get(rasi, "Unknown")

def calculate_house_positions(jd: float, latitude: float, longitude: float) -> Dict:
    """Calculate house cusps and positions"""
    try:
        # Calculate house cusps using Placidus system
        cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'P', swe.FLG_SIDEREAL)
        
        houses = {}
        for i in range(12):
            house_longitude = cusps[i]
            houses[f"House_{i+1}"] = {
                'longitude': house_longitude,
                'rasi': get_rasi_from_longitude(house_longitude),
                'degrees_in_rasi': house_longitude % 30
            }
        
        return houses
    except Exception as e:
        print(f"Error calculating houses: {e}")
        return {}

def calculate_yogas(planetary_positions: Dict) -> List[Dict]:
    """Calculate important yogas"""
    yogas = []
    
    # Get planetary positions
    sun = planetary_positions.get('Sun', {})
    moon = planetary_positions.get('Moon', {})
    mars = planetary_positions.get('Mars', {})
    mercury = planetary_positions.get('Mercury', {})
    jupiter = planetary_positions.get('Jupiter', {})
    venus = planetary_positions.get('Venus', {})
    saturn = planetary_positions.get('Saturn', {})
    
    # Check for important yogas
    if sun and moon:
        # Sun-Moon conjunction (Amavasya)
        sun_moon_diff = abs(sun['longitude'] - moon['longitude'])
        if sun_moon_diff < 10:  # Within 10 degrees
            yogas.append({
                'name': 'Amavasya (New Moon)',
                'type': 'Conjunction',
                'planets': ['Sun', 'Moon'],
                'description': 'New Moon conjunction - powerful for spiritual practices'
            })
        elif 170 < sun_moon_diff < 190:  # Opposition
            yogas.append({
                'name': 'Purnima (Full Moon)',
                'type': 'Opposition',
                'planets': ['Sun', 'Moon'],
                'description': 'Full Moon opposition - good for material pursuits'
            })
    
    # Check for planetary combinations
    if jupiter and venus:
        jup_ven_diff = abs(jupiter['longitude'] - venus['longitude'])
        if jup_ven_diff < 5:  # Within 5 degrees
            yogas.append({
                'name': 'Guru-Venus Conjunction',
                'type': 'Benefic Conjunction',
                'planets': ['Jupiter', 'Venus'],
                'description': 'Highly auspicious for education, arts, and relationships'
            })
    
    if mars and saturn:
        mar_sat_diff = abs(mars['longitude'] - saturn['longitude'])
        if mar_sat_diff < 5:
            yogas.append({
                'name': 'Mars-Saturn Conjunction',
                'type': 'Challenging Conjunction',
                'planets': ['Mars', 'Saturn'],
                'description': 'Can indicate challenges and obstacles'
            })
    
    return yogas

def calculate_shadbala(planetary_positions: Dict, houses: Dict) -> Dict:
    """Calculate Shadbala (Six-fold strength) for planets"""
    shadbala = {}
    
    for planet_name, planet_data in planetary_positions.items():
        if planet_name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            # Basic Shadbala calculation (simplified)
            strength = 0
            
            # 1. Sthana Bala (Positional Strength)
            rasi = planet_data.get('rasi', '')
            if rasi:
                # Exaltation and debilitation points
                exaltation_points = {
                    'Sun': 10, 'Moon': 33, 'Mars': 298, 'Mercury': 165,
                    'Jupiter': 95, 'Venus': 357, 'Saturn': 200
                }
                debilitation_points = {
                    'Sun': 190, 'Moon': 213, 'Mars': 118, 'Mercury': 345,
                    'Jupiter': 275, 'Venus': 177, 'Saturn': 20
                }
                
                planet_longitude = planet_data['longitude']
                exaltation_point = exaltation_points.get(planet_name, 0)
                debilitation_point = debilitation_points.get(planet_name, 0)
                
                # Calculate distance from exaltation/debilitation
                exaltation_distance = abs(planet_longitude - exaltation_point)
                debilitation_distance = abs(planet_longitude - debilitation_point)
                
                if exaltation_distance < 10:
                    strength += 2  # Exalted
                elif debilitation_distance < 10:
                    strength -= 1  # Debilitated
                else:
                    strength += 0.5  # Neutral
            
            # 2. Dik Bala (Directional Strength)
            # Simplified directional strength
            if planet_name in ['Sun', 'Mars']:
                strength += 0.5  # Natural benefics in certain positions
            
            # 3. Kala Bala (Temporal Strength)
            # Simplified temporal strength
            strength += 0.3  # Base temporal strength
            
            shadbala[planet_name] = {
                'total_strength': round(strength, 2),
                'status': 'Strong' if strength > 1 else 'Weak' if strength < 0 else 'Moderate'
            }
    
    return shadbala

def calculate_aspects(planetary_positions: Dict) -> List[Dict]:
    """Calculate planetary aspects"""
    aspects = []
    
    planets = list(planetary_positions.keys())
    
    for i, planet1 in enumerate(planets):
        for planet2 in planets[i+1:]:
            if planet1 in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'] and \
               planet2 in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
                
                pos1 = planetary_positions[planet1]['longitude']
                pos2 = planetary_positions[planet2]['longitude']
                
                # Calculate angular distance
                distance = abs(pos1 - pos2)
                if distance > 180:
                    distance = 360 - distance
                
                # Check for aspects
                if distance < 10:  # Conjunction
                    aspects.append({
                        'type': 'Conjunction',
                        'planets': [planet1, planet2],
                        'distance': round(distance, 2),
                        'description': f'{planet1} and {planet2} in conjunction'
                    })
                elif 60 - 5 <= distance <= 60 + 5:  # Sextile
                    aspects.append({
                        'type': 'Sextile',
                        'planets': [planet1, planet2],
                        'distance': round(distance, 2),
                        'description': f'{planet1} and {planet2} in sextile aspect'
                    })
                elif 90 - 5 <= distance <= 90 + 5:  # Square
                    aspects.append({
                        'type': 'Square',
                        'planets': [planet1, planet2],
                        'distance': round(distance, 2),
                        'description': f'{planet1} and {planet2} in square aspect'
                    })
                elif 120 - 5 <= distance <= 120 + 5:  # Trine
                    aspects.append({
                        'type': 'Trine',
                        'planets': [planet1, planet2],
                        'distance': round(distance, 2),
                        'description': f'{planet1} and {planet2} in trine aspect'
                    })
                elif 180 - 5 <= distance <= 180 + 5:  # Opposition
                    aspects.append({
                        'type': 'Opposition',
                        'planets': [planet1, planet2],
                        'distance': round(distance, 2),
                        'description': f'{planet1} and {planet2} in opposition'
                    })
    
    return aspects

def calculate_enhanced_planetary_positions(date_of_birth: date, time_of_birth: time, 
                                        latitude: float, longitude: float, 
                                        timezone_name: str = None) -> Dict:
    """
    Calculate enhanced planetary positions with houses, yogas, and Shadbala
    """
    try:
        # Setup Swiss Ephemeris (matching original calculation)
        from swiss_ephemeris_utils import setup_swiss_ephemeris
        setup_swiss_ephemeris()
        
        # Create datetime object
        local_dt = datetime.combine(date_of_birth, time_of_birth)
        
        # Handle timezone
        import pytz
        
        if timezone_name:
            try:
                tz = pytz.timezone(timezone_name)
                local_dt = tz.localize(local_dt)
                utc_dt = local_dt.astimezone(pytz.UTC)
            except Exception as e:
                print(f"Error with timezone {timezone_name}: {e}")
                # Fallback to UTC
                utc_dt = local_dt.replace(tzinfo=pytz.UTC)
        else:
            # Fallback to UTC
            utc_dt = local_dt.replace(tzinfo=pytz.UTC)
        
        # Convert to Julian Day (matching original calculation)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                     utc_dt.hour + utc_dt.minute/60.0)
        
        # Set location
        swe.set_topo(longitude, latitude, 0)
        
        # Use sidereal coordinates for all calculations
        SIDEREAL_FLAGS = swe.FLG_SIDEREAL | swe.FLG_SPEED
        
        # Calculate planetary positions (matching original order)
        traditional_planets = [0, 1, 2, 3, 4, 5, 6]  # Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn
        
        results = {}
        
        for pid in traditional_planets:
            name = swe.get_planet_name(pid)
            lonlat = swe.calc_ut(jd, pid, SIDEREAL_FLAGS)[0]
            
            planet_longitude = lonlat[0]
            speed = lonlat[3]
            
            # Calculate rasi and nakshatra
            rasi = get_rasi_from_longitude(planet_longitude)
            nakshatra = get_nakshatra_from_longitude(planet_longitude)
            nakshatra_lord = get_nakshatra_lord(nakshatra)
            
            # Calculate pada
            pada = int(((planet_longitude % (360 / 27)) / (360 / 27 / 4)) + 1)
            
            # Calculate degrees in rasi
            degrees_in_rasi = planet_longitude % 30
            
            results[name] = {
                'longitude': planet_longitude,
                'retrograde': speed < 0 if speed is not None else False,
                'rasi': rasi,
                'rasi_lord': get_rasi_lord(rasi),
                'nakshatra': nakshatra,
                'nakshatra_lord': nakshatra_lord,
                'pada': pada,
                'degrees_in_rasi': degrees_in_rasi
            }
        
        # Calculate Rahu and Ketu (matching original calculation)
        rahu_lonlat = swe.calc_ut(jd, swe.TRUE_NODE, SIDEREAL_FLAGS)[0]
        rahu_info = {
            'longitude': rahu_lonlat[0],
            'retrograde': rahu_lonlat[3] < 0 if rahu_lonlat[3] is not None else False,
            'rasi': get_rasi_from_longitude(rahu_lonlat[0]),
            'rasi_lord': get_rasi_lord(get_rasi_from_longitude(rahu_lonlat[0])),
            'nakshatra': get_nakshatra_from_longitude(rahu_lonlat[0]),
            'nakshatra_lord': get_nakshatra_lord(get_nakshatra_from_longitude(rahu_lonlat[0])),
            'pada': int(((rahu_lonlat[0] % (360 / 27)) / (360 / 27 / 4)) + 1),
            'degrees_in_rasi': rahu_lonlat[0] % 30
        }
        results['Rahu'] = rahu_info
        
        # Ketu is opposite to Rahu
        ketu_longitude = (rahu_lonlat[0] + 180) % 360
        ketu_info = {
            'longitude': ketu_longitude,
            'retrograde': rahu_info['retrograde'],
            'rasi': get_rasi_from_longitude(ketu_longitude),
            'rasi_lord': get_rasi_lord(get_rasi_from_longitude(ketu_longitude)),
            'nakshatra': get_nakshatra_from_longitude(ketu_longitude),
            'nakshatra_lord': get_nakshatra_lord(get_nakshatra_from_longitude(ketu_longitude)),
            'pada': int(((ketu_longitude % (360 / 27)) / (360 / 27 / 4)) + 1),
            'degrees_in_rasi': ketu_longitude % 30
        }
        results['Ketu'] = ketu_info
        
        # Calculate Ascendant (matching original calculation)
        cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'O', SIDEREAL_FLAGS)
        results['Ascendant'] = get_chart_info(ascmc[0])
        
        # Calculate house positions
        houses = calculate_house_positions(jd, latitude, longitude)
        
        # Calculate yogas
        yogas = calculate_yogas(results)
        
        # Calculate Shadbala
        shadbala = calculate_shadbala(results, houses)
        
        # Calculate aspects
        aspects = calculate_aspects(results)
        
        # Add metadata
        results['_metadata'] = {
            'timezone_name': timezone_name,
            'timezone_offset': local_dt.utcoffset().total_seconds() / 3600,
            'calculation_time': utc_dt.isoformat(),
            'local_time': local_dt.isoformat(),
            'julian_day': jd
        }
        
        # Add enhanced features
        results['_enhanced'] = {
            'houses': houses,
            'yogas': yogas,
            'shadbala': shadbala,
            'aspects': aspects
        }
        
        return results
        
    except Exception as e:
        print(f"Error in calculate_enhanced_planetary_positions: {e}")
        return None

def extract_enhanced_planetary_data(planetary_positions: Dict) -> Dict:
    """Extract planetary data for database storage"""
    if not planetary_positions:
        return {}
    
    data = {}
    
    # Extract individual planetary positions
    for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu', 'Ascendant']:
        if planet in planetary_positions:
            planet_data = planetary_positions[planet]
            data[f'{planet.lower()}_longitude'] = planet_data['longitude']
            data[f'{planet.lower()}_rasi'] = planet_data['rasi']
            data[f'{planet.lower()}_rasi_lord'] = planet_data['rasi_lord']
            data[f'{planet.lower()}_nakshatra'] = planet_data['nakshatra']
            data[f'{planet.lower()}_nakshatra_lord'] = planet_data['nakshatra_lord']
            data[f'{planet.lower()}_pada'] = planet_data['pada']
            data[f'{planet.lower()}_degrees_in_rasi'] = planet_data['degrees_in_rasi']
            data[f'{planet.lower()}_retrograde'] = planet_data['retrograde']
    
    # Extract house positions
    if '_enhanced' in planetary_positions and 'houses' in planetary_positions['_enhanced']:
        houses = planetary_positions['_enhanced']['houses']
        for i in range(1, 13):
            house_key = f'House_{i}'
            if house_key in houses:
                house_data = houses[house_key]
                data[f'house_{i}_longitude'] = house_data['longitude']
                data[f'house_{i}_rasi'] = house_data['rasi']
                data[f'house_{i}_degrees'] = house_data['degrees_in_rasi']
    
    # Store yogas as JSON
    if '_enhanced' in planetary_positions and 'yogas' in planetary_positions['_enhanced']:
        data['yogas'] = json.dumps(planetary_positions['_enhanced']['yogas'])
    
    # Store Shadbala as JSON
    if '_enhanced' in planetary_positions and 'shadbala' in planetary_positions['_enhanced']:
        data['shadbala'] = json.dumps(planetary_positions['_enhanced']['shadbala'])
    
    # Store aspects as JSON
    if '_enhanced' in planetary_positions and 'aspects' in planetary_positions['_enhanced']:
        data['aspects'] = json.dumps(planetary_positions['_enhanced']['aspects'])
    
    return data 