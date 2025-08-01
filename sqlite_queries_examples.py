#!/usr/bin/env python3
"""
SQLite Database Querying Examples
Shows how to query the birth charts database using different methods
"""

import sqlite3
from app import app, db, BirthChart
from sqlalchemy import text, func
from datetime import date

def direct_sqlite_queries():
    """Direct SQLite queries using sqlite3 module"""
    
    print("🔍 DIRECT SQLITE QUERIES")
    print("=" * 50)
    
    # Connect to the database file
    conn = sqlite3.connect('instance/birthcharts.db')
    cursor = conn.cursor()
    
    # 1. Basic SELECT query
    print("\n1. Basic SELECT - All records:")
    cursor.execute("SELECT id, name, gender, date_of_birth FROM birth_chart")
    results = cursor.fetchall()
    for row in results:
        print(f"  ID: {row[0]}, Name: {row[1]}, Gender: {row[2]}, DOB: {row[3]}")
    
    # 2. WHERE clause
    print("\n2. WHERE clause - Female records:")
    cursor.execute("""
        SELECT name, city, country, research_category 
        FROM birth_chart 
        WHERE gender = 'Female'
    """)
    results = cursor.fetchall()
    for row in results:
        print(f"  {row[0]} from {row[1]}, {row[2]} - {row[3]}")
    
    # 3. COUNT query
    print("\n3. COUNT query - Total records:")
    cursor.execute("SELECT COUNT(*) FROM birth_chart")
    count = cursor.fetchone()[0]
    print(f"  Total records: {count}")
    
    # 4. GROUP BY query
    print("\n4. GROUP BY - Records by research category:")
    cursor.execute("""
        SELECT research_category, COUNT(*) as count
        FROM birth_chart 
        GROUP BY research_category
    """)
    results = cursor.fetchall()
    for row in results:
        print(f"  {row[0]}: {row[1]} records")
    
    # 5. ORDER BY query
    print("\n5. ORDER BY - Records by name:")
    cursor.execute("""
        SELECT name, date_of_birth, research_category
        FROM birth_chart 
        ORDER BY name ASC
    """)
    results = cursor.fetchall()
    for row in results:
        print(f"  {row[0]} - {row[1]} - {row[2]}")
    
    # 6. LIKE query (search)
    print("\n6. LIKE query - Search by city:")
    cursor.execute("""
        SELECT name, city, country
        FROM birth_chart 
        WHERE city LIKE '%Mumbai%'
    """)
    results = cursor.fetchall()
    for row in results:
        print(f"  {row[0]} from {row[1]}, {row[2]}")
    
    # 7. Complex query with multiple conditions
    print("\n7. Complex query - Business success records:")
    cursor.execute("""
        SELECT name, gender, date_of_birth, city
        FROM birth_chart 
        WHERE research_category = 'Business Success'
        AND date_of_birth >= '1990-01-01'
        ORDER BY date_of_birth DESC
    """)
    results = cursor.fetchall()
    for row in results:
        print(f"  {row[0]} ({row[1]}) - {row[2]} from {row[3]}")
    
    # 8. JSON query (planetary positions)
    print("\n8. JSON query - Check planetary data:")
    cursor.execute("""
        SELECT name, 
               CASE 
                   WHEN planetary_positions IS NOT NULL 
                   THEN 'Has planetary data'
                   ELSE 'No planetary data'
               END as data_status
        FROM birth_chart
    """)
    results = cursor.fetchall()
    for row in results:
        print(f"  {row[0]}: {row[1]}")
    
    conn.close()

def sqlalchemy_queries():
    """SQLAlchemy ORM queries (like Supabase)"""
    
    print("\n🔍 SQLALCHEMY ORM QUERIES (Like Supabase)")
    print("=" * 50)
    
    with app.app_context():
        # 1. Get all records
        print("\n1. Get all records:")
        all_charts = BirthChart.query.all()
        for chart in all_charts:
            print(f"  {chart.name} - {chart.research_category}")
        
        # 2. Filter by condition
        print("\n2. Filter by research category:")
        business_charts = BirthChart.query.filter_by(research_category='Business Success').all()
        for chart in business_charts:
            print(f"  {chart.name} from {chart.city}")
        
        # 3. Complex filtering
        print("\n3. Complex filtering:")
        modern_female_charts = BirthChart.query.filter(
            BirthChart.gender == 'Female',
            BirthChart.date_of_birth >= date(1990, 1, 1)
        ).all()
        for chart in modern_female_charts:
            print(f"  {chart.name} ({chart.date_of_birth})")
        
        # 4. Search with LIKE
        print("\n4. Search with LIKE:")
        mumbai_charts = BirthChart.query.filter(
            BirthChart.city.like('%Mumbai%')
        ).all()
        for chart in mumbai_charts:
            print(f"  {chart.name} from {chart.city}")
        
        # 5. Order by
        print("\n5. Order by name:")
        ordered_charts = BirthChart.query.order_by(BirthChart.name.asc()).all()
        for chart in ordered_charts:
            print(f"  {chart.name}")
        
        # 6. Limit and offset (pagination)
        print("\n6. Pagination (limit 5):")
        paginated_charts = BirthChart.query.limit(5).offset(0).all()
        for chart in paginated_charts:
            print(f"  {chart.name}")
        
        # 7. Count
        print("\n7. Count records:")
        total_count = BirthChart.query.count()
        print(f"  Total records: {total_count}")
        
        # 8. Group by (using SQLAlchemy functions)
        print("\n8. Group by research category:")
        from sqlalchemy import func
        category_counts = db.session.query(
            BirthChart.research_category,
            func.count(BirthChart.id).label('count')
        ).group_by(BirthChart.research_category).all()
        
        for category, count in category_counts:
            print(f"  {category}: {count} records")
        
        # 9. Raw SQL with SQLAlchemy
        print("\n9. Raw SQL query:")
        result = db.session.execute(text("""
            SELECT name, research_category, 
                   CASE 
                       WHEN planetary_positions IS NOT NULL 
                       THEN 'Has data'
                       ELSE 'No data'
                   END as status
            FROM birth_chart
            ORDER BY name
        """))
        
        for row in result:
            print(f"  {row.name} - {row.research_category} - {row.status}")

