"""
Create default admin user
Run this script to create a default admin user for initial setup
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.database import db
from models.user import User
from utils.auth import hash_password

def create_default_admin():
    """Create default admin user"""
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@fitnesscrm.com').first()
        
        if admin:
            print("Default admin user already exists!")
            print(f"Email: {admin.email}")
            print(f"Role: {admin.role}")
            return
        
        # Create default admin
        admin = User(
            email='admin@fitnesscrm.com',
            password_hash=hash_password('admin123'),
            role='admin',
            active=True
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("=" * 60)
        print("Default Admin User Created Successfully!")
        print("=" * 60)
        print(f"Email: {admin.email}")
        print(f"Password: admin123")
        print(f"Role: {admin.role}")
        print("=" * 60)
        print("\n⚠️  IMPORTANT: Change this password after first login!")
        print("=" * 60)

if __name__ == '__main__':
    create_default_admin()

