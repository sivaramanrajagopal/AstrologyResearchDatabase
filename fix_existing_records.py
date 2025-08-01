#!/usr/bin/env python3
"""
Fix existing records by adding planetary positions and updating database schema
"""

from app import app, db, BirthChart
from swiss_ephemeris_utils import calculate_planetary_positions
import json

def fix_existing_records():
    """Fix existing records by adding planetary positions"""
    
    print("🔧 Fixing Existing Records")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Get all existing records
            existing_charts = BirthChart.query.all()
            print(f"Found {len(existing_charts)} existing records")
            
            if not existing_charts:
                print("No existing records to fix")
                return
            
            # Fix each record
            for chart in existing_charts:
                print(f"\nProcessing chart: {chart.name} (ID: {chart.id})")
                
                # Check if planetary positions already exist
                if chart.planetary_positions:
                    print(f"  ✅ Chart {chart.id} already has planetary data")
                    continue
                
                # Calculate planetary positions for existing record
                try:
                    # Use coordinates if available, otherwise use defaults
                    lat = chart.latitude if chart.latitude else 19.0760  # Mumbai default
                    lon = chart.longitude if chart.longitude else 72.8777
                    
                    print(f"  📍 Using coordinates: {lat}, {lon}")
                    
                    # Calculate planetary positions
                    planetary_positions = calculate_planetary_positions(
                        chart.date_of_birth,
                        chart.time_of_birth,
                        lat,
                        lon
                    )
                    
                    if planetary_positions:
                        # Convert to JSON and save
                        planetary_positions_json = json.dumps(planetary_positions)
                        chart.planetary_positions = planetary_positions_json
                        
                        # Update the record
                        db.session.commit()
                        print(f"  ✅ Added planetary data for {chart.name}")
                        
                        # Show sample data
                        sample_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars']
                        for planet in sample_planets:
                            if planet in planetary_positions:
                                info = planetary_positions[planet]
                                print(f"    {planet}: {info['longitude']:.2f}° {info['rasi']}")
                    else:
                        print(f"  ❌ Could not calculate planetary positions for {chart.name}")
                        
                except Exception as e:
                    print(f"  ❌ Error processing {chart.name}: {e}")
                    continue
            
            print(f"\n✅ Fixed {len(existing_charts)} records")
            
        except Exception as e:
            print(f"❌ Error in fix_existing_records: {e}")
            import traceback
            traceback.print_exc()

def verify_database_schema():
    """Verify the database schema is correct"""
    
    print("\n🔍 Verifying Database Schema")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Check if planetary_positions column exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            
            if 'birth_chart' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('birth_chart')]
                print(f"Database columns: {columns}")
                
                if 'planetary_positions' in columns:
                    print("✅ planetary_positions column exists")
                else:
                    print("❌ planetary_positions column missing")
                    
                # Count records with planetary data
                total_charts = BirthChart.query.count()
                charts_with_planets = BirthChart.query.filter(
                    BirthChart.planetary_positions.isnot(None)
                ).count()
                
                print(f"Total charts: {total_charts}")
                print(f"Charts with planetary data: {charts_with_planets}")
                
            else:
                print("❌ birth_chart table not found")
                
        except Exception as e:
            print(f"❌ Error verifying schema: {e}")

if __name__ == "__main__":
    fix_existing_records()
    verify_database_schema() 