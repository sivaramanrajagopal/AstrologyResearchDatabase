#!/usr/bin/env python3
"""
Add notable profiles one by one with gender confirmation before each insert.
Run from project root: python scripts/add_profiles_with_gender_confirm.py
"""

import os
import sys
from datetime import datetime, date, time

# Run from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import environment_config  # noqa: E402
from utils.geocoding import get_location_details  # noqa: E402
from enhanced_swiss_ephemeris import (  # noqa: E402
    calculate_enhanced_planetary_positions,
    extract_enhanced_planetary_data,
)
from supabase_config import supabase_manager  # noqa: E402

# Profile: (name, role/description, date_str, time_str, place_for_geocode, assumed_gender)
PROFILES = [
    ("Satya Nadella", "Microsoft CEO", "1967-08-19", "12:00", "Hyderabad, Telangana, India", "male"),
    ("Narendra Modi", "PM India", "1950-09-17", "11:00", "Vadnagar, Gujarat, India", "male"),
    ("Indra Nooyi", "PepsiCo ex-CEO", "1955-10-28", "21:26", "Chennai, Tamil Nadu, India", "female"),
    ("Shantanu Narayen", "Adobe CEO", "1963-05-23", "10:30", "Hyderabad, Telangana, India", "male"),
    ("N. Chandrasekaran", "Tata Sons Chairman", "1953-06-02", "09:15", "Thanjavur, Tamil Nadu, India", "male"),
    ("Salil Parekh", "Infosys CEO", "1962-01-15", "12:00", "Mumbai, Maharashtra, India", "male"),
    ("Kiran Mazumdar-Shaw", "Biocon CMD", "1953-03-23", "10:45", "Bangalore, Karnataka, India", "female"),
    ("APJ Abdul Kalam", "President/Scientist", "1931-10-15", "03:40", "Rameswaram, Tamil Nadu, India", "male"),
    ("Vikram Sarabhai", "ISRO Founder", "1919-08-12", "02:00", "Ahmedabad, Gujarat, India", "male"),
    ("E. Sreedharan", "Metro Man", "1932-06-12", "06:30", "Palakkad, Kerala, India", "male"),
    ("Roman Saini", "IAS Collector", "1991-07-30", "03:15", "Jaipur, Rajasthan, India", "male"),
    ("Durga Shakti Nagpal", "IAS DM", "1985-07-17", "14:20", "Noida, Uttar Pradesh, India", "female"),
    ("Letika Karwal", "DGP Uttarakhand", "1964-03-22", "10:30", "Dehradun, Uttarakhand, India", "female"),
    ("Dr. Devi Shetty", "Cardio Surgeon", "1953-05-08", "10:30", "Mangalore, Karnataka, India", "male"),
]

# Batch 2: Business & cinema (all male)
PROFILES_BATCH2 = [
    ("Mukesh Ambani", "Reliance Chairman", "1957-04-19", "19:53", "Aden, Yemen", "male"),
    ("Ratan Tata", "Tata Sons ex-Chairman", "1937-12-28", "22:25", "Mumbai, Maharashtra, India", "male"),
    ("N.R. Narayana Murthy", "Infosys Founder", "1946-08-20", "12:05", "Kolar, Karnataka, India", "male"),
    ("Shiv Nadar", "HCL Founder", "1945-07-14", "04:15", "Moolaipozhi, Tamil Nadu, India", "male"),
    ("Azim Premji", "Wipro Chairman", "1945-07-24", "12:00", "Mumbai, Maharashtra, India", "male"),
    ("Gautam Adani", "Adani Group", "1962-06-24", "08:25", "Ahmedabad, Gujarat, India", "male"),
    ("Dhirubhai Ambani", "Reliance Founder", "1932-12-28", "06:37", "Veraval, Gujarat, India", "male"),
    ("Rajinikanth", "Cinema Business", "1950-12-12", "11:35", "Bangalore, Karnataka, India", "male"),
    ("A.R. Rahman", "Music Business", "1967-01-06", "03:30", "Chennai, Tamil Nadu, India", "male"),
    ("Kamal Haasan", "Cinema Business", "1954-11-07", "06:30", "Paramakudi, Tamil Nadu, India", "male"),
    ("Anand Mahindra", "Mahindra Group", "1955-05-01", "00:01", "Mumbai, Maharashtra, India", "male"),
    ("Kumar Mangalam Birla", "Aditya Birla", "1967-06-14", "09:30", "Kolkata, West Bengal, India", "male"),
    ("Cyrus Poonawalla", "Serum Institute", "1948-06-20", "11:45", "Pune, Maharashtra, India", "male"),
    ("Uday Kotak", "Kotak Mahindra", "1959-03-15", "10:20", "Mumbai, Maharashtra, India", "male"),
    ("S.D. Shibulal", "Infosys Co-founder", "1955-03-01", "10:45", "Thrissur, Kerala, India", "male"),
]


