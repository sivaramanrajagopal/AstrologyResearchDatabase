#!/usr/bin/env python3
"""
Direct comparison between original and enhanced calculations
"""

import environment_config
from datetime import datetime, date, time
from swiss_ephemeris_utils import calculate_planetary_positions_global
from enhanced_swiss_ephemeris import calculate_enhanced_planetary_positions

def direct_comparison():
    """
    Direct comparison of calculations
    """
    print("🔍 Direct Calculation Comparison")
    print("=" * 40)
    
    # Test data
    date_of_birth = date(1978, 9, 18)
    time_of_birth = time(17, 35)  # 5:35 PM
    latitude = 13.08430070
    longitude = 80.27046220
    timezone_name = 'Asia/Calcutta'
    
    print(f"📅 Date: {date_of_birth}")
    print(f"🕐 Time: {time_of_birth}")
    print(f"📍 Location: Chennai, India")
    print()
    
    # Original calculation
    print("📊 ORIGINAL CALCULATION:")
    print("-" * 25)
    positions_orig = calculate_planetary_positions_global(
        date_of_birth, time_of_birth, latitude, longitude, timezone_name
    )
    
    if 'Moon' in positions_orig:
        moon_orig = positions_orig['Moon']
        print(f"Moon: {moon_orig['longitude']:.2f}° - {moon_orig['rasi']} - {moon_orig['nakshatra']} Pada {moon_orig['pada']}")
    
    if 'Ascendant' in positions_orig:
        asc_orig = positions_orig['Ascendant']
        print(f"Ascendant: {asc_orig['longitude']:.2f}° - {asc_orig['rasi']} - {asc_orig['nakshatra']}")
    
    print()
    
    # Enhanced calculation
    print("📊 ENHANCED CALCULATION:")
    print("-" * 25)
    positions_enh = calculate_enhanced_planetary_positions(
        date_of_birth, time_of_birth, latitude, longitude, timezone_name
    )
    
    if 'Moon' in positions_enh:
        moon_enh = positions_enh['Moon']
        print(f"Moon: {moon_enh['longitude']:.2f}° - {moon_enh['rasi']} - {moon_enh['nakshatra']} Pada {moon_enh['pada']}")
    
    if 'Ascendant' in positions_enh:
        asc_enh = positions_enh['Ascendant']
        print(f"Ascendant: {asc_enh['longitude']:.2f}° - {asc_enh['rasi']} - {asc_enh['nakshatra']}")
    
    print()
    
    # Compare Moon
    if 'Moon' in positions_orig and 'Moon' in positions_enh:
        moon_diff = abs(positions_orig['Moon']['longitude'] - positions_enh['Moon']['longitude'])
        print(f"🌙 Moon difference: {moon_diff:.2f}°")
        if moon_diff < 0.1:
            print("✅ Moon calculations match!")
        else:
            print("❌ Moon calculations differ!")
    
    # Compare Ascendant
    if 'Ascendant' in positions_orig and 'Ascendant' in positions_enh:
        asc_diff = abs(positions_orig['Ascendant']['longitude'] - positions_enh['Ascendant']['longitude'])
        print(f"🏠 Ascendant difference: {asc_diff:.2f}°")
        if asc_diff < 0.1:
            print("✅ Ascendant calculations match!")
        else:
            print("❌ Ascendant calculations differ!")

if __name__ == "__main__":
    direct_comparison() 