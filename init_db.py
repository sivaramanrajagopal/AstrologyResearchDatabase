#!/usr/bin/env python3
"""
Database initialization script for Astrological Birth Chart Database
"""

from app import app, db, BirthChart

def init_database():
    """Initialize the database with the correct schema"""
    with app.app_context():
        # Drop all tables to ensure clean slate
        db.drop_all()
        print("✓ Dropped all existing tables")
        
        # Create all tables with new schema
        db.create_all()
        print("✓ Created all tables with new schema")
        
        # Verify the schema
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'birth_chart' in tables:
            columns = [col['name'] for col in inspector.get_columns('birth_chart')]
            print(f"✓ Birth chart table columns: {columns}")
            
            if 'planetary_positions' in columns:
                print("✓ Planetary positions column exists!")
            else:
                print("✗ Planetary positions column missing!")
        else:
            print("✗ Birth chart table not found!")

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Database initialization complete!") 