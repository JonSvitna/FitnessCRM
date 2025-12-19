"""
Unit tests for analytics API routes.
"""

import pytest
from datetime import datetime
from models.database import Client, Trainer, Session, Payment, Assignment


class TestAnalyticsRoutes:
    """Test analytics API endpoints."""
    
    @pytest.mark.api
    def test_get_client_retention(self, client):
        """Test GET /api/analytics/clients/retention returns retention metrics."""
        response = client.get('/api/analytics/clients/retention')
        assert response.status_code == 200
        data = response.get_json()
        
        # Should contain retention metrics
        assert 'total_active' in data or 'retention_rate' in data
    
    @pytest.mark.api
    def test_get_client_engagement(self, client):
        """Test GET /api/analytics/clients/engagement returns engagement metrics."""
        response = client.get('/api/analytics/clients/engagement')
        assert response.status_code == 200
        data = response.get_json()
        
        assert isinstance(data, dict)
    
    @pytest.mark.api
    def test_get_client_lifetime_value(self, client):
        """Test GET /api/analytics/clients/lifetime-value returns LTV metrics."""
        response = client.get('/api/analytics/clients/lifetime-value')
        assert response.status_code == 200
        data = response.get_json()
        
        assert isinstance(data, dict)
    
    @pytest.mark.api
    def test_get_trainer_performance(self, client):
        """Test GET /api/analytics/trainers/performance returns trainer metrics."""
        response = client.get('/api/analytics/trainers/performance')
        assert response.status_code == 200
        data = response.get_json()
        
        # Should return list of trainer performance data
        assert isinstance(data, list) or 'trainers' in data
    
    @pytest.mark.api
    def test_get_trainer_performance_by_id(self, client, db_session, sample_trainer):
        """Test GET /api/analytics/trainers/performance/<id> returns specific trainer metrics."""
        # Create trainer
        trainer = Trainer(**sample_trainer)
        db_session.add(trainer)
        db_session.commit()
        
        response = client.get(f'/api/analytics/trainers/performance/{trainer.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        assert isinstance(data, dict)
        assert 'trainer_id' in data or 'id' in data
    
    @pytest.mark.api
    def test_get_revenue_metrics(self, client):
        """Test GET /api/analytics/revenue returns revenue metrics."""
        response = client.get('/api/analytics/revenue')
        assert response.status_code == 200
        data = response.get_json()
        
        # Should contain revenue information
        assert isinstance(data, dict)
    
    @pytest.mark.integration
    def test_analytics_with_actual_data(self, client, db_session, sample_trainer, sample_client):
        """Test analytics endpoints with actual data in database."""
        # Create trainer and client
        trainer = Trainer(**sample_trainer)
        client_obj = Client(**sample_client)
        db_session.add_all([trainer, client_obj])
        db_session.commit()
        
        # Create assignment
        assignment = Assignment(
            trainer_id=trainer.id,
            client_id=client_obj.id,
            notes='Test assignment'
        )
        db_session.add(assignment)
        
        # Create session
        session = Session(
            trainer_id=trainer.id,
            client_id=client_obj.id,
            session_date=datetime.now().isoformat(),
            duration=60,
            session_type='personal',
            status='completed'
        )
        db_session.add(session)
        
        # Create payment
        payment = Payment(
            client_id=client_obj.id,
            amount=100.00,
            payment_date=datetime.now(),
            payment_method='credit_card',
            payment_type='membership',
            status='completed'
        )
        db_session.add(payment)
        db_session.commit()
        
        # Test trainer performance with data
        response = client.get(f'/api/analytics/trainers/performance/{trainer.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        
        # Test client retention with data
        response = client.get('/api/analytics/clients/retention')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        
        # Test revenue metrics with data
        response = client.get('/api/analytics/revenue')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)


class TestAdvancedAnalyticsRoutes:
    """Test advanced analytics API endpoints."""
    
    @pytest.mark.api
    def test_get_churn_prediction(self, client, db_session, sample_client):
        """Test GET /api/analytics/advanced/churn-prediction/<id>."""
        # Create client
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        response = client.get(f'/api/analytics/advanced/churn-prediction/{client_obj.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        # Should contain churn prediction data
        assert isinstance(data, dict)
        assert 'churn_risk' in data or 'risk_score' in data or 'client_id' in data
    
    @pytest.mark.api
    def test_get_revenue_forecast(self, client):
        """Test GET /api/analytics/advanced/revenue-forecast."""
        response = client.get('/api/analytics/advanced/revenue-forecast')
        assert response.status_code == 200
        data = response.get_json()
        
        # Should contain forecast data
        assert isinstance(data, dict) or isinstance(data, list)
    
    @pytest.mark.api
    def test_get_trainer_benchmark(self, client, db_session, sample_trainer):
        """Test GET /api/analytics/advanced/trainer-benchmark/<id>."""
        # Create trainer
        trainer = Trainer(**sample_trainer)
        db_session.add(trainer)
        db_session.commit()
        
        response = client.get(f'/api/analytics/advanced/trainer-benchmark/{trainer.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        # Should contain benchmark data
        assert isinstance(data, dict)
    
    @pytest.mark.api
    def test_get_predictive_insights(self, client):
        """Test GET /api/analytics/advanced/predictive-insights."""
        response = client.get('/api/analytics/advanced/predictive-insights')
        assert response.status_code == 200
        data = response.get_json()
        
        # Should contain insights
        assert isinstance(data, dict)
