#!/usr/bin/env python3
"""
Import charts from CSV export back into Supabase database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import environment_config
from supabase_config import supabase_manager
import csv
from datetime import datetime

def import_charts_from_csv(csv_file):
    """Import charts from CSV file into database"""

    if not supabase_manager:
        print("✗ Supabase not configured")
        return False

    charts_imported = 0
    charts_failed = 0

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                # Convert string booleans to actual booleans
                for key in row.keys():
                    if '_retrograde' in key:
                        row[key] = row[key] == 'Y'

                # Convert numeric fields
                numeric_fields = [
                    'latitude', 'longitude',
                    'sun_longitude', 'moon_longitude', 'mars_longitude', 'mercury_longitude',
                    'jupiter_longitude', 'venus_longitude', 'saturn_longitude', 'rahu_longitude',
                    'ketu_longitude', 'ascendant_longitude',
                    'sun_degrees_in_rasi', 'moon_degrees_in_rasi', 'mars_degrees_in_rasi',
                    'mercury_degrees_in_rasi', 'jupiter_degrees_in_rasi', 'venus_degrees_in_rasi',
                    'saturn_degrees_in_rasi', 'rahu_degrees_in_rasi', 'ketu_degrees_in_rasi',
                    'ascendant_degrees_in_rasi',
                    'house_1_longitude', 'house_2_longitude', 'house_3_longitude', 'house_4_longitude',
                    'house_5_longitude', 'house_6_longitude', 'house_7_longitude', 'house_8_longitude',
                    'house_9_longitude', 'house_10_longitude', 'house_11_longitude', 'house_12_longitude',
                    'house_1_degrees', 'house_2_degrees', 'house_3_degrees', 'house_4_degrees',
                    'house_5_degrees', 'house_6_degrees', 'house_7_degrees', 'house_8_degrees',
                    'house_9_degrees', 'house_10_degrees', 'house_11_degrees', 'house_12_degrees',
                    'sun_pada', 'moon_pada', 'mars_pada', 'mercury_pada', 'jupiter_pada',
                    'venus_pada', 'saturn_pada', 'rahu_pada', 'ketu_pada', 'ascendant_pada'
                ]

                for field in numeric_fields:
                    if field in row and row[field]:
                        row[field] = float(row[field])

                # Remove the id field (let Supabase generate it)
                if 'id' in row:
                    del row['id']

                # Remove empty strings
                data = {k: v if v != '' else None for k, v in row.items()}

                # Insert into database
                result = supabase_manager.supabase.table('birth_charts').insert(data).execute()

                print(f"✓ Imported: {row.get('name', 'Unknown')}")
                charts_imported += 1

            except Exception as e:
                print(f"✗ Failed to import {row.get('name', 'Unknown')}: {e}")
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
    success = import_charts_from_csv(csv_file)

    if success:
        print("\n✅ Import completed successfully!")
    else:
        print("\n❌ Import failed!")
        sys.exit(1)
