#!/usr/bin/env python3
"""
Database migration script to add end_time column to sessions table
This fixes the error: column sessions.end_time does not exist

Run this script once to update existing databases.
"""

from app import create_app
from models.database import db
from sqlalchemy import text
import sys

def check_column_exists():
    """Check if end_time column already exists"""
    try:
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='sessions' 
            AND column_name='end_time'
        """))
        return result.fetchone() is not None
    except Exception as e:
        print(f"Error checking column existence: {e}")
        return False

def add_end_time_column():
    """Add end_time column to sessions table"""
    try:
        # Add the column as nullable
        db.session.execute(text("""
            ALTER TABLE sessions 
            ADD COLUMN IF NOT EXISTS end_time TIMESTAMP
        """))
        db.session.commit()
        print("✓ Successfully added end_time column to sessions table")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error adding end_time column: {e}")
        return False

def populate_end_time_values():
    """Populate end_time values for existing sessions based on session_date + duration"""
    try:
        # Update existing sessions to calculate end_time from session_date and duration
        db.session.execute(text("""
            UPDATE sessions 
            SET end_time = session_date + (duration || ' minutes')::INTERVAL
            WHERE end_time IS NULL AND session_date IS NOT NULL AND duration IS NOT NULL
        """))
        db.session.commit()
        
        # Get count of updated rows
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM sessions WHERE end_time IS NOT NULL
        """))
        count = result.scalar()
        print(f"✓ Successfully populated end_time values for {count} existing sessions")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"✗ Error populating end_time values: {e}")
        return False

def migrate():
    """Run the migration"""
    app = create_app()
    
    with app.app_context():
        print("Checking if migration is needed...")
        
        if check_column_exists():
            print("! Column 'end_time' already exists in sessions table")
            print("! Migration not needed or already completed")
            return True
        
        print("\nAdding end_time column to sessions table...")
        if not add_end_time_column():
            return False
        
        print("\nPopulating end_time values for existing sessions...")
        if not populate_end_time_values():
            return False
        
        print("\n✓ Migration completed successfully!")
        return True

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
