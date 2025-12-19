"""
Unit tests for measurement/progress tracking API routes.
"""

import pytest
from datetime import datetime
from models.database import ProgressRecord, Client


class TestMeasurementRoutes:
    """Test measurement/progress tracking API endpoints."""
    
    @pytest.mark.api
    def test_get_measurements(self, client):
        """Test GET /api/measurements returns measurement list."""
        response = client.get('/api/measurements')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, (list, dict))
    
    @pytest.mark.api
    def test_create_measurement(self, client, db_session, sample_client):
        """Test POST /api/measurements creates a measurement."""
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        measurement_data = {
            'client_id': client_obj.id,
            'record_date': datetime.now().isoformat(),
            'weight': 180.5,
            'body_fat_percentage': 18.5,
            'measurements': {
                'chest': 40,
                'waist': 32,
                'hips': 38,
                'biceps': 14
            },
            'notes': 'Feeling strong'
        }
        response = client.post('/api/measurements', json=measurement_data)
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'id' in data
        assert data['client_id'] == client_obj.id
        assert data['weight'] == 180.5
    
    @pytest.mark.api
    def test_get_measurement_by_id(self, client, db_session, sample_client):
        """Test GET /api/measurements/<id> returns specific measurement."""
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        measurement = ProgressRecord(
            client_id=client_obj.id,
            record_date=datetime.now(),
            weight=175.0,
            body_fat_percentage=20.0
        )
        db_session.add(measurement)
        db_session.commit()
        
        response = client.get(f'/api/measurements/{measurement.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['id'] == measurement.id
        assert data['weight'] == 175.0
    
    @pytest.mark.api
    def test_update_measurement(self, client, db_session, sample_client):
        """Test PUT /api/measurements/<id> updates measurement."""
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        measurement = ProgressRecord(
            client_id=client_obj.id,
            record_date=datetime.now(),
            weight=180.0,
            body_fat_percentage=19.0
        )
        db_session.add(measurement)
        db_session.commit()
        
        update_data = {
            'weight': 178.5,
            'notes': 'Lost 1.5 pounds'
        }
        response = client.put(f'/api/measurements/{measurement.id}', json=update_data)
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['weight'] == 178.5
        assert data['notes'] == 'Lost 1.5 pounds'
    
    @pytest.mark.api
    def test_delete_measurement(self, client, db_session, sample_client):
        """Test DELETE /api/measurements/<id> deletes measurement."""
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        measurement = ProgressRecord(
            client_id=client_obj.id,
            record_date=datetime.now(),
            weight=175.0
        )
        db_session.add(measurement)
        db_session.commit()
        measurement_id = measurement.id
        
        response = client.delete(f'/api/measurements/{measurement_id}')
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get(f'/api/measurements/{measurement_id}')
        assert response.status_code == 404
    
    @pytest.mark.api
    def test_filter_measurements_by_client(self, client, db_session, sample_client):
        """Test filtering measurements by client_id."""
        client1 = Client(**sample_client)
        client2_data = sample_client.copy()
        client2_data['email'] = 'client2@example.com'
        client2 = Client(**client2_data)
        db_session.add_all([client1, client2])
        db_session.commit()
        
        measurement1 = ProgressRecord(client_id=client1.id, record_date=datetime.now(), weight=180.0)
        measurement2 = ProgressRecord(client_id=client2.id, record_date=datetime.now(), weight=150.0)
        db_session.add_all([measurement1, measurement2])
        db_session.commit()
        
        response = client.get(f'/api/measurements?client_id={client1.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        # Handle both list and dict responses
        measurements = data if isinstance(data, list) else data.get('measurements', data.get('data', []))
        if measurements:
            assert all(m['client_id'] == client1.id for m in measurements)
    
    @pytest.mark.integration
    def test_measurement_history(self, client, db_session, sample_client):
        """Test getting measurement history for a client."""
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        # Create multiple measurements over time
        from datetime import timedelta
        base_date = datetime.now()
        
        for i in range(5):
            measurement = ProgressRecord(
                client_id=client_obj.id,
                record_date=base_date - timedelta(days=i*7),
                weight=185.0 - i,
                body_fat_percentage=20.0 - (i * 0.5)
            )
            db_session.add(measurement)
        db_session.commit()
        
        # Get measurements for client
        response = client.get(f'/api/measurements?client_id={client_obj.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        # Should have multiple measurements
        measurements = data if isinstance(data, list) else data.get('measurements', data.get('data', []))
        assert len(measurements) >= 5
    
    @pytest.mark.api
    def test_create_measurement_missing_client_id(self, client):
        """Test POST /api/measurements without client_id."""
        measurement_data = {
            'weight': 180.0,
            'record_date': datetime.now().isoformat()
        }
        response = client.post('/api/measurements', json=measurement_data)
        assert response.status_code in [400, 422]
