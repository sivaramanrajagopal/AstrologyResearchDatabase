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
    
    def get_charts_created_on_date(self, on_date: datetime) -> List[Dict]:
        """
        Get all birth charts created on a given date (UTC).
        on_date: datetime.date or datetime; only the date part is used.
        """
        try:
            d = on_date.date() if isinstance(on_date, datetime) else on_date
            start = datetime(d.year, d.month, d.day, 0, 0, 0)
            end = datetime(d.year, d.month, d.day, 23, 59, 59)
            start_iso = start.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
            end_iso = end.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
            result = (
                self.supabase.table('astrology_charts')
                .select('*')
                .gte('created_at', start_iso)
                .lte('created_at', end_iso)
                .order('id')
                .execute()
            )
            return result.data or []
        except Exception as e:
            print(f"Error getting charts by date: {e}")
            return []

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

    def upsert_career_prediction(
        self,
        chart_id: int,
        career_strength: str,
        factors: list,
        scores: dict,
        d10_snapshot: Optional[Dict] = None,
        dasha_bukti_snapshot: Optional[Dict] = None,
        bav_sav_snapshot: Optional[Dict] = None,
    ) -> Optional[Dict]:
        """Insert or update career prediction for a chart."""
        try:
            row = {
                'chart_id': chart_id,
                'career_strength': career_strength,
                'factors': factors,
                'scores': scores,
                'd10_snapshot': d10_snapshot,
                'dasha_bukti_snapshot': dasha_bukti_snapshot,
                'bav_sav_snapshot': bav_sav_snapshot,
            }
            result = self.supabase.table('career_predictions').upsert(
                row, on_conflict='chart_id'
            ).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error upserting career prediction: {e}")
            return None

    def get_career_prediction(self, chart_id: int) -> Optional[Dict]:
        """Get latest career prediction for a chart."""
        try:
            result = self.supabase.table('career_predictions').select('*').eq('chart_id', chart_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting career prediction: {e}")
            return None

# Initialize Supabase manager
try:
    supabase_manager = SupabaseManager()
except Exception as e:
    print(f"Warning: Could not initialize Supabase: {e}")
    supabase_manager = None 