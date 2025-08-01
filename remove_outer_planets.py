#!/usr/bin/env python3
"""
Remove Uranus, Neptune, Pluto from existing records
"""

from app import app, db, BirthChart
from swiss_ephemeris_utils import calculate_planetary_positions
import json

def remove_outer_planets():
    """
    Update existing birth chart records to remove Uranus, Neptune, Pluto
    """
    print("🔄 Removing Uranus, Neptune, Pluto from existing records...")
    
    with app.app_context():
        # Get all birth charts
        charts = BirthChart.query.all()
        
        updated_count = 0
        
        for chart in charts:
            try:
                # Check if the record has planetary positions
                if chart.planetary_positions:
                    existing_data = json.loads(chart.planetary_positions)
                    
                    # Check if outer planets exist
                    has_outer_planets = any(planet in existing_data for planet in ['Uranus', 'Neptune', 'Pluto'])
                    
                    if has_outer_planets:
                        print(f"📝 Updating chart {chart.id}: {chart.name}")
                        
                        # Recalculate planetary positions (now excludes outer planets)
                        planetary_positions = calculate_planetary_positions(
                            chart.date_of_birth, 
                            chart.time_of_birth, 
                            chart.latitude or 0, 
                            chart.longitude or 0,
                            5.5  # IST timezone
                        )
                        
                        # Update the record
                        chart.planetary_positions = json.dumps(planetary_positions)
                        updated_count += 1
                        
                        # Show what planets are now included
                        planets = [p for p in planetary_positions.keys() if p not in ['House_Cusps']]
                        print(f"  🌟 Planets now included: {', '.join(planets)}")
                
            except Exception as e:
                print(f"❌ Error updating chart {chart.id}: {e}")
        
        # Commit all changes
        db.session.commit()
        
        print(f"✅ Updated {updated_count} records to remove outer planets")
        
        if updated_count == 0:
            print("ℹ️  All records already have correct planets or no records found")

if __name__ == "__main__":
    remove_outer_planets() 