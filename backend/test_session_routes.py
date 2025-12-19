"""
Unit tests for session API routes.
"""

import pytest
from datetime import datetime, timedelta
from models.database import Session, Trainer, Client


class TestSessionRoutes:
    """Test session API endpoints."""
    
    @pytest.mark.api
    def test_get_sessions_empty(self, client):
        """Test GET /api/sessions with no sessions."""
        response = client.get('/api/sessions')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    @pytest.mark.api
    def test_create_session(self, client, db_session, sample_trainer, sample_client, sample_session):
        """Test POST /api/sessions creates a session."""
        # Create trainer and client first
        trainer = Trainer(**sample_trainer)
        client_obj = Client(**sample_client)
        db_session.add_all([trainer, client_obj])
        db_session.commit()
        
        # Create session
        session_data = {
            **sample_session,
            'trainer_id': trainer.id,
            'client_id': client_obj.id
        }
        response = client.post('/api/sessions', json=session_data)
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'id' in data
        assert data['trainer_id'] == trainer.id
        assert data['client_id'] == client_obj.id
        assert data['duration'] == sample_session['duration']
    
    @pytest.mark.api
    def test_get_session_by_id(self, client, db_session, sample_trainer, sample_client, sample_session):
        """Test GET /api/sessions/<id> returns specific session."""
        # Create trainer, client, and session
        trainer = Trainer(**sample_trainer)
        client_obj = Client(**sample_client)
        db_session.add_all([trainer, client_obj])
        db_session.commit()
        
        session = Session(
            trainer_id=trainer.id,
            client_id=client_obj.id,
            **sample_session
        )
        db_session.add(session)
        db_session.commit()
        
        # Get session
        response = client.get(f'/api/sessions/{session.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['id'] == session.id
        assert data['trainer_id'] == trainer.id
        assert data['client_id'] == client_obj.id
    
    @pytest.mark.api
    def test_update_session(self, client, db_session, sample_trainer, sample_client, sample_session):
        """Test PUT /api/sessions/<id> updates session."""
        # Create trainer, client, and session
        trainer = Trainer(**sample_trainer)
        client_obj = Client(**sample_client)
        db_session.add_all([trainer, client_obj])
        db_session.commit()
        
        session = Session(
            trainer_id=trainer.id,
            client_id=client_obj.id,
            **sample_session
        )
        db_session.add(session)
        db_session.commit()
        session_id = session.id
        
        # Update session
        update_data = {
            'status': 'completed',
            'notes': 'Session completed successfully'
        }
        response = client.put(f'/api/sessions/{session_id}', json=update_data)
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['status'] == 'completed'
        assert data['notes'] == 'Session completed successfully'
    
    @pytest.mark.api
    def test_delete_session(self, client, db_session, sample_trainer, sample_client, sample_session):
        """Test DELETE /api/sessions/<id> deletes session."""
        # Create trainer, client, and session
        trainer = Trainer(**sample_trainer)
        client_obj = Client(**sample_client)
        db_session.add_all([trainer, client_obj])
        db_session.commit()
        
        session = Session(
            trainer_id=trainer.id,
            client_id=client_obj.id,
            **sample_session
        )
        db_session.add(session)
        db_session.commit()
        session_id = session.id
        
        # Delete session
        response = client.delete(f'/api/sessions/{session_id}')
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get(f'/api/sessions/{session_id}')
        assert response.status_code == 404
    
    @pytest.mark.api
    def test_filter_sessions_by_trainer(self, client, db_session, sample_trainer, sample_client, sample_session):
        """Test filtering sessions by trainer_id."""
        # Create trainers and clients
        trainer1 = Trainer(**sample_trainer)
        trainer2_data = sample_trainer.copy()
        trainer2_data['email'] = 'trainer2@example.com'
        trainer2 = Trainer(**trainer2_data)
        client_obj = Client(**sample_client)
        db_session.add_all([trainer1, trainer2, client_obj])
        db_session.commit()
        
        # Create sessions for different trainers
        session1 = Session(
            trainer_id=trainer1.id,
            client_id=client_obj.id,
            **sample_session
        )
        session2_data = sample_session.copy()
        session2_data['session_date'] = (datetime.now() + timedelta(days=1)).isoformat()
        session2 = Session(
            trainer_id=trainer2.id,
            client_id=client_obj.id,
            **session2_data
        )
        db_session.add_all([session1, session2])
        db_session.commit()
        
        # Filter by trainer1
        response = client.get(f'/api/sessions?trainer_id={trainer1.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        assert len(data) >= 1
        assert all(s['trainer_id'] == trainer1.id for s in data)
    
    @pytest.mark.api
    def test_filter_sessions_by_status(self, client, db_session, sample_trainer, sample_client, sample_session):
        """Test filtering sessions by status."""
        # Create trainer and client
        trainer = Trainer(**sample_trainer)
        client_obj = Client(**sample_client)
        db_session.add_all([trainer, client_obj])
        db_session.commit()
        
        # Create sessions with different statuses
        session1 = Session(
            trainer_id=trainer.id,
            client_id=client_obj.id,
            **sample_session
        )
        session2_data = sample_session.copy()
        session2_data['status'] = 'completed'
        session2_data['session_date'] = (datetime.now() + timedelta(days=1)).isoformat()
        session2 = Session(
            trainer_id=trainer.id,
            client_id=client_obj.id,
            **session2_data
        )
        db_session.add_all([session1, session2])
        db_session.commit()
        
        # Filter by completed status
        response = client.get('/api/sessions?status=completed')
        assert response.status_code == 200
        data = response.get_json()
        
        assert all(s['status'] == 'completed' for s in data)
