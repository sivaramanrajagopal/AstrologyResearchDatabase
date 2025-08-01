#!/usr/bin/env python3
"""
Find date/time that gives Moon at 357.30°
"""

import swisseph as swe
import datetime

def setup_swiss_ephemeris():
    """Setup Swiss Ephemeris"""
    swe.set_ephe_path('./ephe')
    swe.set_sid_mode(swe.SIDM_LAHIRI)  # Lahiri ayanamsa (Vedic)

def find_moon_357():
    """
    Find date/time that gives Moon at 357.30°
    """
    print("🔍 Finding Date/Time for Moon at 357.30°")
    print("=" * 50)
    
    # Setup Swiss Ephemeris
    setup_swiss_ephemeris()
    
    # Test different dates around 1990
    base_date = datetime.date(1990, 6, 15)
    
    print("Testing dates around June 15, 1990...")
    print()
    
    for day_offset in range(-7, 8):  # Test ±7 days
        test_date = base_date + datetime.timedelta(days=day_offset)
        
        for hour in range(0, 24, 2):  # Test every 2 hours
            test_time = datetime.time(hour, 0, 0)
            
            # Create datetime object
            local_dt = datetime.datetime.combine(test_date, test_time)
            
            # Convert to Julian Day
            jd = swe.julday(local_dt.year, local_dt.month, local_dt.day,
                            local_dt.hour + local_dt.minute / 60.0)
            
            # Set topocentric coordinates (Mumbai)
            swe.set_topo(72.8777, 19.076, 0)
            
            # Calculate Moon position
            FLAGS = swe.FLG_SIDEREAL | swe.FLG_SPEED
            moon_lonlat = swe.calc_ut(jd, 1, FLAGS)[0]  # 1 = Moon
            moon_longitude = moon_lonlat[0]
            
            # Check if close to 357.30°
            if abs(moon_longitude - 357.30) < 1.0:  # Within 1 degree
                print(f"🎯 Found! {test_date} {test_time} -> Moon: {moon_longitude:.2f}°")
                
                # Calculate nakshatra and pada
                nakshatras = [
                    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
                    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
                    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
                    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
                    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
                    "Revati"
                ]
                
                nakshatra_index = int((moon_longitude % 360) // (360 / 27))
                nakshatra = nakshatras[nakshatra_index]
                pada = int(((moon_longitude % (360 / 27)) / (360 / 27 / 4)) + 1)
                
                print(f"  Nakshatra: {nakshatra}")
                print(f"  Pada: {pada}")
                print()
    
    print("If no exact match found, the date/time in your app might be different.")
    print("Please provide the exact birth details from your app.")

if __name__ == "__main__":
    find_moon_357() 