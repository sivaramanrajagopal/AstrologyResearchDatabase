#!/usr/bin/env python3
"""
Google Geocoding API integration with timezone handling
"""

import requests
import json
from typing import Dict, Optional
import os
from datetime import datetime
import pytz

class GoogleGeocodingAPI:
    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_MAPS_API_KEY', 'your-google-maps-api-key')
        self.geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.timezone_url = "https://maps.googleapis.com/maps/api/timezone/json"
    
    def geocode_address(self, address: str) -> Optional[Dict]:
        """
        Get latitude, longitude, and formatted address from place name
        """
        try:
            params = {
                'address': address,
                'key': self.api_key
            }
            
            response = requests.get(self.geocoding_url, params=params)
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                location = result['geometry']['location']
                
                return {
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'formatted_address': result['formatted_address'],
                    'place_id': result['place_id'],
                    'address_components': result['address_components']
                }
            else:
                print(f"Geocoding error: {data.get('status', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"Error in geocoding: {str(e)}")
            return None
    
    def get_timezone_info(self, latitude: float, longitude: float, timestamp: int = None) -> Optional[Dict]:
        """
        Get timezone information for given coordinates
        """
        try:
            if timestamp is None:
                timestamp = int(datetime.now().timestamp())
            
            params = {
                'location': f"{latitude},{longitude}",
                'timestamp': timestamp,
                'key': self.api_key
            }
            
            response = requests.get(self.timezone_url, params=params)
            data = response.json()
            
            if data['status'] == 'OK':
                return {
                    'timezone_id': data['timeZoneId'],
                    'timezone_name': data['timeZoneName'],
                    'dst_offset': data['dstOffset'],
                    'raw_offset': data['rawOffset'],
                    'total_offset_hours': (data['rawOffset'] + data['dstOffset']) / 3600
                }
            else:
                print(f"Timezone error: {data.get('status', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"Error getting timezone: {str(e)}")
            return None

# Initialize the API class
geo_api = GoogleGeocodingAPI()

def get_location_details(place_name: str, birth_datetime: str = None) -> Optional[Dict]:
    """
    Get complete location details including timezone offset for astrological calculations
    """
    try:
        # Get geocoding data
        geo_data = geo_api.geocode_address(place_name)
        
        if not geo_data:
            return None
        
        # Get timezone data
        timezone_data = geo_api.get_timezone_info(
            geo_data['latitude'], 
            geo_data['longitude']
        )
        
        if timezone_data:
            return {
                **geo_data,
                **timezone_data
            }
        else:
            return geo_data
            
    except Exception as e:
        print(f"Error getting location details: {str(e)}")
        return None

def test_geocoding():
    """
    Test the geocoding functionality
    """
    test_places = [
        "Mumbai, India",
        "New York, USA", 
        "London, UK",
        "Tokyo, Japan",
        "Sydney, Australia"
    ]
    
    print("🌍 Testing Google Geocoding API")
    print("=" * 50)
    
    for place in test_places:
        print(f"\n📍 Testing: {place}")
        details = get_location_details(place)
        
        if details:
            print(f"   ✅ Success!")
            print(f"   Coordinates: {details['latitude']}, {details['longitude']}")
            print(f"   Address: {details['formatted_address']}")
            if 'timezone_id' in details:
                print(f"   Timezone: {details['timezone_id']}")
                print(f"   Offset: {details['total_offset_hours']:.1f} hours")
        else:
            print(f"   ❌ Failed to get location details")

if __name__ == "__main__":
    test_geocoding() 