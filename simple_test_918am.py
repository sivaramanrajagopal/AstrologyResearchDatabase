#!/usr/bin/env python3
"""
Simple test for 9:18 AM calculations without timezonefinder dependency
"""

import environment_config
from datetime import datetime, date, time
import pyswisseph as swe

def test_918am():
    """
    Test calculations for July 3, 2010, 9:18 AM, Pleasanton, CA
    """
    print("🔮 Testing 9:18 AM Calculations")
    print("=" * 50)
    
    # Test data
    test_date = date(2010, 7, 3)
    test_time = time(9, 18)  # 9:18 AM
    latitude = 37.6604484
    longitude = -121.8757968
    timezone_name = 'America/Los_Angeles'
    
    print(f"📍 Location: Pleasanton, California")
    print(f"📅 Date: {test_date}")
    print(f"🕐 Time: {test_time}")
    print(f"🌐 Coordinates: {latitude}, {longitude}")
    print(f"⏰ Timezone: {timezone_name}")
    print()
    
    try:
        # Setup Swiss Ephemeris
        swe.set_ephe_path('ephe')
        
        # Create datetime object (local time)
        local_dt = datetime.combine(test_date, test_time)
        
        # Handle timezone
        import pytz
        tz = pytz.timezone(timezone_name)
        local_dt = tz.localize(local_dt)
        utc_dt = local_dt.astimezone(pytz.UTC)
        
        # Convert to Julian Day using UTC time
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                        utc_dt.hour + utc_dt.minute / 60.0)
        
        # Set topocentric coordinates
        swe.set_topo(longitude, latitude, 0)
        
        # Use sidereal coordinates for all calculations (Vedic astrology)
        SIDEREAL_FLAGS = swe.FLG_SIDEREAL | swe.FLG_SPEED
        
        # Calculate Ascendant
        cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'O', SIDEREAL_FLAGS)
        ascendant_longitude = ascmc[0]
        
        # Determine Rasi
        rasis = ["Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni", 
                "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"]
        rasi_index = int(ascendant_longitude // 30)
        rasi = rasis[rasi_index]
        
        # Determine Nakshatra
        nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
                     "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
                     "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
                     "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
                     "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
        nakshatra_index = int(ascendant_longitude // (360 / 27))
        nakshatra = nakshatras[nakshatra_index]
        
        # Calculate pada
        pada = int(((ascendant_longitude % (360 / 27)) / (360 / 27 / 4)) + 1)
        
        print("🔮 CALCULATION RESULTS:")
        print("-" * 30)
        print(f"Ascendant Longitude: {ascendant_longitude:.2f}°")
        print(f"Rasi: {rasi}")
        print(f"Nakshatra: {nakshatra}")
        print(f"Pada: {pada}")
        print()
        
        # Check if it's Cancer
        if rasi == "Kataka":
            print("✅ SUCCESS: Lagna is Kadagam (Cancer) as expected!")
        else:
            print(f"❌ Lagna is {rasi}, expected Kadagam (Cancer)")
        
        # Cancer range verification
        cancer_start = 90.0
        cancer_end = 120.0
        
        print(f"\n🦀 CANCER RANGE VERIFICATION:")
        print(f"   Cancer (Kataka) range: {cancer_start}° to {cancer_end}°")
        print(f"   Ascendant longitude: {ascendant_longitude:.2f}°")
        
        if cancer_start <= ascendant_longitude <= cancer_end:
            print(f"   ✅ Longitude {ascendant_longitude:.2f}° is within Cancer range!")
        else:
            print(f"   ❌ Longitude {ascendant_longitude:.2f}° is outside Cancer range")
        
        # Metadata
        print(f"\n📊 METADATA:")
        print(f"   Timezone: {timezone_name}")
        print(f"   Local Time: {local_dt.isoformat()}")
        print(f"   UTC Time: {utc_dt.isoformat()}")
        print(f"   Julian Day: {jd:.6f}")
        
    except Exception as e:
        print(f"❌ Error in calculation: {e}")

if __name__ == "__main__":
    test_918am() 