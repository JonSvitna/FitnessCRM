"""
Utility script to create User accounts for existing trainers/clients that don't have them
Run this if trainers/clients were created before password management was added
"""

from app import create_app
from models.database import db, Trainer, Client
from models.user import User
from utils.auth import hash_password

def create_missing_user_accounts():
    """Create User accounts for trainers/clients that don't have them"""
    app = create_app()
    
    with app.app_context():
        # Find trainers without User accounts
        trainers = Trainer.query.all()
        created_count = 0
        
        for trainer in trainers:
            user = User.query.filter_by(email=trainer.email).first()
            if not user:
                # Create user account with default password
                default_password = 'trainer123'  # Change this!
                user = User(
                    email=trainer.email,
                    password_hash=hash_password(default_password),
                    role='trainer',
                    active=True
                )
                db.session.add(user)
                created_count += 1
                print(f"Created User account for trainer: {trainer.email} (password: trainer123)")
        
        # Find clients without User accounts
        clients = Client.query.all()
        
        for client in clients:
            user = User.query.filter_by(email=client.email).first()
            if not user:
                # Create user account with default password
                default_password = 'client123'  # Change this!
                user = User(
                    email=client.email,
                    password_hash=hash_password(default_password),
                    role='client',
                    active=True
                )
                db.session.add(user)
                created_count += 1
                print(f"Created User account for client: {client.email} (password: client123)")
        
        if created_count > 0:
            db.session.commit()
            print(f"\n✓ Created {created_count} User accounts")
            print("⚠️  IMPORTANT: Change these default passwords immediately!")
        else:
            print("✓ All trainers/clients already have User accounts")
        
        return created_count

if __name__ == '__main__':
    create_missing_user_accounts()

