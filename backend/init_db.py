#!/usr/bin/env python3
"""
Database initialization script for Fitness CRM
Creates all tables and optionally seeds with sample data
"""

from app import create_app
from models.database import db, Trainer, Client, Assignment
import sys

def init_database(seed=False):
    """Initialize the database with tables and optional seed data"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        
        if seed:
            print("\nSeeding database with sample data...")
            seed_database()
            print("✓ Database seeded successfully!")

def seed_database():
    """Seed the database with sample data"""
    
    # Check if data already exists
    if Trainer.query.first() is not None:
        print("! Database already contains data. Skipping seed.")
        return
    
    # Create sample trainers
    trainers = [
        Trainer(
            name="Mike Johnson",
            email="mike.johnson@fitcrm.com",
            phone="+1 (555) 100-0001",
            specialization="Strength Training, Powerlifting",
            certification="NASM-CPT, CSCS",
            experience=8
        ),
        Trainer(
            name="Sarah Williams",
            email="sarah.williams@fitcrm.com",
            phone="+1 (555) 100-0002",
            specialization="Cardio, HIIT, Weight Loss",
            certification="ACE-CPT",
            experience=5
        ),
        Trainer(
            name="David Chen",
            email="david.chen@fitcrm.com",
            phone="+1 (555) 100-0003",
            specialization="Yoga, Flexibility, Rehabilitation",
            certification="RYT-500, NASM-CES",
            experience=10
        ),
    ]
    
    for trainer in trainers:
        db.session.add(trainer)
    
    db.session.commit()
    print(f"  ✓ Added {len(trainers)} trainers")
    
    # Create sample clients
    clients = [
        Client(
            name="Emma Thompson",
            email="emma.thompson@example.com",
            phone="+1 (555) 200-0001",
            age=28,
            goals="Weight loss, improved cardiovascular health",
            medical_conditions="None"
        ),
        Client(
            name="James Martinez",
            email="james.martinez@example.com",
            phone="+1 (555) 200-0002",
            age=35,
            goals="Muscle gain, strength training",
            medical_conditions="None"
        ),
        Client(
            name="Lisa Anderson",
            email="lisa.anderson@example.com",
            phone="+1 (555) 200-0003",
            age=42,
            goals="Flexibility, stress reduction, back pain management",
            medical_conditions="Chronic lower back pain"
        ),
        Client(
            name="Robert Taylor",
            email="robert.taylor@example.com",
            phone="+1 (555) 200-0004",
            age=31,
            goals="Marathon training, endurance",
            medical_conditions="None"
        ),
        Client(
            name="Jennifer Lee",
            email="jennifer.lee@example.com",
            phone="+1 (555) 200-0005",
            age=26,
            goals="Toning, general fitness",
            medical_conditions="Mild asthma"
        ),
    ]
    
    for client in clients:
        db.session.add(client)
    
    db.session.commit()
    print(f"  ✓ Added {len(clients)} clients")
    
    # Create sample assignments
    assignments = [
        Assignment(
            trainer_id=1,  # Mike Johnson
            client_id=2,   # James Martinez
            notes="Focus on compound lifts and progressive overload"
        ),
        Assignment(
            trainer_id=2,  # Sarah Williams
            client_id=1,   # Emma Thompson
            notes="Starting with cardio base building, 3x per week"
        ),
        Assignment(
            trainer_id=2,  # Sarah Williams
            client_id=4,   # Robert Taylor
            notes="Marathon training plan - 16 week program"
        ),
        Assignment(
            trainer_id=3,  # David Chen
            client_id=3,   # Lisa Anderson
            notes="Therapeutic yoga for back pain, 2x per week"
        ),
        Assignment(
            trainer_id=2,  # Sarah Williams
            client_id=5,   # Jennifer Lee
            notes="Circuit training and HIIT workouts"
        ),
    ]
    
    for assignment in assignments:
        db.session.add(assignment)
    
    db.session.commit()
    print(f"  ✓ Added {len(assignments)} assignments")

def clear_database():
    """Clear all data from the database"""
    app = create_app()
    
    with app.app_context():
        print("Clearing database...")
        db.drop_all()
        print("✓ Database cleared successfully!")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'seed':
            init_database(seed=True)
        elif command == 'clear':
            clear_database()
        elif command == 'reset':
            clear_database()
            init_database(seed=True)
        else:
            print(f"Unknown command: {command}")
            print("Usage: python init_db.py [seed|clear|reset]")
            print("  seed  - Create tables and add sample data")
            print("  clear - Drop all tables")
            print("  reset - Drop all tables and recreate with sample data")
    else:
        init_database()
