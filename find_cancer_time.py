#!/usr/bin/env python3
"""
Script to find the correct time for Cancer (Kadagam) Ascendant
Date: July 3, 2010
Place: Pleasanton, California
"""

import environment_config
from datetime import datetime, date, time
from swiss_ephemeris_utils import calculate_planetary_positions_global

def find_cancer_ascendant_time():
    """
    Find the time that gives Cancer (Kadagam) as Ascendant
    """
    print("🔍 Finding Cancer (Kadagam) Ascendant Time")
    print("=" * 50)
    
    # Test data
    test_date = date(2010, 7, 3)
    latitude = 37.6604484
    longitude = -121.8757968
    timezone_name = 'America/Los_Angeles'
    
    print(f"📍 Location: Pleasanton, California")
    print(f"📅 Date: {test_date}")
    print(f"🌐 Coordinates: {latitude}, {longitude}")
    print(f"⏰ Timezone: {timezone_name}")
    print()
    
    # Test different times to find Cancer Ascendant
    test_times = [
        time(6, 0),   # 6:00 AM
        time(7, 0),   # 7:00 AM
        time(8, 0),   # 8:00 AM
        time(9, 0),   # 9:00 AM
        time(10, 0),  # 10:00 AM
        time(11, 0),  # 11:00 AM
        time(12, 0),  # 12:00 PM
        time(13, 0),  # 1:00 PM
        time(14, 0),  # 2:00 PM
        time(15, 0),  # 3:00 PM
        time(16, 0),  # 4:00 PM
        time(17, 0),  # 5:00 PM
        time(18, 0),  # 6:00 PM
        time(19, 0),  # 7:00 PM
        time(20, 0),  # 8:00 PM
        time(21, 0),  # 9:00 PM
        time(22, 0),  # 10:00 PM
        time(23, 0),  # 11:00 PM
    ]
    
    cancer_times = []
    
    for test_time in test_times:
        try:
            positions = calculate_planetary_positions_global(
                date_of_birth=test_date,
                time_of_birth=test_time,
                latitude=latitude,
                longitude=longitude,
                timezone_name=timezone_name
            )
            
            if positions and 'Ascendant' in positions:
                ascendant = positions['Ascendant']
                rasi = ascendant.get('rasi', 'Unknown')
                longitude = ascendant.get('longitude', 0)
                
                print(f"🕐 {test_time.strftime('%H:%M')} - Ascendant: {rasi} ({longitude:.2f}°)")
                
                if rasi == 'Kataka':
                    cancer_times.append({
                        'time': test_time,
                        'longitude': longitude,
                        'positions': positions
                    })
                    print(f"   ✅ CANCER FOUND!")
        
        except Exception as e:
            print(f"❌ Error at {test_time}: {e}")
    
    print(f"\n🎯 RESULTS:")
    print("=" * 30)
    
    if cancer_times:
        print(f"✅ Found {len(cancer_times)} time(s) with Cancer Ascendant:")
        for i, result in enumerate(cancer_times, 1):
            print(f"   {i}. {result['time'].strftime('%H:%M')} - {result['longitude']:.2f}°")
            
            # Show detailed planetary positions for the first Cancer time
            if i == 1:
                positions = result['positions']
                print(f"\n🔮 Detailed Planetary Positions for {result['time'].strftime('%H:%M')}:")
                print("-" * 40)
                
                key_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu', 'Ascendant']
                for planet in key_planets:
                    if planet in positions:
                        planet_data = positions[planet]
                        print(f"{planet:12}: {planet_data['longitude']:8.2f}° - {planet_data['rasi']:10} - {planet_data['nakshatra']}")
    else:
        print("❌ No Cancer Ascendant found in the tested time range")
        print("   This might indicate the date/location combination doesn't have Cancer rising")
        print("   or we need to test different times")

def test_specific_time():
    """
    Test the original time (3:18 PM) and show why it's not Cancer
    """
    print(f"\n🔍 ANALYSIS OF 3:18 PM:")
    print("=" * 30)
    
    test_time = time(15, 18)  # 3:18 PM
    
    try:
        positions = calculate_planetary_positions_global(
            date_of_birth=date(2010, 7, 3),
            time_of_birth=test_time,
            latitude=37.6604484,
            longitude=-121.8757968,
            timezone_name='America/Los_Angeles'
        )
        
        if positions and 'Ascendant' in positions:
            ascendant = positions['Ascendant']
            longitude = ascendant.get('longitude', 0)
            rasi = ascendant.get('rasi', 'Unknown')
            
            print(f"   Time: {test_time.strftime('%H:%M')}")
            print(f"   Ascendant: {rasi} ({longitude:.2f}°)")
            
            # Cancer range is 90° to 120°
            if 90 <= longitude <= 120:
                print(f"   ✅ Longitude {longitude:.2f}° is within Cancer range (90°-120°)")
            else:
                print(f"   ❌ Longitude {longitude:.2f}° is outside Cancer range (90°-120°)")
                print(f"   Cancer range: 90° to 120°")
                print(f"   Current longitude: {longitude:.2f}°")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    find_cancer_ascendant_time()
    test_specific_time() 