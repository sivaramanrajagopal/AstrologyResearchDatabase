#!/usr/bin/env python3
"""
Database Query Examples for Astrology Birth Chart Database
Similar to Supabase queries but using SQLAlchemy ORM
"""

from app import app, db, BirthChart
from datetime import datetime, date
import json

def query_examples():
    """Examples of how to query the database"""
    
    with app.app_context():
        
        # 1. SELECT * FROM birth_chart (Get all records)
        all_charts = BirthChart.query.all()
        print(f"Total charts: {len(all_charts)}")
        
        # 2. SELECT * FROM birth_chart WHERE research_category = 'Business Success'
        business_charts = BirthChart.query.filter_by(research_category='Business Success').all()
        print(f"Business success charts: {len(business_charts)}")
        
        # 3. SELECT * FROM birth_chart WHERE gender = 'Male' AND research_category = 'IT Career'
        male_it_charts = BirthChart.query.filter_by(
            gender='Male', 
            research_category='IT Career'
        ).all()
        print(f"Male IT career charts: {len(male_it_charts)}")
        
        # 4. SELECT * FROM birth_chart WHERE date_of_birth >= '1990-01-01'
        modern_charts = BirthChart.query.filter(
            BirthChart.date_of_birth >= date(1990, 1, 1)
        ).all()
        print(f"Charts from 1990 onwards: {len(modern_charts)}")
        
        # 5. SELECT * FROM birth_chart ORDER BY created_at DESC LIMIT 10
        recent_charts = BirthChart.query.order_by(
            BirthChart.created_at.desc()
        ).limit(10).all()
        print(f"10 most recent charts: {len(recent_charts)}")
        
        # 6. SELECT COUNT(*) FROM birth_chart GROUP BY research_category
        category_counts = db.session.query(
            BirthChart.research_category,
            db.func.count(BirthChart.id)
        ).group_by(BirthChart.research_category).all()
        print("Charts by category:")
        for category, count in category_counts:
            print(f"  {category}: {count}")
        
        # 7. SELECT * FROM birth_chart WHERE city LIKE '%Mumbai%'
        mumbai_charts = BirthChart.query.filter(
            BirthChart.city.like('%Mumbai%')
        ).all()
        print(f"Charts from Mumbai: {len(mumbai_charts)}")
        
        # 8. SELECT * FROM birth_chart WHERE latitude BETWEEN 20 AND 30
        tropical_charts = BirthChart.query.filter(
            BirthChart.latitude.between(20, 30)
        ).all()
        print(f"Charts from tropical latitudes: {len(tropical_charts)}")
        
        # 9. Complex query with multiple conditions
        specific_charts = BirthChart.query.filter(
            BirthChart.gender == 'Female',
            BirthChart.research_category.in_(['Medical Conditions', 'Autism Research']),
            BirthChart.date_of_birth >= date(1980, 1, 1),
            BirthChart.date_of_birth <= date(2000, 12, 31)
        ).order_by(BirthChart.date_of_birth.asc()).all()
        print(f"Female medical charts 1980-2000: {len(specific_charts)}")
        
        # 10. Query with planetary positions (JSON data)
        charts_with_planets = BirthChart.query.filter(
            BirthChart.planetary_positions.isnot(None)
        ).all()
        print(f"Charts with planetary data: {len(charts_with_planets)}")
        
        # Example: Get planetary data for first chart
        if charts_with_planets:
            first_chart = charts_with_planets[0]
            try:
                planetary_data = json.loads(first_chart.planetary_positions)
                print(f"Sample planetary data for {first_chart.name}:")
                for planet, data in planetary_data.items():
                    if isinstance(data, dict) and 'longitude' in data:
                        print(f"  {planet}: {data['longitude']}°")
            except json.JSONDecodeError:
                print("Error parsing planetary data")

def advanced_queries():
    """More advanced query examples"""
    
    with app.app_context():
        
        # 1. Pagination (like Supabase .range())
        page = 1
        per_page = 20
        offset = (page - 1) * per_page
        
        paginated_charts = BirthChart.query.order_by(
            BirthChart.created_at.desc()
        ).offset(offset).limit(per_page).all()
        
        # 2. Aggregation queries
        total_charts = BirthChart.query.count()
        male_count = BirthChart.query.filter_by(gender='Male').count()
        female_count = BirthChart.query.filter_by(gender='Female').count()
        
        print(f"Total: {total_charts}, Male: {male_count}, Female: {female_count}")
        
        # 3. Date range queries
        today = datetime.now().date()
        last_month = BirthChart.query.filter(
            BirthChart.created_at >= datetime(today.year, today.month-1, 1)
        ).count()
        print(f"Charts added in last month: {last_month}")
        
        # 4. Text search (like Supabase .ilike())
        search_term = "success"
        search_results = BirthChart.query.filter(
            db.or_(
                BirthChart.name.ilike(f'%{search_term}%'),
                BirthChart.additional_notes.ilike(f'%{search_term}%')
            )
        ).all()
        print(f"Search results for '{search_term}': {len(search_results)}")

def export_queries():
    """Query examples for data export"""
    
    with app.app_context():
        
        # Export all data for CSV
        all_data = BirthChart.query.all()
        
        # Export specific category
        medical_data = BirthChart.query.filter_by(
            research_category='Medical Conditions'
        ).all()
        
        # Export with specific fields only
        basic_data = db.session.query(
            BirthChart.name,
            BirthChart.gender,
            BirthChart.date_of_birth,
            BirthChart.city,
            BirthChart.research_category
        ).all()
        
        print(f"Export examples - All: {len(all_data)}, Medical: {len(medical_data)}, Basic: {len(basic_data)}")

if __name__ == "__main__":
    print("=== Database Query Examples ===")
    query_examples()
    print("\n=== Advanced Queries ===")
    advanced_queries()
    print("\n=== Export Queries ===")
    export_queries() 