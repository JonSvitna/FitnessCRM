"""
Unit tests for main API routes (trainers, clients, CRM).
"""

import pytest
from models.database import Trainer, Client, Assignment


class TestTrainerRoutes:
    """Test trainer API endpoints."""
    
    @pytest.mark.api
    def test_get_trainers_empty(self, client):
        """Test GET /api/trainers with no trainers."""
        response = client.get('/api/trainers')
        assert response.status_code == 200
        data = response.get_json()
        # Should return either empty list or dict with trainers key
        assert isinstance(data, (list, dict))
    
    @pytest.mark.api
    def test_create_trainer(self, client, sample_trainer):
        """Test POST /api/trainers creates a trainer."""
        response = client.post('/api/trainers', json=sample_trainer)
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'id' in data
        assert data['name'] == sample_trainer['name']
        assert data['email'] == sample_trainer['email']
        assert data['phone'] == sample_trainer['phone']
    
    @pytest.mark.api
    def test_create_trainer_missing_required_fields(self, client):
        """Test POST /api/trainers with missing required fields."""
        incomplete_trainer = {
            'name': 'John Trainer'
            # Missing email
        }
        response = client.post('/api/trainers', json=incomplete_trainer)
        # Should return 400 or 422 for validation error, not 500
        assert response.status_code in [400, 422]
    
    @pytest.mark.api
    def test_get_trainer_by_id(self, client, db_session, sample_trainer):
        """Test GET /api/trainers/<id> returns specific trainer."""
        # Create trainer in database
        trainer = Trainer(**sample_trainer)
        db_session.add(trainer)
        db_session.commit()
        
        # Get trainer
        response = client.get(f'/api/trainers/{trainer.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['id'] == trainer.id
        assert data['name'] == trainer.name
        assert data['email'] == trainer.email
    
    @pytest.mark.api
    def test_get_nonexistent_trainer(self, client):
        """Test GET /api/trainers/<id> with nonexistent ID."""
        response = client.get('/api/trainers/99999')
        assert response.status_code == 404
    
    @pytest.mark.api
    def test_update_trainer(self, client, db_session, sample_trainer):
        """Test PUT /api/trainers/<id> updates trainer."""
        # Create trainer
        trainer = Trainer(**sample_trainer)
        db_session.add(trainer)
        db_session.commit()
        trainer_id = trainer.id
        
        # Update trainer
        update_data = {
            'name': 'Updated Trainer Name',
            'hourly_rate': 100.00
        }
        response = client.put(f'/api/trainers/{trainer_id}', json=update_data)
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['name'] == 'Updated Trainer Name'
        assert data['hourly_rate'] == 100.00
    
    @pytest.mark.api
    def test_delete_trainer(self, client, db_session, sample_trainer):
        """Test DELETE /api/trainers/<id> deletes trainer."""
        # Create trainer
        trainer = Trainer(**sample_trainer)
        db_session.add(trainer)
        db_session.commit()
        trainer_id = trainer.id
        
        # Delete trainer
        response = client.delete(f'/api/trainers/{trainer_id}')
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get(f'/api/trainers/{trainer_id}')
        assert response.status_code == 404


class TestClientRoutes:
    """Test client API endpoints."""
    
    @pytest.mark.api
    def test_get_clients_empty(self, client):
        """Test GET /api/clients with no clients."""
        response = client.get('/api/clients')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, (list, dict))
    
    @pytest.mark.api
    def test_create_client(self, client, sample_client):
        """Test POST /api/clients creates a client."""
        response = client.post('/api/clients', json=sample_client)
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'id' in data
        assert data['name'] == sample_client['name']
        assert data['email'] == sample_client['email']
        assert data['age'] == sample_client['age']
    
    @pytest.mark.api
    def test_create_client_missing_required_fields(self, client):
        """Test POST /api/clients with missing required fields."""
        incomplete_client = {
            'name': 'Jane Client'
            # Missing email
        }
        response = client.post('/api/clients', json=incomplete_client)
        # Should return 400 or 422 for validation error, not 500
        assert response.status_code in [400, 422]
    
    @pytest.mark.api
    def test_get_client_by_id(self, client, db_session, sample_client):
        """Test GET /api/clients/<id> returns specific client."""
        # Create client
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        # Get client
        response = client.get(f'/api/clients/{client_obj.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['id'] == client_obj.id
        assert data['name'] == client_obj.name
        assert data['email'] == client_obj.email
    
    @pytest.mark.api
    def test_get_nonexistent_client(self, client):
        """Test GET /api/clients/<id> with nonexistent ID."""
        response = client.get('/api/clients/99999')
        assert response.status_code == 404
    
    @pytest.mark.api
    def test_update_client(self, client, db_session, sample_client):
        """Test PUT /api/clients/<id> updates client."""
        # Create client
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        client_id = client_obj.id
        
        # Update client
        update_data = {
            'name': 'Updated Client Name',
            'goals': 'New fitness goals'
        }
        response = client.put(f'/api/clients/{client_id}', json=update_data)
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['name'] == 'Updated Client Name'
        assert data['goals'] == 'New fitness goals'
    
    @pytest.mark.api
    def test_delete_client(self, client, db_session, sample_client):
        """Test DELETE /api/clients/<id> deletes client."""
        # Create client
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        client_id = client_obj.id
        
        # Delete client
        response = client.delete(f'/api/clients/{client_id}')
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get(f'/api/clients/{client_id}')
        assert response.status_code == 404


class TestCRMRoutes:
    """Test CRM management endpoints."""
    
    @pytest.mark.api
    def test_get_dashboard_stats(self, client):
        """Test GET /api/crm/dashboard returns stats."""
        response = client.get('/api/crm/dashboard')
        assert response.status_code == 200
        data = response.get_json()
        
        # Dashboard should have key stats
        assert 'total_trainers' in data or 'trainers' in data
        assert 'total_clients' in data or 'clients' in data
    
    @pytest.mark.api
    def test_get_crm_stats(self, client):
        """Test GET /api/crm/stats returns statistics."""
        response = client.get('/api/crm/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
    
    @pytest.mark.api
    def test_create_assignment(self, client, db_session, sample_trainer, sample_client):
        """Test POST /api/crm/assign creates assignment."""
        # Create trainer and client
        trainer = Trainer(**sample_trainer)
        client_obj = Client(**sample_client)
        db_session.add_all([trainer, client_obj])
        db_session.commit()
        
        # Create assignment
        assignment_data = {
            'trainer_id': trainer.id,
            'client_id': client_obj.id,
            'notes': 'Initial assignment'
        }
        response = client.post('/api/crm/assign', json=assignment_data)
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'id' in data
        assert data['trainer_id'] == trainer.id
        assert data['client_id'] == client_obj.id
    
    @pytest.mark.api
    def test_get_assignments(self, client, db_session, sample_trainer, sample_client):
        """Test GET /api/crm/assignments returns all assignments."""
        # Create trainer, client, and assignment
        trainer = Trainer(**sample_trainer)
        client_obj = Client(**sample_client)
        db_session.add_all([trainer, client_obj])
        db_session.commit()
        
        assignment = Assignment(
            trainer_id=trainer.id,
            client_id=client_obj.id,
            notes='Test assignment'
        )
        db_session.add(assignment)
        db_session.commit()
        
        # Get assignments
        response = client.get('/api/crm/assignments')
        assert response.status_code == 200
        data = response.get_json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
    
    @pytest.mark.api
    def test_delete_assignment(self, client, db_session, sample_trainer, sample_client):
        """Test DELETE /api/crm/assignments/<id> deletes assignment."""
        # Create trainer, client, and assignment
        trainer = Trainer(**sample_trainer)
        client_obj = Client(**sample_client)
        db_session.add_all([trainer, client_obj])
        db_session.commit()
        
        assignment = Assignment(
            trainer_id=trainer.id,
            client_id=client_obj.id,
            notes='Test assignment'
        )
        db_session.add(assignment)
        db_session.commit()
        assignment_id = assignment.id
        
        # Delete assignment
        response = client.delete(f'/api/crm/assignments/{assignment_id}')
        assert response.status_code == 200


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    @pytest.mark.api
    def test_health_check(self, client):
        """Test GET /api/health returns healthy status."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'status' in data
        assert data['status'] in ['healthy', 'ok']
