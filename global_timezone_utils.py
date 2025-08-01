#!/usr/bin/env python3
"""
Global timezone utilities for astrology calculations
"""

from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime, date
import json

# Initialize timezone finder
tf = TimezoneFinder()

def get_timezone_from_coordinates(lat, lon):
    """
    Automatically detect timezone from coordinates
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
    
    Returns:
        str: Timezone name (e.g., 'Asia/Kolkata', 'America/New_York')
    """
    try:
        timezone_name = tf.timezone_at(lng=lon, lat=lat)
        if timezone_name:
            # Validate timezone name with pytz
            import pytz
            try:
                pytz.timezone(timezone_name)
                return timezone_name
            except pytz.exceptions.UnknownTimeZoneError:
                print(f"Invalid timezone detected: {timezone_name}")
                return estimate_timezone_from_longitude(lon)
        else:
            # Fallback: estimate timezone from longitude
            return estimate_timezone_from_longitude(lon)
    except Exception as e:
        print(f"Error detecting timezone: {e}")
        return estimate_timezone_from_longitude(lon)

def estimate_timezone_from_longitude(lon):
    """
    Estimate timezone from longitude as fallback
    
    Args:
        lon (float): Longitude
    
    Returns:
        str: Estimated timezone name
    """
    # Rough estimation based on longitude
    # Each 15 degrees = 1 hour timezone difference
    hours_from_utc = int(round(lon / 15))
    
    # Map to common timezone names
    timezone_map = {
        -12: 'Pacific/Kwajalein',
        -11: 'Pacific/Midway',
        -10: 'Pacific/Honolulu',
        -9: 'America/Anchorage',
        -8: 'America/Los_Angeles',
        -7: 'America/Denver',
        -6: 'America/Chicago',
        -5: 'America/New_York',
        -4: 'America/Halifax',
        -3: 'America/Sao_Paulo',
        -2: 'Atlantic/South_Georgia',
        -1: 'Atlantic/Azores',
        0: 'Europe/London',
        1: 'Europe/Paris',
        2: 'Europe/Kiev',
        3: 'Europe/Moscow',
        4: 'Asia/Dubai',
        5: 'Asia/Kolkata',
        6: 'Asia/Dhaka',
        7: 'Asia/Bangkok',
        8: 'Asia/Shanghai',
        9: 'Asia/Tokyo',
        10: 'Australia/Sydney',
        11: 'Pacific/Guadalcanal',
        12: 'Pacific/Auckland'
    }
    
    return timezone_map.get(hours_from_utc, 'UTC')

def get_timezone_offset(lat, lon, birth_date):
    """
    Get timezone offset for specific date (handles DST)
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        birth_date (date): Birth date
    
    Returns:
        float: Timezone offset in hours from UTC
    """
    try:
        timezone_name = get_timezone_from_coordinates(lat, lon)
        tz = pytz.timezone(timezone_name)
        
        # Create datetime at noon to avoid DST transition issues
        dt = datetime.combine(birth_date, datetime.min.time().replace(hour=12))
        local_dt = tz.localize(dt)
        
        return local_dt.utcoffset().total_seconds() / 3600
    except Exception as e:
        print(f"Error calculating timezone offset: {e}")
        return 0

def get_timezone_info(lat, lon, birth_date=None):
    """
    Get comprehensive timezone information
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        birth_date (date): Birth date (optional)
    
    Returns:
        dict: Timezone information
    """
    try:
        timezone_name = get_timezone_from_coordinates(lat, lon)
        tz = pytz.timezone(timezone_name)
        
        # Get current offset
        now = datetime.now()
        local_now = tz.localize(now)
        current_offset = local_now.utcoffset().total_seconds() / 3600
        
        # Get offset for birth date if provided
        birth_offset = None
        if birth_date:
            birth_offset = get_timezone_offset(lat, lon, birth_date)
        
        return {
            'timezone_name': timezone_name,
            'current_offset': current_offset,
            'birth_offset': birth_offset,
            'is_dst': local_now.dst().total_seconds() > 0 if local_now.dst() else False
        }
    except Exception as e:
        print(f"Error getting timezone info: {e}")
        return {
            'timezone_name': 'UTC',
            'current_offset': 0,
            'birth_offset': 0,
            'is_dst': False
        }

def test_global_locations():
    """
    Test timezone detection for various global locations
    """
    test_locations = [
        {'name': 'New York', 'lat': 40.7128, 'lon': -74.0060},
        {'name': 'London', 'lat': 51.5074, 'lon': -0.1278},
        {'name': 'Tokyo', 'lat': 35.6762, 'lon': 139.6503},
        {'name': 'Sydney', 'lat': -33.8688, 'lon': 151.2093},
        {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777},
        {'name': 'Dubai', 'lat': 25.2048, 'lon': 55.2708},
        {'name': 'Singapore', 'lat': 1.3521, 'lon': 103.8198},
        {'name': 'Cairo', 'lat': 30.0444, 'lon': 31.2357},
        {'name': 'Rio de Janeiro', 'lat': -22.9068, 'lon': -43.1729},
        {'name': 'Los Angeles', 'lat': 34.0522, 'lon': -118.2437}
    ]
    
    print("🌍 Testing Global Timezone Detection")
    print("=" * 60)
    
    for location in test_locations:
        info = get_timezone_info(location['lat'], location['lon'])
        print(f"📍 {location['name']}:")
        print(f"   Coordinates: {location['lat']}, {location['lon']}")
        print(f"   Timezone: {info['timezone_name']}")
        print(f"   Current Offset: UTC{info['current_offset']:+g}")
        print(f"   DST: {'Yes' if info['is_dst'] else 'No'}")
        print()

if __name__ == "__main__":
    test_global_locations() 