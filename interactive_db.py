#!/usr/bin/env python3
"""
Interactive Database Shell for Astrology Birth Chart Database
Run this to query the database interactively
"""

from app import app, db, BirthChart
from datetime import datetime, date
import json

def interactive_shell():
    """Interactive database query shell"""
    
    print("🔮 Astrology Database Interactive Shell")
    print("=" * 50)
    print("Available commands:")
    print("  all() - Get all birth charts")
    print("  count() - Count total charts")
    print("  by_category(category) - Filter by research category")
    print("  by_gender(gender) - Filter by gender")
    print("  by_city(city) - Filter by city")
    print("  recent(limit=10) - Get recent charts")
    print("  search(term) - Search in names and notes")
    print("  stats() - Show statistics")
    print("  quit() - Exit")
    print("=" * 50)
    
    with app.app_context():
        while True:
            try:
                command = input("\n🔍 Enter command: ").strip()
                
                if command == "quit()":
                    print("👋 Goodbye!")
                    break
                    
                elif command == "all()":
                    charts = BirthChart.query.all()
                    print(f"📊 Found {len(charts)} charts:")
                    for chart in charts:
                        print(f"  - {chart.name} ({chart.gender}) from {chart.city}")
                        
                elif command == "count()":
                    total = BirthChart.query.count()
                    print(f"📈 Total charts: {total}")
                    
                elif command.startswith("by_category("):
                    category = command.split("(")[1].split(")")[0].strip("'\"")
                    charts = BirthChart.query.filter_by(research_category=category).all()
                    print(f"📂 {category} charts: {len(charts)}")
                    for chart in charts:
                        print(f"  - {chart.name}")
                        
                elif command.startswith("by_gender("):
                    gender = command.split("(")[1].split(")")[0].strip("'\"")
                    charts = BirthChart.query.filter_by(gender=gender).all()
                    print(f"👥 {gender} charts: {len(charts)}")
                    for chart in charts:
                        print(f"  - {chart.name}")
                        
                elif command.startswith("by_city("):
                    city = command.split("(")[1].split(")")[0].strip("'\"")
                    charts = BirthChart.query.filter(BirthChart.city.like(f'%{city}%')).all()
                    print(f"🏙️ Charts from {city}: {len(charts)}")
                    for chart in charts:
                        print(f"  - {chart.name} ({chart.city})")
                        
                elif command.startswith("recent("):
                    try:
                        limit = int(command.split("(")[1].split(")")[0])
                    except:
                        limit = 10
                    charts = BirthChart.query.order_by(BirthChart.created_at.desc()).limit(limit).all()
                    print(f"🕒 {limit} most recent charts:")
                    for chart in charts:
                        print(f"  - {chart.name} (added: {chart.created_at.strftime('%Y-%m-%d')})")
                        
                elif command.startswith("search("):
                    term = command.split("(")[1].split(")")[0].strip("'\"")
                    charts = BirthChart.query.filter(
                        db.or_(
                            BirthChart.name.like(f'%{term}%'),
                            BirthChart.additional_notes.like(f'%{term}%')
                        )
                    ).all()
                    print(f"🔍 Search results for '{term}': {len(charts)}")
                    for chart in charts:
                        print(f"  - {chart.name}")
                        
                elif command == "stats()":
                    total = BirthChart.query.count()
                    male = BirthChart.query.filter_by(gender='Male').count()
                    female = BirthChart.query.filter_by(gender='Female').count()
                    
                    categories = db.session.query(
                        BirthChart.research_category,
                        db.func.count(BirthChart.id)
                    ).group_by(BirthChart.research_category).all()
                    
                    print("📊 Database Statistics:")
                    print(f"  Total charts: {total}")
                    print(f"  Male: {male}")
                    print(f"  Female: {female}")
                    print("  By category:")
                    for category, count in categories:
                        print(f"    {category}: {count}")
                        
                else:
                    print("❌ Unknown command. Type 'quit()' to exit.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    interactive_shell() 