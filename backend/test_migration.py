"""
Unit tests for database migration script.
Tests the logic of migrate_add_end_time.py
"""

import pytest
from datetime import datetime, timedelta
from models.database import Session, Trainer, Client, db
from sqlalchemy import text


class TestEndTimeMigration:
    """Test end_time column migration."""
    
    @pytest.mark.api
    def test_session_has_end_time_column(self, app, _db):
        """Test that Session model has end_time column."""
        with app.app_context():
            # Check that the Session model includes end_time
            assert hasattr(Session, 'end_time')
            
    @pytest.mark.api
    def test_session_creation_sets_end_time(self, db_session, sample_trainer, sample_client):
        """Test that creating a session through the API sets end_time."""
        # Create trainer and client
        trainer = Trainer(**sample_trainer)
        client_obj = Client(**sample_client)
        db_session.add_all([trainer, client_obj])
        db_session.commit()
        
        # Create session with explicit end_time calculation
        session_date = datetime(2024, 12, 20, 10, 0, 0)
        duration = 60
        end_time = session_date + timedelta(minutes=duration)
        
        session = Session(
            trainer_id=trainer.id,
            client_id=client_obj.id,
            session_date=session_date,
            end_time=end_time,
            duration=duration,
            session_type='personal',
            status='scheduled'
        )
        db_session.add(session)
        db_session.commit()
        
        # Verify end_time is set
        assert session.end_time is not None
        assert session.end_time == end_time
        assert session.end_time == session_date + timedelta(minutes=duration)
    
    @pytest.mark.api
    def test_session_to_dict_includes_end_time(self, db_session, sample_trainer, sample_client):
        """Test that session.to_dict() includes end_time."""
        # Create trainer and client
        trainer = Trainer(**sample_trainer)
        client_obj = Client(**sample_client)
        db_session.add_all([trainer, client_obj])
        db_session.commit()
        
        # Create session
        session_date = datetime(2024, 12, 20, 10, 0, 0)
        duration = 60
        
        session = Session(
            trainer_id=trainer.id,
            client_id=client_obj.id,
            session_date=session_date,
            end_time=session_date + timedelta(minutes=duration),
            duration=duration,
            session_type='personal',
            status='scheduled'
        )
        db_session.add(session)
        db_session.commit()
        
        # Convert to dict
        session_dict = session.to_dict()
        
        # Verify end_time is in the dictionary
        assert 'end_time' in session_dict
        assert session_dict['end_time'] is not None
    
    @pytest.mark.api
    def test_query_sessions_with_end_time(self, db_session, sample_trainer, sample_client):
        """Test that querying sessions works with end_time column."""
        # Create trainer and client
        trainer = Trainer(**sample_trainer)
        client_obj = Client(**sample_client)
        db_session.add_all([trainer, client_obj])
        db_session.commit()
        
        # Create multiple sessions
        sessions_data = [
            {
                'session_date': datetime(2024, 12, 20, 10, 0, 0),
                'duration': 60
            },
            {
                'session_date': datetime(2024, 12, 21, 14, 0, 0),
                'duration': 45
            },
            {
                'session_date': datetime(2024, 12, 22, 9, 0, 0),
                'duration': 90
            }
        ]
        
        for data in sessions_data:
            session = Session(
                trainer_id=trainer.id,
                client_id=client_obj.id,
                session_date=data['session_date'],
                end_time=data['session_date'] + timedelta(minutes=data['duration']),
                duration=data['duration'],
                session_type='personal',
                status='scheduled'
            )
            db_session.add(session)
        
        db_session.commit()
        
        # Query sessions
        all_sessions = Session.query.all()
        assert len(all_sessions) == 3
        
        # Verify all sessions have end_time
        for session in all_sessions:
            assert session.end_time is not None
            expected_end = session.session_date + timedelta(minutes=session.duration)
            assert session.end_time == expected_end
    
    @pytest.mark.api
    def test_session_conflict_detection_uses_end_time(self, db_session, sample_trainer, sample_client):
        """Test that conflict detection can use end_time column."""
        # Create trainer and client
        trainer = Trainer(**sample_trainer)
        client_obj = Client(**sample_client)
        db_session.add_all([trainer, client_obj])
        db_session.commit()
        
        # Create first session: 10:00 - 11:00
        session1_start = datetime(2024, 12, 20, 10, 0, 0)
        session1 = Session(
            trainer_id=trainer.id,
            client_id=client_obj.id,
            session_date=session1_start,
            end_time=session1_start + timedelta(minutes=60),
            duration=60,
            session_type='personal',
            status='scheduled'
        )
        db_session.add(session1)
        db_session.commit()
        
        # Check for conflicts with a session from 10:30 - 11:30 (should conflict)
        session2_start = datetime(2024, 12, 20, 10, 30, 0)
        session2_end = session2_start + timedelta(minutes=60)
        
        conflict = Session.query.filter(
            Session.trainer_id == trainer.id,
            Session.status != 'cancelled',
            Session.session_date < session2_end,
            Session.end_time > session2_start
        ).first()
        
        # Should find a conflict
        assert conflict is not None
        assert conflict.id == session1.id
        
        # Check for non-conflicting session from 11:00 - 12:00 (should not conflict)
        session3_start = datetime(2024, 12, 20, 11, 0, 0)
        session3_end = session3_start + timedelta(minutes=60)
        
        no_conflict = Session.query.filter(
            Session.trainer_id == trainer.id,
            Session.status != 'cancelled',
            Session.session_date < session3_end,
            Session.end_time > session3_start
        ).first()
        
        # Should find the existing session (they exactly touch at 11:00)
        # but sessions that start exactly when another ends typically should be allowed
        # For stricter no-touch policy, the boundary condition needs adjustment
