"""
Utility script to verify User accounts are being created correctly
Run this to check if User accounts exist for trainers/clients
"""

from app import create_app
from models.database import db, Trainer, Client
from models.user import User

def verify_user_accounts():
    """Check if trainers/clients have User accounts"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("USER ACCOUNT VERIFICATION REPORT")
        print("=" * 60)
        
        # Check trainers
        trainers = Trainer.query.all()
        trainers_without_users = []
        trainers_with_users = []
        
        print(f"\n📋 TRAINERS ({len(trainers)} total):")
        for trainer in trainers:
            user = User.query.filter_by(email=trainer.email).first()
            if user:
                trainers_with_users.append(trainer)
                print(f"  ✅ {trainer.name} ({trainer.email}) - User ID: {user.id}, Role: {user.role}")
            else:
                trainers_without_users.append(trainer)
                print(f"  ❌ {trainer.name} ({trainer.email}) - NO USER ACCOUNT")
        
        # Check clients
        clients = Client.query.all()
        clients_without_users = []
        clients_with_users = []
        
        print(f"\n👥 CLIENTS ({len(clients)} total):")
        for client in clients:
            user = User.query.filter_by(email=client.email).first()
            if user:
                clients_with_users.append(client)
                print(f"  ✅ {client.name} ({client.email}) - User ID: {user.id}, Role: {user.role}")
            else:
                clients_without_users.append(client)
                print(f"  ❌ {client.name} ({client.email}) - NO USER ACCOUNT")
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY:")
        print("=" * 60)
        print(f"Trainers with User accounts: {len(trainers_with_users)}/{len(trainers)}")
        print(f"Trainers without User accounts: {len(trainers_without_users)}")
        print(f"Clients with User accounts: {len(clients_with_users)}/{len(clients)}")
        print(f"Clients without User accounts: {len(clients_without_users)}")
        
        if trainers_without_users or clients_without_users:
            print("\n⚠️  ACTION REQUIRED:")
            print("   Use 'Change Password' button in admin dashboard to create User accounts")
            print("   Or run: python utils/create_trainer_user.py")
        else:
            print("\n✅ All trainers and clients have User accounts!")
        
        # Check for specific email
        import sys
        if len(sys.argv) > 1:
            email = sys.argv[1].strip().lower()
            print(f"\n🔍 Checking specific email: {email}")
            user = User.query.filter_by(email=email).first()
            trainer = Trainer.query.filter_by(email=email).first()
            client = Client.query.filter_by(email=email).first()
            
            if user:
                print(f"  ✅ User account EXISTS")
                print(f"     - User ID: {user.id}")
                print(f"     - Role: {user.role}")
                print(f"     - Active: {user.active}")
            else:
                print(f"  ❌ User account DOES NOT EXIST")
            
            if trainer:
                print(f"  ✅ Trainer record EXISTS (ID: {trainer.id})")
            else:
                print(f"  ❌ Trainer record DOES NOT EXIST")
            
            if client:
                print(f"  ✅ Client record EXISTS (ID: {client.id})")
            else:
                print(f"  ❌ Client record DOES NOT EXIST")

if __name__ == '__main__':
    import sys
    verify_user_accounts()
    if len(sys.argv) > 1:
        print(f"\n💡 To create User account for {sys.argv[1]}:")
        print(f"   1. Go to admin dashboard")
        print(f"   2. Find trainer/client with email: {sys.argv[1]}")
        print(f"   3. Click 'Change Password' button")
        print(f"   4. Set a password (this creates the User account)")