def advanced_queries():
    """Advanced querying techniques"""
    
    print("\n🔍 ADVANCED QUERYING TECHNIQUES")
    print("=" * 50)
    
    with app.app_context():
        # 1. Date range queries
        print("\n1. Date range queries:")
        recent_charts = BirthChart.query.filter(
            BirthChart.date_of_birth >= date(1990, 1, 1),
            BirthChart.date_of_birth <= date(2000, 12, 31)
        ).all()
        for chart in recent_charts:
            print(f"  {chart.name} - {chart.date_of_birth}")
        
        # 2. Multiple research categories
        print("\n2. Multiple research categories:")
        medical_charts = BirthChart.query.filter(
            BirthChart.research_category.in_(['Medical Conditions', 'Autism Research'])
        ).all()
        for chart in medical_charts:
            print(f"  {chart.name} - {chart.research_category}")
        
        # 3. OR conditions
        print("\n3. OR conditions:")
        from sqlalchemy import or_
        specific_charts = BirthChart.query.filter(
            or_(
                BirthChart.city.like('%Mumbai%'),
                BirthChart.city.like('%Delhi%')
            )
        ).all()
        for chart in specific_charts:
            print(f"  {chart.name} from {chart.city}")
        
        # 4. Subqueries
        print("\n4. Subquery - Charts with planetary data:")
        charts_with_planets = BirthChart.query.filter(
            BirthChart.planetary_positions.isnot(None)
        ).all()
        for chart in charts_with_planets:
            print(f"  {chart.name} has planetary data")
        
        # 5. Aggregation with conditions
        print("\n5. Aggregation with conditions:")
        male_count = BirthChart.query.filter(BirthChart.gender == 'Male').count()
        female_count = BirthChart.query.filter(BirthChart.gender == 'Female').count()
        print(f"  Male records: {male_count}")
        print(f"  Female records: {female_count}")
        
        # 6. Text search across multiple fields
        print("\n6. Text search across fields:")
        search_term = "Test"
        search_results = BirthChart.query.filter(
            or_(
                BirthChart.name.like(f'%{search_term}%'),
                BirthChart.city.like(f'%{search_term}%'),
                BirthChart.research_category.like(f'%{search_term}%')
            )
        ).all()
        for chart in search_results:
            print(f"  {chart.name} - {chart.city} - {chart.research_category}")

def export_queries():
    """Export data using queries"""
    
    print("\n🔍 EXPORT QUERIES")
    print("=" * 50)
    
    with app.app_context():
        # 1. Export all data for ML
        print("\n1. Export all data for ML analysis:")
        all_data = BirthChart.query.all()
        ml_data = []
        for chart in all_data:
            ml_data.append({
                'id': chart.id,
                'name': chart.name,
                'gender': chart.gender,
                'birth_date': str(chart.date_of_birth),
                'birth_time': str(chart.time_of_birth),
                'city': chart.city,
                'country': chart.country,
                'research_category': chart.research_category,
                'has_planetary_data': chart.planetary_positions is not None
            })
        
        print(f"  Exported {len(ml_data)} records for ML analysis")
        
        # 2. Export by research category
        print("\n2. Export by research category:")
        categories = db.session.query(BirthChart.research_category).distinct().all()
        for category in categories:
            category_name = category[0]
            charts = BirthChart.query.filter_by(research_category=category_name).all()
            print(f"  {category_name}: {len(charts)} records")
        
        # 3. Export planetary data
        print("\n3. Export charts with planetary data:")
        charts_with_planets = BirthChart.query.filter(
            BirthChart.planetary_positions.isnot(None)
        ).all()
        
        planetary_data = []
        for chart in charts_with_planets:
            planetary_data.append({
                'name': chart.name,
                'birth_info': f"{chart.date_of_birth} {chart.time_of_birth}",
                'location': f"{chart.city}, {chart.country}",
                'planetary_data': chart.planetary_positions
            })
        
        print(f"  {len(planetary_data)} charts with planetary data ready for analysis")

if __name__ == "__main__":
    print("🗄️ SQLite Database Querying Examples")
    print("=" * 60)
    
    try:
        direct_sqlite_queries()
        sqlalchemy_queries()
        advanced_queries()
        export_queries()
        
        print("\n✅ All query examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc() 