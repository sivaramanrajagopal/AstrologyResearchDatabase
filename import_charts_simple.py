#!/usr/bin/env python3
"""
Import charts from CSV - simplified version that recalculates positions
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import environment_config
from supabase_config import supabase_manager
import csv

def import_charts_simple(csv_file):
    """Import charts from CSV - basic data only"""

    if not supabase_manager:
        print("✗ Supabase not configured")
        return False

    charts_imported = 0
    charts_failed = 0

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                # Extract only basic birth data
                data = {
                    'name': row.get('name'),
                    'gender': row.get('gender'),
                    'date_of_birth': row.get('date_of_birth'),
                    'time_of_birth': row.get('time_of_birth'),
                    'place_of_birth': row.get('place_of_birth'),
                    'latitude': float(row.get('latitude')),
                    'longitude': float(row.get('longitude')),
                    'timezone_name': row.get('timezone_name'),
                    'description': row.get('description') if row.get('description') else None,
                    'primary_category': row.get('primary_category') if row.get('primary_category') else None,
                    'sub_category': row.get('sub_category') if row.get('sub_category') else None,
                    'outcome': row.get('outcome') if row.get('outcome') else None,
                    'severity': row.get('severity') if row.get('severity') else None,
                    'timing': row.get('timing') if row.get('timing') else None,
                }

                # Add all planetary position data from CSV
                planets = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu']
                for planet in planets:
                    data[f'{planet}_longitude'] = float(row.get(f'{planet}_longitude', 0))
                    data[f'{planet}_rasi'] = row.get(f'{planet}_rasi')
                    data[f'{planet}_rasi_lord'] = row.get(f'{planet}_rasi_lord')
                    data[f'{planet}_nakshatra'] = row.get(f'{planet}_nakshatra')
                    data[f'{planet}_nakshatra_lord'] = row.get(f'{planet}_nakshatra_lord')
                    data[f'{planet}_pada'] = int(row.get(f'{planet}_pada', 0))
                    data[f'{planet}_degrees_in_rasi'] = float(row.get(f'{planet}_degrees_in_rasi', 0))
                    data[f'{planet}_retrograde'] = row.get(f'{planet}_retrograde') == 'Y'

                # Add ascendant data
                data['ascendant_longitude'] = float(row.get('ascendant_longitude', 0))
                data['ascendant_rasi'] = row.get('ascendant_rasi')
                data['ascendant_rasi_lord'] = row.get('ascendant_rasi_lord')
                data['ascendant_nakshatra'] = row.get('ascendant_nakshatra')
                data['ascendant_nakshatra_lord'] = row.get('ascendant_nakshatra_lord')
                data['ascendant_pada'] = int(row.get('ascendant_pada', 0))

                # Add house data
                for i in range(1, 13):
                    data[f'house_{i}_longitude'] = float(row.get(f'house_{i}_longitude', 0))
                    data[f'house_{i}_rasi'] = row.get(f'house_{i}_rasi')
                    data[f'house_{i}_degrees'] = float(row.get(f'house_{i}_degrees', 0))

                # Insert into database
                result = supabase_manager.supabase.table('birth_charts').insert(data).execute()

                print(f"✓ Imported: {row.get('name', 'Unknown')}")
                charts_imported += 1

            except Exception as e:
                print(f"✗ Failed to import {row.get('name', 'Unknown')}: {e}")
                import traceback
                traceback.print_exc()
                charts_failed += 1

    print(f"\n{'='*80}")
    print(f"Import Summary:")
    print(f"  Successfully imported: {charts_imported}")
    print(f"  Failed: {charts_failed}")
    print(f"{'='*80}")

    return charts_imported > 0

if __name__ == "__main__":
    csv_file = "exports/charts_added_2026-02-21.csv"

    if not os.path.exists(csv_file):
        print(f"✗ CSV file not found: {csv_file}")
        sys.exit(1)

    print(f"Importing charts from {csv_file}...")
    success = import_charts_simple(csv_file)

    if success:
        print("\n✅ Import completed successfully!")
    else:
        print("\n❌ Import failed!")
        sys.exit(1)
