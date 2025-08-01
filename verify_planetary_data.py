#!/usr/bin/env python3
"""
Verify planetary data for specific records
"""

import environment_config
from supabase_config import SupabaseManager

def verify_planetary_data():
    """
    Verify planetary data for specific records
    """
    print("🔍 Verifying Planetary Data for Specific Records")
    print("=" * 50)
    
    supabase_manager = SupabaseManager()
    
    try:
        charts = supabase_manager.get_all_charts()
        
        for chart in charts:
            print(f"\n📋 {chart['name']} (ID: {chart['id']}):")
            print(f"   📅 Date: {chart['date_of_birth']}")
            print(f"   🕐 Time: {chart['time_of_birth']}")
            print(f"   📍 Location: {chart['place_of_birth']}")
            
            # Check Moon data
            if 'moon_longitude' in chart and chart['moon_longitude'] is not None:
                moon_lon = chart['moon_longitude']
                moon_rasi = chart.get('moon_rasi', 'N/A')
                moon_nakshatra = chart.get('moon_nakshatra', 'N/A')
                moon_pada = chart.get('moon_pada', 'N/A')
                print(f"   🌙 Moon: {moon_lon:.2f}° - {moon_rasi} - {moon_nakshatra} Pada {moon_pada}")
            else:
                print(f"   🌙 Moon: ❌ Missing data")
            
            # Check Ascendant data
            if 'ascendant_longitude' in chart and chart['ascendant_longitude'] is not None:
                asc_lon = chart['ascendant_longitude']
                asc_rasi = chart.get('ascendant_rasi', 'N/A')
                asc_nakshatra = chart.get('ascendant_nakshatra', 'N/A')
                asc_pada = chart.get('ascendant_pada', 'N/A')
                print(f"   🏠 Ascendant: {asc_lon:.2f}° - {asc_rasi} - {asc_nakshatra} Pada {asc_pada}")
            else:
                print(f"   🏠 Ascendant: ❌ Missing data")
            
            # Check if enhanced data is present
            house_data_present = any(f'house_{i}_longitude' in chart and chart[f'house_{i}_longitude'] is not None for i in range(1, 13))
            yogas_present = 'yogas' in chart and chart['yogas'] is not None
            shadbala_present = 'shadbala' in chart and chart['shadbala'] is not None
            aspects_present = 'aspects' in chart and chart['aspects'] is not None
            
            print(f"   🏠 Houses: {'✅ Present' if house_data_present else '❌ Missing'}")
            print(f"   🧘 Yogas: {'✅ Present' if yogas_present else '❌ Missing'}")
            print(f"   ⚖️ Shadbala: {'✅ Present' if shadbala_present else '❌ Missing'}")
            print(f"   🔗 Aspects: {'✅ Present' if aspects_present else '❌ Missing'}")
            
            print("-" * 50)
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_planetary_data() 