"""
Utility script to check if a user account exists and verify password
Usage: python utils/check_user_account.py <email>
"""

from app import create_app
from models.user import User
from utils.auth import verify_password, hash_password

def check_user_account(email):
    """Check if user account exists and verify details"""
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ No User account found for: {email}")
            print("\nTo create a User account:")
            print("1. If this is a trainer: Use 'Change Password' button in admin dashboard")
            print("2. If this is a client: Use 'Change Password' button in admin dashboard")
            print("3. Or run: python utils/create_trainer_user.py")
            return False
        
        print(f"✅ User account found for: {email}")
        print(f"   - ID: {user.id}")
        print(f"   - Role: {user.role}")
        print(f"   - Active: {user.active}")
        print(f"   - Created: {user.created_at}")
        print(f"   - Last Login: {user.last_login}")
        print(f"   - Has Password Hash: {'Yes' if user.password_hash else 'No'}")
        
        return True

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python utils/check_user_account.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    check_user_account(email)

