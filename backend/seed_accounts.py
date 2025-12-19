#!/usr/bin/env python3
"""
Seed database with real account data including User accounts with email addresses
This script creates trainers, clients, and their corresponding User accounts for authentication
"""

from app import create_app
from models.database import db, Trainer, Client, Assignment
from models.user import User
from utils.auth import hash_password
import sys

def seed_accounts():
    """Seed the database with real account data"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Seeding Database with Real Accounts")
        print("=" * 60)
        
        # Check if admin user exists, if not create it
        admin = User.query.filter_by(email='admin@fitnesscrm.com').first()
        if not admin:
            admin = User(
                email='admin@fitnesscrm.com',
                password_hash=hash_password('admin123'),
                role='admin',
                active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("\n✓ Created admin user: admin@fitnesscrm.com")
            print("  Password: admin123")
        else:
            print("\n✓ Admin user already exists")
        
        # Create trainers with real email addresses
        trainers_data = [
            {
                "name": "Mike Johnson",
                "email": "mike.johnson@fitnesscrm.com",
                "phone": "+1 (555) 100-0001",
                "specialization": "Strength Training, Powerlifting",
                "certification": "NASM-CPT, CSCS",
                "experience": 8,
                "password": "trainer123"
            },
            {
                "name": "Sarah Williams",
                "email": "sarah.williams@fitnesscrm.com",
                "phone": "+1 (555) 100-0002",
                "specialization": "Cardio, HIIT, Weight Loss",
                "certification": "ACE-CPT",
                "experience": 5,
                "password": "trainer123"
            },
            {
                "name": "David Chen",
                "email": "david.chen@fitnesscrm.com",
                "phone": "+1 (555) 100-0003",
                "specialization": "Yoga, Flexibility, Rehabilitation",
                "certification": "RYT-500, NASM-CES",
                "experience": 10,
                "password": "trainer123"
            },
            {
                "name": "Jessica Brown",
                "email": "jessica.brown@fitnesscrm.com",
                "phone": "+1 (555) 100-0004",
                "specialization": "CrossFit, Functional Training",
                "certification": "CrossFit Level 2",
                "experience": 6,
                "password": "trainer123"
            },
        ]
        
        print("\n" + "=" * 60)
        print("Creating Trainers and User Accounts")
        print("=" * 60)
        
        trainer_count = 0
        for trainer_data in trainers_data:
            # Check if trainer already exists
            existing_trainer = Trainer.query.filter_by(email=trainer_data['email']).first()
            if existing_trainer:
                print(f"\n⊘ Trainer already exists: {trainer_data['name']} ({trainer_data['email']})")
                continue
            
            # Create trainer
            trainer = Trainer(
                name=trainer_data['name'],
                email=trainer_data['email'],
                phone=trainer_data['phone'],
                specialization=trainer_data['specialization'],
                certification=trainer_data['certification'],
                experience=trainer_data['experience']
            )
            db.session.add(trainer)
            db.session.flush()  # Get trainer ID
            
            # Create User account for trainer
            user = User(
                email=trainer_data['email'],
                password_hash=hash_password(trainer_data['password']),
                role='trainer',
                active=True
            )
            db.session.add(user)
            
            trainer_count += 1
            print(f"\n✓ Created trainer: {trainer_data['name']}")
            print(f"  Email: {trainer_data['email']}")
            print(f"  Password: {trainer_data['password']}")
            print(f"  Specialization: {trainer_data['specialization']}")
        
        db.session.commit()
        print(f"\n✓ Total trainers created: {trainer_count}")
        
        # Create clients with real email addresses
        clients_data = [
            {
                "name": "Emma Thompson",
                "email": "emma.thompson@example.com",
                "phone": "+1 (555) 200-0001",
                "age": 28,
                "goals": "Weight loss, improved cardiovascular health",
                "medical_conditions": "None",
                "password": "client123"
            },
            {
                "name": "James Martinez",
                "email": "james.martinez@example.com",
                "phone": "+1 (555) 200-0002",
                "age": 35,
                "goals": "Muscle gain, strength training",
                "medical_conditions": "None",
                "password": "client123"
            },
            {
                "name": "Lisa Anderson",
                "email": "lisa.anderson@example.com",
                "phone": "+1 (555) 200-0003",
                "age": 42,
                "goals": "Flexibility, stress reduction, back pain management",
                "medical_conditions": "Chronic lower back pain",
                "password": "client123"
            },
            {
                "name": "Robert Taylor",
                "email": "robert.taylor@example.com",
                "phone": "+1 (555) 200-0004",
                "age": 31,
                "goals": "Marathon training, endurance",
                "medical_conditions": "None",
                "password": "client123"
            },
            {
                "name": "Jennifer Lee",
                "email": "jennifer.lee@example.com",
                "phone": "+1 (555) 200-0005",
                "age": 26,
                "goals": "Toning, general fitness",
                "medical_conditions": "Mild asthma",
                "password": "client123"
            },
            {
                "name": "Michael Scott",
                "email": "michael.scott@example.com",
                "phone": "+1 (555) 200-0006",
                "age": 45,
                "goals": "Weight management, stress relief",
                "medical_conditions": "None",
                "password": "client123"
            },
            {
                "name": "Amanda Clark",
                "email": "amanda.clark@example.com",
                "phone": "+1 (555) 200-0007",
                "age": 33,
                "goals": "Athletic performance, competition prep",
                "medical_conditions": "None",
                "password": "client123"
            },
            {
                "name": "Daniel Kim",
                "email": "daniel.kim@example.com",
                "phone": "+1 (555) 200-0008",
                "age": 29,
                "goals": "Build muscle, improve posture",
                "medical_conditions": "None",
                "password": "client123"
            },
        ]
        
        print("\n" + "=" * 60)
        print("Creating Clients and User Accounts")
        print("=" * 60)
        
        client_count = 0
        for client_data in clients_data:
            # Check if client already exists
            existing_client = Client.query.filter_by(email=client_data['email']).first()
            if existing_client:
                print(f"\n⊘ Client already exists: {client_data['name']} ({client_data['email']})")
                continue
            
            # Create client
            client = Client(
                name=client_data['name'],
                email=client_data['email'],
                phone=client_data['phone'],
                age=client_data['age'],
                goals=client_data['goals'],
                medical_conditions=client_data['medical_conditions']
            )
            db.session.add(client)
            db.session.flush()  # Get client ID
            
            # Create User account for client
            user = User(
                email=client_data['email'],
                password_hash=hash_password(client_data['password']),
                role='client',
                active=True
            )
            db.session.add(user)
            
            client_count += 1
            print(f"\n✓ Created client: {client_data['name']}")
            print(f"  Email: {client_data['email']}")
            print(f"  Password: {client_data['password']}")
            print(f"  Age: {client_data['age']}")
            print(f"  Goals: {client_data['goals']}")
        
        db.session.commit()
        print(f"\n✓ Total clients created: {client_count}")
        
        # Create some sample assignments
        print("\n" + "=" * 60)
        print("Creating Sample Assignments")
        print("=" * 60)
        
        # Fetch created trainers and clients
        trainers = Trainer.query.all()
        clients = Client.query.all()
        
        if len(trainers) > 0 and len(clients) > 0:
            assignments_data = [
                {"trainer_email": "mike.johnson@fitnesscrm.com", "client_email": "james.martinez@example.com", 
                 "notes": "Focus on compound lifts and progressive overload"},
                {"trainer_email": "sarah.williams@fitnesscrm.com", "client_email": "emma.thompson@example.com",
                 "notes": "Starting with cardio base building, 3x per week"},
                {"trainer_email": "sarah.williams@fitnesscrm.com", "client_email": "robert.taylor@example.com",
                 "notes": "Marathon training plan - 16 week program"},
                {"trainer_email": "david.chen@fitnesscrm.com", "client_email": "lisa.anderson@example.com",
                 "notes": "Therapeutic yoga for back pain, 2x per week"},
                {"trainer_email": "sarah.williams@fitnesscrm.com", "client_email": "jennifer.lee@example.com",
                 "notes": "Circuit training and HIIT workouts"},
                {"trainer_email": "jessica.brown@fitnesscrm.com", "client_email": "amanda.clark@example.com",
                 "notes": "CrossFit competition prep, 5x per week"},
            ]
            
            assignment_count = 0
            for assignment_data in assignments_data:
                trainer = Trainer.query.filter_by(email=assignment_data['trainer_email']).first()
                client = Client.query.filter_by(email=assignment_data['client_email']).first()
                
                if trainer and client:
                    # Check if assignment already exists
                    existing = Assignment.query.filter_by(
                        trainer_id=trainer.id, 
                        client_id=client.id
                    ).first()
                    
                    if not existing:
                        assignment = Assignment(
                            trainer_id=trainer.id,
                            client_id=client.id,
                            notes=assignment_data['notes']
                        )
                        db.session.add(assignment)
                        assignment_count += 1
                        print(f"\n✓ Assigned {client.name} to {trainer.name}")
                        print(f"  Notes: {assignment_data['notes']}")
            
            db.session.commit()
            print(f"\n✓ Total assignments created: {assignment_count}")
        
        print("\n" + "=" * 60)
        print("Database Seeding Complete!")
        print("=" * 60)
        print("\n⚠️  IMPORTANT: Default passwords are set for development!")
        print("   Change these passwords in production!")
        print("\nLogin Credentials:")
        print("  Admin: admin@fitnesscrm.com / admin123")
        print("  Trainers: [email] / trainer123")
        print("  Clients: [email] / client123")
        print("=" * 60)

def clear_all_data():
    """Clear all users, trainers, clients, and assignments"""
    app = create_app()
    
    with app.app_context():
        print("\n⚠️  WARNING: This will delete ALL data from the database!")
        response = input("Type 'yes' to continue: ")
        
        if response.lower() != 'yes':
            print("Cancelled.")
            return
        
        print("\nClearing database...")
        
        # Delete in order of dependencies
        Assignment.query.delete()
        User.query.delete()
        Client.query.delete()
        Trainer.query.delete()
        
        db.session.commit()
        print("✓ All data cleared successfully!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'clear':
        clear_all_data()
    else:
        seed_accounts()
