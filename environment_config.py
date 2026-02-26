#!/usr/bin/env python3
"""
Environment configuration for Global Astrology Database
"""

import os

# Set environment variables
os.environ['SUPABASE_URL'] = 'https://svrtefferaxnmmejwfdv.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN2cnRlZmZlcmF4bm1tZWp3ZmR2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxNzg5NjQsImV4cCI6MjA2NDc1NDk2NH0.w3m5Vo_q_-QASqzL-k-iWWGYZWG0maqiNzsLHL9aJ7Y'
os.environ['GOOGLE_MAPS_API_KEY'] = 'AIzaSyCYM1jG3VT8D4gTtwkxNK1RaOzEgdmLbs4'
os.environ['SECRET_KEY'] = 'global_astrology_secret_key_2024_secure_random_string'

print("✅ Environment variables set successfully!")
print(f"Supabase URL: {os.environ.get('SUPABASE_URL', '(not set)')}")
key = os.environ.get('GOOGLE_MAPS_API_KEY') or ''
print(f"Google Maps API Key: {(key[:20] + '...') if len(key) > 20 else key or '(not set)'}") 