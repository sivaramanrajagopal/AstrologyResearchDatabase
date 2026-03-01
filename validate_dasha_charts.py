#!/usr/bin/env python3
"""
Validate Dasha Calculator with Known Charts from Database (ID 16-29)
This script tests the Vimshottari Dasha implementation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import environment_config
from supabase_config import supabase_manager
from services.dasha_calculator import generate_dasa_table, get_current_dasa_bhukti, generate_dasa_bhukti_table
from datetime import datetime
import swisseph as swe

def main():
    print("=" * 100)
    print("DASHA CALCULATOR VALIDATION - Known Personality Charts (ID 16-29)")
    print("=" * 100)

    if not supabase_manager:
        print("✗ Supabase not configured")
        return

    swe.set_sid_mode(swe.SIDM_LAHIRI)

    validation_results = []
    successful_count = 0

    for chart_id in range(16, 30):  # IDs 16-29
        try:
            # Fetch chart from database
            chart_data = supabase_manager.supabase.table('birth_charts').select('*').eq('id', chart_id).execute()

            if not chart_data.data:
                print(f"\n⚠️  Chart ID {chart_id}: Not found in database")
                continue

            chart = chart_data.data[0]

            print(f"\n{'='*100}")
            print(f"CHART ID {chart_id}")
            print(f"{'='*100}")

            # Extract birth data
            dob_str = chart.get('date_of_birth')
            tob_str = chart.get('time_of_birth')
            place = chart.get('place_of_birth', 'Unknown')

            print(f"Date of Birth: {dob_str}")
            print(f"Time of Birth: {tob_str}")
            print(f"Place: {place}")

            # Parse datetime
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            try:
                tob = datetime.strptime(tob_str, '%H:%M').time()
            except:
                tob = datetime.strptime(tob_str, '%H:%M:%S').time()

            # Calculate Julian Day
            dt = datetime.combine(dob, tob)
            jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)

            # Get Moon longitude from database
            moon_lon = chart.get('moon_longitude')
            if moon_lon is None:
                print("✗ Moon longitude not available")
                continue

            print(f"Moon Longitude: {moon_lon:.6f}°")

            # Calculate Dasha periods
            birth_nakshatra, birth_pada, dasa_table = generate_dasa_table(jd, moon_lon, total_years=120)

            print(f"\nBirth Nakshatra: {birth_nakshatra}")
            print(f"Birth Pada: {pada}")

            # Get current Dasha/Bhukti
            current_info = get_current_dasa_bhukti(jd, moon_lon)

            print(f"\n📅 CURRENT DASHA/BHUKTI (as of {datetime.now().strftime('%Y-%m-%d')})")
            print(f"   Age: {current_info['age']:.2f} years")
            print(f"   Mahadasha: {current_info['current_dasa']}")
            print(f"   Antardasha (Bhukti): {current_info['current_bhukti']}")
            print(f"   Period: {current_info['start_date']} to {current_info['end_date']}")
            print(f"   Remaining: {current_info['remaining_years']:.2f} years")

            # Show Dasha sequence (first 10 periods)
            print(f"\n📋 DASHA SEQUENCE (First 10 Periods)")
            print(f"   {'Planet':<12} {'Start Age':<12} {'End Age':<12} {'Duration (yrs)':<15} {'Start Date':<12} {'End Date':<12}")
            print(f"   {'-'*85}")

            for i, period in enumerate(dasa_table[:10]):
                marker = " ➤" if period['planet'] == current_info['current_dasa'] else "  "
                print(f"{marker} {period['planet']:<12} {period['start_age']:<12.2f} {period['end_age']:<12.2f} {period['duration']:<15.2f} {period['start_date']:<12} {period['end_date']:<12}")

            # Calculate Bhukti table for current dasha
            _, _, bhukti_table = generate_dasa_bhukti_table(jd, moon_lon)

            # Filter for current mahadasha
            current_dasa_bhuktis = [b for b in bhukti_table if b['maha_dasa'] == current_info['current_dasa']]

            if current_dasa_bhuktis:
                print(f"\n📊 BHUKTI PERIODS IN CURRENT {current_info['current_dasa']} MAHADASHA")
                print(f"   {'Bhukti':<12} {'Start Date':<12} {'End Date':<12} {'Duration (yrs)':<15}")
                print(f"   {'-'*55}")

                for bhukti in current_dasa_bhuktis[:9]:  # Show all 9 bhuktis
                    marker = " ➤" if bhukti['bhukti'] == current_info['current_bhukti'] else "  "
                    print(f"{marker} {bhukti['bhukti']:<12} {bhukti['start_date']:<12} {bhukti['end_date']:<12} {bhukti['duration']:<15.2f}")

            validation_results.append({
                'chart_id': chart_id,
                'nakshatra': birth_nakshatra,
                'pada': birth_pada,
                'current_dasa': current_info['current_dasa'],
                'current_bhukti': current_info['current_bhukti'],
                'age': current_info['age'],
                'status': '✓ Success'
            })

            successful_count += 1
            print(f"\n✓ Dasha calculation successful for Chart ID {chart_id}")

        except Exception as e:
            print(f"\n✗ Error processing Chart ID {chart_id}: {e}")
            import traceback
            traceback.print_exc()
            validation_results.append({
                'chart_id': chart_id,
                'status': f'✗ Error: {str(e)[:100]}'
            })

    # Summary
    print(f"\n\n{'='*100}")
    print("VALIDATION SUMMARY")
    print(f"{'='*100}")
    print(f"Total Charts Processed: {len(validation_results)}")
    print(f"Successful: {successful_count}")
    print(f"Failed: {len(validation_results) - successful_count}")

    print(f"\n{'='*100}")
    print("RESULTS TABLE")
    print(f"{'='*100}")
    print(f"{'ID':<5} {'Nakshatra':<20} {'Pada':<6} {'Current Dasha':<15} {'Current Bhukti':<15} {'Age':<8} {'Status':<15}")
    print(f"{'-'*100}")

    for result in validation_results:
        print(f"{result.get('chart_id', 'N/A'):<5} "
              f"{result.get('nakshatra', 'N/A'):<20} "
              f"{result.get('pada', 'N/A'):<6} "
              f"{result.get('current_dasa', 'N/A'):<15} "
              f"{result.get('current_bhukti', 'N/A'):<15} "
              f"{result.get('age', 0):<8.2f} "
              f"{result.get('status', 'N/A'):<15}")

    print(f"\n{'='*100}")
    if successful_count == len(validation_results):
        print("✅ ALL VALIDATIONS PASSED!")
    elif successful_count > 0:
        print(f"⚠️  PARTIAL SUCCESS: {successful_count}/{len(validation_results)} charts validated")
    else:
        print("❌ ALL VALIDATIONS FAILED!")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    main()
