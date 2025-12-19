"""
Pytest configuration and fixtures for FitnessCRM backend tests.
"""

import os
import pytest
from app import create_app
from models.database import db


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    os.environ['TESTING'] = 'true'
    os.environ['DATABASE_URL'] = os.environ.get(
        'TEST_DATABASE_URL',
        'postgresql://localhost/fitnesscrm_test'
    )
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['WTF_CSRF_ENABLED'] = False
    
    return app


@pytest.fixture(scope='session')
def _db(app):
    """Create database for testing."""
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()


@pytest.fixture(scope='function')
def db_session(app, _db):
    """Create a new database session for a test."""
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        
        session = _db.session
        session.begin_nested()
        
        yield session
        
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


# Sample data fixtures
@pytest.fixture
def sample_trainer():
    """Sample trainer data."""
    return {
        'name': 'John Trainer',
        'email': 'john@example.com',
        'phone': '555-0100',
        'specialization': 'Strength Training',
        'certification': 'ACE-CPT',
        'experience': 5,
        'bio': 'Experienced strength trainer',
        'hourly_rate': 75.00,
        'active': True
    }


@pytest.fixture
def sample_client():
    """Sample client data."""
    return {
        'name': 'Jane Client',
        'email': 'jane@example.com',
        'phone': '555-0200',
        'age': 30,
        'goals': 'Weight loss and fitness',
        'medical_conditions': 'None',
        'emergency_contact': 'John Doe',
        'emergency_phone': '555-0300',
        'status': 'active',
        'membership_type': 'monthly'
    }


@pytest.fixture
def sample_session():
    """Sample session data."""
    return {
        'session_date': '2024-12-20T10:00:00',
        'duration': 60,
        'session_type': 'personal',
        'notes': 'Regular training session',
        'status': 'scheduled'
    }


@pytest.fixture
def auth_headers():
    """Sample authentication headers."""
    return {
        'Authorization': 'Bearer test_token',
        'Content-Type': 'application/json'
    }
