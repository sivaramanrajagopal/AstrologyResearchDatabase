#!/usr/bin/env python3
"""
Export birth charts added today from Supabase to a CSV file.
Uses UTC date for 'today'. Run from project root:
  python3 scripts/export_today_charts_csv.py
Output: exports/charts_added_YYYY-MM-DD.csv
"""

import os
import sys
import csv
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import environment_config  # noqa: E402
from supabase_config import supabase_manager  # noqa: E402

# CSV columns: basic info + each planet (rasi, nakshatra, lord, degrees) + ascendant + houses summary
BASIC_COLS = [
    'id', 'name', 'gender', 'date_of_birth', 'time_of_birth', 'place_of_birth',
    'latitude', 'longitude', 'timezone_name', 'description', 'primary_category', 'sub_category',
    'outcome', 'severity', 'timing', 'created_at', 'updated_at'
]
PLANETS = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu']
PLANET_COLS = []
for p in PLANETS:
    PLANET_COLS.extend([f'{p}_longitude', f'{p}_rasi', f'{p}_rasi_lord', f'{p}_nakshatra', f'{p}_nakshatra_lord', f'{p}_pada', f'{p}_degrees_in_rasi', f'{p}_retrograde'])
ASC_COLS = ['ascendant_longitude', 'ascendant_rasi', 'ascendant_rasi_lord', 'ascendant_nakshatra', 'ascendant_nakshatra_lord', 'ascendant_pada', 'ascendant_degrees_in_rasi']
HOUSE_COLS = []
for i in range(1, 13):
    HOUSE_COLS.extend([f'house_{i}_longitude', f'house_{i}_rasi', f'house_{i}_degrees'])
ALL_COLS = BASIC_COLS + PLANET_COLS + ASC_COLS + HOUSE_COLS


def safe_val(v):
    if v is None:
        return ''
    if isinstance(v, bool):
        return 'Y' if v else 'N'
    if isinstance(v, (dict, list)):
        return str(v)[:500]  # truncate JSON
    return str(v)


def main():
    if not supabase_manager:
        print("Supabase not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY.")
        sys.exit(1)
    # Use UTC today, or optional date from args: YYYY-MM-DD
    if len(sys.argv) >= 2:
        try:
            today = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
        except ValueError:
            print("Usage: python3 scripts/export_today_charts_csv.py [YYYY-MM-DD]")
            sys.exit(1)
    else:
        today = datetime.now(timezone.utc).date()
    charts = supabase_manager.get_charts_created_on_date(today)
    if not charts:
        print(f"No charts found created on {today} (UTC).")
        print("Tip: Pass a date: python3 scripts/export_today_charts_csv.py 2025-02-21")
        sys.exit(0)
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'exports')
    os.makedirs(out_dir, exist_ok=True)
    filename = os.path.join(out_dir, f'charts_added_{today.isoformat()}.csv')
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(ALL_COLS)
        for row in charts:
            w.writerow([safe_val(row.get(c)) for c in ALL_COLS])
    print(f"Exported {len(charts)} chart(s) to {filename}")
    return filename


if __name__ == '__main__':
    main()
