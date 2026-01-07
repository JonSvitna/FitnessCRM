#!/usr/bin/env python3
"""
Database migration script to add location column to sessions table
Run this script once to update existing databases.
"""

from app import create_app
from models.database import db
from sqlalchemy import text
import sys

def check_column_exists():
    """Check if location column already exists"""
    try:
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='sessions' 
            AND column_name='location'
        """))
        return result.fetchone() is not None
    except Exception as e:
        print(f"Error checking column existence: {e}")
        return False

def add_location_column():
    """Add location column to sessions table"""
    try:
        # Add the column as nullable
        db.session.execute(text("""
            ALTER TABLE sessions 
            ADD COLUMN IF NOT EXISTS location VARCHAR(200)
        """))
        db.session.commit()
        print("✓ Successfully added location column to sessions table")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error adding location column: {e}")
        return False

def migrate():
    """Run the migration"""
    app = create_app()
    
    with app.app_context():
        print("Checking if migration is needed...")
        
        if check_column_exists():
            print("! Column 'location' already exists in sessions table")
            print("! Migration not needed or already completed")
            return True
        
        print("\nAdding location column to sessions table...")
        if not add_location_column():
            return False
        
        print("\n✓ Migration completed successfully!")
        return True

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
