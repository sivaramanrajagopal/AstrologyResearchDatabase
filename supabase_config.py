#!/usr/bin/env python3
"""
Supabase configuration and database utilities for global astrology database
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Dict, List, Optional
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class SupabaseManager:
    def __init__(self):
        self.url = os.environ.get('SUPABASE_URL')
        self.key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(self.url, self.key)
    
    def insert_birth_chart(self, chart_data: Dict) -> Optional[Dict]:
        """
        Insert a new birth chart into the astrology_charts table
        """
        try:
            result = self.supabase.table('astrology_charts').insert(chart_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error inserting birth chart: {e}")
            return None
    
    def get_birth_chart(self, chart_id: int) -> Optional[Dict]:
        """
        Get a birth chart by ID
        """
        try:
            result = self.supabase.table('astrology_charts').select('*').eq('id', chart_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting birth chart: {e}")
            return None
    
    def get_all_charts(self, limit: int = 100) -> List[Dict]:
        """
        Get all birth charts with optional limit
        """
        try:
            result = self.supabase.table('astrology_charts').select('*').limit(limit).execute()
            return result.data
        except Exception as e:
            print(f"Error getting all charts: {e}")
            return []
    
    def update_birth_chart(self, chart_id: int, chart_data: Dict) -> Optional[Dict]:
        """
        Update a birth chart
        """
        try:
            result = self.supabase.table('astrology_charts').update(chart_data).eq('id', chart_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating birth chart: {e}")
            return None
    
    def delete_birth_chart(self, chart_id: int) -> bool:
        """
        Delete a birth chart
        """
        try:
            result = self.supabase.table('astrology_charts').delete().eq('id', chart_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting birth chart: {e}")
            return False
    
    def get_charts_by_category(self, primary_category: str = None, sub_category: str = None) -> List[Dict]:
        """
        Get charts filtered by category
        """
        try:
            query = self.supabase.table('astrology_charts').select('*')
            
            if primary_category:
                query = query.eq('primary_category', primary_category)
            
            if sub_category:
                query = query.eq('sub_category', sub_category)
            
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"Error getting charts by category: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """
        Get database statistics
        """
        try:
            # Get total count
            total_result = self.supabase.table('astrology_charts').select('id', count='exact').execute()
            total_charts = total_result.count if total_result.count else 0
            
            # Get category counts
            category_result = self.supabase.table('astrology_charts').select('primary_category').execute()
            category_counts = {}
            
            for chart in category_result.data:
                category = chart.get('primary_category', 'Unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
            
            return {
                'total_charts': total_charts,
                'category_counts': category_counts
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {'total_charts': 0, 'category_counts': {}}

# Initialize Supabase manager
try:
    supabase_manager = SupabaseManager()
except Exception as e:
    print(f"Warning: Could not initialize Supabase: {e}")
    supabase_manager = None 