def parse_time(tstr):
    """Parse HH:MM or HH:MM:SS to time."""
    tstr = tstr.strip()
    if len(tstr) == 5:  # HH:MM
        return datetime.strptime(tstr, "%H:%M").time()
    return datetime.strptime(tstr, "%H:%M:%S").time()


def add_one(idx, name, role, date_str, time_str, place, assumed_gender, skip_confirm=False):
    """Show gender, get confirmation (unless skip_confirm), then add profile to DB."""
    print("\n" + "=" * 60)
    print(f"Profile {idx}: {name}")
    print(f"  Role: {role}")
    print(f"  DOB: {date_str}  Time: {time_str}  Place: {place}")
    print(f"  Gender (backend): {assumed_gender}")
    print("=" * 60)
    if skip_confirm:
        gender = assumed_gender
    else:
        confirm = input("Confirm gender? (y = use above, or type 'male'/'female' to correct): ").strip().lower()
        if not confirm:
            print("Skipped (empty input).")
            return False
        if confirm in ("male", "female"):
            gender = confirm
        elif confirm == "y" or confirm == "yes":
            gender = assumed_gender
        else:
            print("Skipped (invalid input).")
            return False

    # Parse date/time
    dob = datetime.strptime(date_str, "%Y-%m-%d").date()
    try:
        tot = parse_time(time_str)
    except Exception:
        tot = datetime.strptime(time_str.strip(), "%H:%M").time()

    # Geocode
    print("  Geocoding...")
    location_details = get_location_details(place)
    if not location_details:
        print("  ERROR: Could not geocode place.")
        return False
    print(f"  -> {location_details.get('latitude')}, {location_details.get('longitude')}")

    # Planetary positions
    print("  Calculating chart...")
    planetary_positions = calculate_enhanced_planetary_positions(
        date_of_birth=dob,
        time_of_birth=tot,
        latitude=location_details["latitude"],
        longitude=location_details["longitude"],
        timezone_name=location_details.get("timezone_id"),
    )
    if not planetary_positions:
        print("  ERROR: Chart calculation failed.")
        return False

    chart_data = {
        "name": name,
        "gender": gender,
        "date_of_birth": dob.isoformat(),
        "time_of_birth": tot.isoformat(),
        "place_of_birth": place,
        "latitude": location_details["latitude"],
        "longitude": location_details["longitude"],
        "timezone_name": location_details.get("timezone_id", "UTC"),
        "primary_category": "career",
        "sub_category": "leadership",
        "specific_condition": None,
        "description": role,
        "outcome": "unknown",
        "severity": "unknown",
        "timing": "unknown",
        "travel_country": "",
        "travel_city": "",
        "travel_purpose": "",
        "travel_outcome": "",
        "researcher_id": "",
        "consent_given": False,
        "anonymize": False,
        "created_by": "script",
    }
    chart_data.update(extract_enhanced_planetary_data(planetary_positions))

    if not supabase_manager:
        print("  ERROR: Supabase not configured.")
        return False
    result = supabase_manager.insert_birth_chart(chart_data)
    if result:
        print(f"  OK: Inserted (id={result.get('id', '?')}).")
        return True
    print("  ERROR: Insert failed.")
    return False


def main():
    if not supabase_manager:
        print("Supabase not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY.")
        sys.exit(1)
    profiles = PROFILES
    if "--batch" in sys.argv:
        idx = sys.argv.index("--batch")
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1] == "2":
            profiles = PROFILES_BATCH2
            print("Using batch 2 (business & cinema).")
    skip_confirm = "--yes-use-assumed-genders" in sys.argv or "-y" in sys.argv
    if skip_confirm:
        print("Using assumed genders for all profiles (no prompt).")
    else:
        print("Add profiles one by one with gender confirmation")
    print("Total profiles:", len(profiles))
    for i, (name, role, date_str, time_str, place, assumed_gender) in enumerate(profiles, start=1):
        add_one(i, name, role, date_str, time_str, place, assumed_gender, skip_confirm=skip_confirm)
    print("\nDone.")


if __name__ == "__main__":
    main()
