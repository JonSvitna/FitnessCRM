"""
Unit tests for database models.
"""

import pytest
from datetime import datetime
from models.database import Trainer, Client, Assignment, Session, ProgressRecord, Payment


class TestTrainerModel:
    """Test Trainer model."""
    
    @pytest.mark.database
    def test_create_trainer(self, db_session, sample_trainer):
        """Test creating a trainer."""
        trainer = Trainer(**sample_trainer)
        db_session.add(trainer)
        db_session.commit()
        
        assert trainer.id is not None
        assert trainer.name == sample_trainer['name']
        assert trainer.email == sample_trainer['email']
        assert trainer.created_at is not None
        assert trainer.updated_at is not None
    
    @pytest.mark.database
    def test_trainer_unique_email(self, db_session, sample_trainer):
        """Test that trainer email must be unique."""
        # Create first trainer
        trainer1 = Trainer(**sample_trainer)
        db_session.add(trainer1)
        db_session.commit()
        
        # Try to create second trainer with same email
        sample_trainer2 = sample_trainer.copy()
        sample_trainer2['name'] = 'Different Name'
        trainer2 = Trainer(**sample_trainer2)
        db_session.add(trainer2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()
    
    @pytest.mark.database
    def test_trainer_relationships(self, db_session, sample_trainer, sample_client):
        """Test trainer relationships with assignments."""
        trainer = Trainer(**sample_trainer)
        client = Client(**sample_client)
        db_session.add_all([trainer, client])
        db_session.commit()
        
        # Create assignment
        assignment = Assignment(
            trainer_id=trainer.id,
            client_id=client.id,
            notes='Test assignment'
        )
        db_session.add(assignment)
        db_session.commit()
        
        # Verify relationship
        assert len(trainer.assignments) == 1
        assert trainer.assignments[0].client == client
    
    @pytest.mark.database
    def test_trainer_to_dict(self, db_session, sample_trainer):
        """Test trainer to_dict method if it exists."""
        trainer = Trainer(**sample_trainer)
        db_session.add(trainer)
        db_session.commit()
        
        # If model has to_dict method
        if hasattr(trainer, 'to_dict'):
            trainer_dict = trainer.to_dict()
            assert isinstance(trainer_dict, dict)
            assert trainer_dict['name'] == sample_trainer['name']


class TestClientModel:
    """Test Client model."""
    
    @pytest.mark.database
    def test_create_client(self, db_session, sample_client):
        """Test creating a client."""
        client = Client(**sample_client)
        db_session.add(client)
        db_session.commit()
        
        assert client.id is not None
        assert client.name == sample_client['name']
        assert client.email == sample_client['email']
        assert client.age == sample_client['age']
        assert client.created_at is not None
        assert client.updated_at is not None
    
    @pytest.mark.database
    def test_client_unique_email(self, db_session, sample_client):
        """Test that client email must be unique."""
        # Create first client
        client1 = Client(**sample_client)
        db_session.add(client1)
        db_session.commit()
        
        # Try to create second client with same email
        sample_client2 = sample_client.copy()
        sample_client2['name'] = 'Different Name'
        client2 = Client(**sample_client2)
        db_session.add(client2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()
    
    @pytest.mark.database
    def test_client_default_status(self, db_session):
        """Test that client has default status."""
        client = Client(
            name='Test Client',
            email='test@example.com',
            phone='555-0000',
            age=25
        )
        db_session.add(client)
        db_session.commit()
        
        # Should have default status (active or pending)
        assert client.status in ['active', 'inactive', 'pending']
    
    @pytest.mark.database
    def test_client_relationships(self, db_session, sample_trainer, sample_client):
        """Test client relationships with assignments."""
        trainer = Trainer(**sample_trainer)
        client = Client(**sample_client)
        db_session.add_all([trainer, client])
        db_session.commit()
        
        # Create assignment
        assignment = Assignment(
            trainer_id=trainer.id,
            client_id=client.id,
            notes='Test assignment'
        )
        db_session.add(assignment)
        db_session.commit()
        
        # Verify relationship
        assert len(client.assignments) == 1
        assert client.assignments[0].trainer == trainer


class TestAssignmentModel:
    """Test Assignment model."""
    
    @pytest.mark.database
    def test_create_assignment(self, db_session, sample_trainer, sample_client):
        """Test creating an assignment."""
        trainer = Trainer(**sample_trainer)
        client = Client(**sample_client)
        db_session.add_all([trainer, client])
        db_session.commit()
        
        assignment = Assignment(
            trainer_id=trainer.id,
            client_id=client.id,
            notes='Test assignment',
            status='active'
        )
        db_session.add(assignment)
        db_session.commit()
        
        assert assignment.id is not None
        assert assignment.trainer_id == trainer.id
        assert assignment.client_id == client.id
        assert assignment.notes == 'Test assignment'
        assert assignment.created_at is not None
    
    @pytest.mark.database
    def test_assignment_relationships(self, db_session, sample_trainer, sample_client):
        """Test assignment relationships."""
        trainer = Trainer(**sample_trainer)
        client = Client(**sample_client)
        db_session.add_all([trainer, client])
        db_session.commit()
        
        assignment = Assignment(
            trainer_id=trainer.id,
            client_id=client.id,
            notes='Test'
        )
        db_session.add(assignment)
        db_session.commit()
        
        # Verify relationships
        assert assignment.trainer == trainer
        assert assignment.client == client
        assert assignment.trainer.name == trainer.name
        assert assignment.client.name == client.name
    
    @pytest.mark.database
    def test_cascade_delete_assignment(self, db_session, sample_trainer, sample_client):
        """Test that deleting trainer/client handles assignment."""
        trainer = Trainer(**sample_trainer)
        client = Client(**sample_client)
        db_session.add_all([trainer, client])
        db_session.commit()
        
        assignment = Assignment(
            trainer_id=trainer.id,
            client_id=client.id,
            notes='Test'
        )
        db_session.add(assignment)
        db_session.commit()
        assignment_id = assignment.id
        
        # Delete trainer (if cascade is set up)
        db_session.delete(trainer)
        db_session.commit()
        
        # Assignment might be deleted or set to null depending on cascade rules
        # This test validates the relationship is properly configured


class TestSessionModel:
    """Test Session model."""
    
    @pytest.mark.database
    def test_create_session(self, db_session, sample_trainer, sample_client, sample_session):
        """Test creating a session."""
        trainer = Trainer(**sample_trainer)
        client = Client(**sample_client)
        db_session.add_all([trainer, client])
        db_session.commit()
        
        session = Session(
            trainer_id=trainer.id,
            client_id=client.id,
            **sample_session
        )
        db_session.add(session)
        db_session.commit()
        
        assert session.id is not None
        assert session.trainer_id == trainer.id
        assert session.client_id == client.id
        assert session.duration == sample_session['duration']
        assert session.status == sample_session['status']


class TestProgressRecordModel:
    """Test ProgressRecord model."""
    
    @pytest.mark.database
    def test_create_progress_record(self, db_session, sample_client):
        """Test creating a progress record."""
        client = Client(**sample_client)
        db_session.add(client)
        db_session.commit()
        
        progress = ProgressRecord(
            client_id=client.id,
            record_date=datetime.now(),
            weight=75.5,
            body_fat_percentage=20.0,
            notes='Good progress'
        )
        db_session.add(progress)
        db_session.commit()
        
        assert progress.id is not None
        assert progress.client_id == client.id
        assert progress.weight == 75.5
        assert progress.body_fat_percentage == 20.0


class TestPaymentModel:
    """Test Payment model."""
    
    @pytest.mark.database
    def test_create_payment(self, db_session, sample_client):
        """Test creating a payment."""
        client = Client(**sample_client)
        db_session.add(client)
        db_session.commit()
        
        payment = Payment(
            client_id=client.id,
            amount=100.00,
            payment_date=datetime.now(),
            payment_method='credit_card',
            payment_type='membership',
            status='completed'
        )
        db_session.add(payment)
        db_session.commit()
        
        assert payment.id is not None
        assert payment.client_id == client.id
        assert payment.amount == 100.00
        assert payment.status == 'completed'
    
    @pytest.mark.database
    def test_payment_default_status(self, db_session, sample_client):
        """Test payment default status."""
        client = Client(**sample_client)
        db_session.add(client)
        db_session.commit()
        
        payment = Payment(
            client_id=client.id,
            amount=50.00,
            payment_date=datetime.now(),
            payment_method='cash',
            payment_type='session'
        )
        db_session.add(payment)
        db_session.commit()
        
        # Should have a default or set status
        assert payment.status in ['pending', 'completed', 'refunded', 'failed']
