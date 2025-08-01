#!/usr/bin/env python3
"""
Script to update existing records with enhanced calculations
This will add house positions, yogas, Shadbala, and aspects to existing records
"""

import environment_config
from datetime import datetime
from enhanced_swiss_ephemeris import calculate_enhanced_planetary_positions, extract_enhanced_planetary_data
from supabase_config import SupabaseManager

def update_existing_records():
    """
    Update existing records with enhanced calculations
    """
    print("🔄 Updating existing records with enhanced calculations...")
    print("=" * 60)
    
    # Initialize Supabase
    supabase_manager = SupabaseManager()
    
    try:
        # Get all existing records
        charts = supabase_manager.get_all_charts()
        
        if not charts:
            print("❌ No records found to update")
            return
        
        print(f"📊 Found {len(charts)} records to update")
        print()
        
        updated_count = 0
        
        for chart in charts:
            try:
                print(f"🔄 Processing: {chart['name']} (ID: {chart['id']})")
                
                # Parse date and time
                date_of_birth = datetime.strptime(chart['date_of_birth'], '%Y-%m-%d').date()
                time_of_birth = datetime.strptime(chart['time_of_birth'], '%H:%M:%S').time()
                
                # Calculate enhanced positions
                enhanced_positions = calculate_enhanced_planetary_positions(
                    date_of_birth=date_of_birth,
                    time_of_birth=time_of_birth,
                    latitude=chart['latitude'],
                    longitude=chart['longitude'],
                    timezone_name=chart['timezone_name']
                )
                
                if enhanced_positions:
                    # Extract enhanced data
                    enhanced_data = extract_enhanced_planetary_data(enhanced_positions)
                    
                    # Update the record
                    success = supabase_manager.update_birth_chart(chart['id'], enhanced_data)
                    
                    if success:
                        print(f"✅ Updated {chart['name']} with enhanced data")
                        updated_count += 1
                    else:
                        print(f"❌ Failed to update {chart['name']}")
                else:
                    print(f"❌ Failed to calculate enhanced positions for {chart['name']}")
                
            except Exception as e:
                print(f"❌ Error processing {chart.get('name', 'Unknown')}: {e}")
        
        print()
        print(f"🎉 Update complete! {updated_count}/{len(charts)} records updated successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def verify_enhanced_data():
    """
    Verify that enhanced data is present in records
    """
    print("\n🔍 Verifying enhanced data...")
    print("=" * 40)
    
    supabase_manager = SupabaseManager()
    
    try:
        charts = supabase_manager.get_all_charts()
        
        for chart in charts:
            print(f"\n📋 {chart['name']} (ID: {chart['id']}):")
            
            # Check house data
            house_data_present = any(f'house_{i}_longitude' in chart and chart[f'house_{i}_longitude'] is not None for i in range(1, 13))
            print(f"   🏠 House positions: {'✅ Present' if house_data_present else '❌ Missing'}")
            
            # Check JSON data
            yogas_present = 'yogas' in chart and chart['yogas'] is not None
            shadbala_present = 'shadbala' in chart and chart['shadbala'] is not None
            aspects_present = 'aspects' in chart and chart['aspects'] is not None
            
            print(f"   🧘 Yogas: {'✅ Present' if yogas_present else '❌ Missing'}")
            print(f"   ⚖️ Shadbala: {'✅ Present' if shadbala_present else '❌ Missing'}")
            print(f"   🔗 Aspects: {'✅ Present' if aspects_present else '❌ Missing'}")
    
    except Exception as e:
        print(f"❌ Error verifying data: {e}")

if __name__ == "__main__":
    print("🚀 Enhanced Data Update Script")
    print("=" * 40)
    
    # First, update existing records
    update_existing_records()
    
    # Then verify the data
    verify_enhanced_data()
    
    print("\n🎯 Next Steps:")
    print("1. Run the safe migration script in Supabase")
    print("2. Run this script to update existing records")
    print("3. Test the application with enhanced features")
    print("4. Add new birth charts to see enhanced calculations") 