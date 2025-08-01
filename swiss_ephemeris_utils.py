#!/usr/bin/env python3
"""
Swiss Ephemeris utilities for planetary calculations with global timezone support
"""

import swisseph as swe
import datetime
import json
from global_timezone_utils import get_timezone_from_coordinates, get_timezone_offset

# Constants
EPHE_FILES = [
    'seas_18.se1',
    'sepl_18.se1', 
    'semo_18.se1'
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

RASIS = [
    "Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
    "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"
]

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury", "Ketu", "Venus",
    "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn",
    "Mercury", "Ketu", "Venus", "Sun", "Moon",
    "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

PLANET_NAMES = {
    0: "Sun", 1: "Moon", 2: "Mercury", 3: "Venus", 4: "Mars",
    5: "Jupiter", 6: "Saturn", 7: "Uranus", 8: "Neptune", 9: "Pluto"
}

def download_ephe_files():
    """Download ephemeris files (skipped due to 404 errors)"""
    print("Note: Using built-in Swiss Ephemeris calculations (ephemeris files not required for basic calculations)")
    # Skip actual downloads as URLs return 404
    pass

def setup_swiss_ephemeris():
    """Setup Swiss Ephemeris with Lahiri Ayanamsa"""
    try:
        # Set ephemeris path
        swe.set_ephe_path('ephe')
        
        # Set Lahiri Ayanamsa
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        print("Swiss Ephemeris path set to: ephe")
    except Exception as e:
        print(f"Error setting up Swiss Ephemeris: {e}")

def get_chart_info(longitude, speed=None):
    """
    Get chart information for a given longitude.
    Updated to match original OpenAI code and include nakshatra lords.
    """
    # Ensure longitude is within 0-360 range
    longitude = longitude % 360
    
    # Calculate rasi (sign)
    rasi_index = int(longitude // 30)
    rasi = RASIS[rasi_index]
    
    # Calculate nakshatra
    nakshatra_index = int(longitude // (360 / 27))
    nakshatra = NAKSHATRAS[nakshatra_index]
    nakshatra_lord = NAKSHATRA_LORDS[nakshatra_index]
    
    # Calculate pada
    pada = int(((longitude % (360 / 27)) / (360 / 27 / 4)) + 1)
    
    # Calculate degrees in rasi
    degrees_in_rasi = longitude % 30
    
    return {
        'longitude': longitude,
        'retrograde': speed < 0 if speed is not None else False,
        'rasi': rasi,
        'rasi_lord': get_rasi_lord(rasi),
        'nakshatra': nakshatra,
        'nakshatra_lord': nakshatra_lord,
        'pada': pada,
        'degrees_in_rasi': degrees_in_rasi
    }

def get_rasi_lord(rasi):
    """Get the lord of a rasi"""
    rasi_lords = {
        "Mesha": "Mars", "Rishaba": "Venus", "Mithuna": "Mercury",
        "Kataka": "Moon", "Simha": "Sun", "Kanni": "Mercury",
        "Thula": "Venus", "Vrischika": "Mars", "Dhanus": "Jupiter",
        "Makara": "Saturn", "Kumbha": "Saturn", "Meena": "Jupiter"
    }
    return rasi_lords.get(rasi, "Unknown")

def calculate_planetary_positions_global(date_of_birth, time_of_birth, latitude, longitude, timezone_name=None):
    """
    Calculate planetary positions with automatic timezone handling.
    
    Args:
        date_of_birth: Date object
        time_of_birth: Time object
        latitude: float (latitude of birth place)
        longitude: float (longitude of birth place)
        timezone_name: str (optional timezone name, e.g., 'Asia/Kolkata')
    
    Returns:
        dict: Planetary positions and chart information
    """
    try:
        # Setup Swiss Ephemeris
        setup_swiss_ephemeris()
        
        # Create datetime object (local time)
        local_dt = datetime.datetime.combine(date_of_birth, time_of_birth)
        
        # Handle timezone automatically
        import pytz
        
        if timezone_name:
            try:
                tz = pytz.timezone(timezone_name)
                local_dt = tz.localize(local_dt)
                utc_dt = local_dt.astimezone(pytz.UTC)
            except Exception as e:
                print(f"Error with timezone {timezone_name}: {e}")
                # Fallback to UTC
                timezone_name = 'UTC'
                tz = pytz.UTC
                local_dt = local_dt.replace(tzinfo=tz)
                utc_dt = local_dt
        else:
            # Detect timezone from coordinates
            try:
                timezone_name = get_timezone_from_coordinates(latitude, longitude)
                tz = pytz.timezone(timezone_name)
                local_dt = tz.localize(local_dt)
                utc_dt = local_dt.astimezone(pytz.UTC)
            except Exception as e:
                print(f"Error detecting timezone: {e}")
                # Fallback to UTC
                timezone_name = 'UTC'
                tz = pytz.UTC
                local_dt = local_dt.replace(tzinfo=tz)
                utc_dt = local_dt
        
        # Convert to Julian Day using UTC time
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                        utc_dt.hour + utc_dt.minute / 60.0)
        
        # Set topocentric coordinates
        swe.set_topo(longitude, latitude, 0)
        
        # Use sidereal coordinates for all calculations (Vedic astrology)
        SIDEREAL_FLAGS = swe.FLG_SIDEREAL | swe.FLG_SPEED
        
        results = {}
        
        # Calculate traditional 9 planets (Sun to Saturn) - excluding Uranus, Neptune, Pluto
        traditional_planets = [0, 1, 2, 3, 4, 5, 6]  # Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn
        for pid in traditional_planets:
            name = swe.get_planet_name(pid)
            # Use sidereal for all planets
            lonlat = swe.calc_ut(jd, pid, SIDEREAL_FLAGS)[0]
            results[name] = get_chart_info(lonlat[0], lonlat[3])
        
        # Calculate Rahu & Ketu (Lunar Nodes) - use sidereal
        rahu = swe.calc_ut(jd, swe.TRUE_NODE, SIDEREAL_FLAGS)[0]
        results['Rahu'] = get_chart_info(rahu[0], rahu[3])
        
        # Ketu is 180 degrees opposite to Rahu
        ketu_lon = (rahu[0] + 180.0) % 360.0
        ketu_info = get_chart_info(ketu_lon, rahu[3])
        ketu_info['retrograde'] = True  # Ketu is always retrograde
        results['Ketu'] = ketu_info
        
        # Calculate Ascendant - use sidereal
        cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'O', SIDEREAL_FLAGS)
        results['Ascendant'] = get_chart_info(ascmc[0])
        
        # Add house cusps
        house_cusps = []
        for i, cusp in enumerate(cusps[:12], 1):
            house_cusps.append({
                'house': i,
                'longitude': cusp,
                'rasi': RASIS[int(cusp // 30)]
            })
        results['House_Cusps'] = house_cusps
        
        # Add timezone metadata
        results['_metadata'] = {
            'timezone_name': timezone_name,
            'timezone_offset': local_dt.utcoffset().total_seconds() / 3600,
            'calculation_time': utc_dt.isoformat(),
            'local_time': local_dt.isoformat(),
            'julian_day': jd
        }
        
        return results
        
    except Exception as e:
        print(f"Error in calculate_planetary_positions_global: {e}")
        return {}

def calculate_planetary_positions(date_of_birth, time_of_birth, latitude, longitude, timezone_offset=5.5):
    """
    Legacy function for backward compatibility.
    Now uses global timezone detection.
    """
    return calculate_planetary_positions_global(date_of_birth, time_of_birth, latitude, longitude)

def format_planetary_positions(positions):
    """
    Format planetary positions for display.
    """
    formatted = {}
    
    for planet, info in positions.items():
        if planet == 'House_Cusps':
            formatted[planet] = info
            continue
            
        if planet == '_metadata':
            formatted[planet] = info
            continue
            
        formatted[planet] = {
            'longitude': round(info['longitude'], 6),
            'rasi': info['rasi'],
            'rasi_lord': info['rasi_lord'],
            'nakshatra': info['nakshatra'],
            'nakshatra_lord': info['nakshatra_lord'],
            'pada': info['pada'],
            'retrograde': info['retrograde'],
            'degrees_in_rasi': round(info['degrees_in_rasi'], 6)
        }
    
    return formatted

def get_planet_summary(positions):
    """
    Get a summary of planetary positions.
    """
    summary = []
    
    for planet, info in positions.items():
        if planet in ['House_Cusps', '_metadata']:
            continue
            
        summary.append(f"{planet}: {info['rasi']} ({info['nakshatra']})")
    
    return summary

def test_global_calculations():
    """
    Test global calculations with a sample birth chart.
    """
    print("🧪 Testing Global Planetary Calculations")
    print("=" * 50)
    
    # Test data: Chennai, 1978-09-18, 17:35
    date_of_birth = datetime.date(1978, 9, 18)
    time_of_birth = datetime.time(17, 35)
    latitude = 13.0843
    longitude = 80.2705
    timezone_name = "Asia/Calcutta"
    
    print(f"📍 Location: Chennai, India")
    print(f"📅 Date: {date_of_birth}")
    print(f"🕐 Time: {time_of_birth}")
    print(f"🌍 Timezone: {timezone_name}")
    
    # Calculate positions
    positions = calculate_planetary_positions_global(
        date_of_birth, time_of_birth, latitude, longitude, timezone_name
    )
    
    if positions:
        print("\n✅ Planetary Positions Calculated:")
        for planet, info in positions.items():
            if planet in ['House_Cusps', '_metadata']:
                continue
            print(f"  {planet}: {info['rasi']} ({info['nakshatra']}) - {info['longitude']:.2f}°")
        
        print(f"\n📊 Metadata: {positions.get('_metadata', {})}")
    else:
        print("❌ Failed to calculate planetary positions")

if __name__ == '__main__':
    test_global_calculations() 