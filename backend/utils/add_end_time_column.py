"""
Migration script to add end_time column to sessions table.
This script calculates end_time for existing sessions based on session_date + duration.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models.database import db, Session
from datetime import timedelta

def add_end_time_column():
    """Add end_time column to sessions table and populate it for existing records"""
    with app.app_context():
        try:
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('sessions')]
            
            if 'end_time' in columns:
                print("✓ Column 'end_time' already exists in sessions table")
                return
            
            print("Adding 'end_time' column to sessions table...")
            
            # Add the column (using text() for SQL execution)
            from sqlalchemy import text
            db.session.execute(text("""
                ALTER TABLE sessions 
                ADD COLUMN end_time TIMESTAMP
            """))
            db.session.commit()
            
            print("✓ Column added successfully")
            
            # Populate end_time for existing sessions
            print("Calculating end_time for existing sessions...")
            sessions = Session.query.all()
            updated_count = 0
            
            for session in sessions:
                if session.session_date and session.duration:
                    session.end_time = session.session_date + timedelta(minutes=session.duration)
                    updated_count += 1
            
            db.session.commit()
            print(f"✓ Updated {updated_count} existing sessions with calculated end_time")
            
            print("\nMigration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error during migration: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    add_end_time_column()

