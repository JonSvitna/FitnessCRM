"""
Unit tests for payment API routes.
"""

import pytest
from datetime import datetime
from models.database import Payment, Client


class TestPaymentRoutes:
    """Test payment API endpoints."""
    
    @pytest.mark.api
    def test_get_payments_empty(self, client):
        """Test GET /api/payments with no payments."""
        response = client.get('/api/payments')
        assert response.status_code == 200
        data = response.get_json()
        # Should return paginated response or list
        assert 'payments' in data or isinstance(data, list)
    
    @pytest.mark.api
    def test_create_payment(self, client, db_session, sample_client):
        """Test POST /api/payments creates a payment."""
        # Create client first
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        # Create payment
        payment_data = {
            'client_id': client_obj.id,
            'amount': 100.00,
            'payment_date': datetime.now().isoformat(),
            'payment_method': 'credit_card',
            'payment_type': 'membership',
            'status': 'completed'
        }
        response = client.post('/api/payments', json=payment_data)
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'id' in data
        assert data['client_id'] == client_obj.id
        assert data['amount'] == 100.00
        assert data['payment_method'] == 'credit_card'
    
    @pytest.mark.api
    def test_get_payment_by_id(self, client, db_session, sample_client):
        """Test GET /api/payments/<id> returns specific payment."""
        # Create client and payment
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        payment = Payment(
            client_id=client_obj.id,
            amount=75.50,
            payment_date=datetime.now(),
            payment_method='cash',
            payment_type='session',
            status='completed'
        )
        db_session.add(payment)
        db_session.commit()
        
        # Get payment
        response = client.get(f'/api/payments/{payment.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['id'] == payment.id
        assert data['client_id'] == client_obj.id
        assert data['amount'] == 75.50
    
    @pytest.mark.api
    def test_update_payment(self, client, db_session, sample_client):
        """Test PUT /api/payments/<id> updates payment."""
        # Create client and payment
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        payment = Payment(
            client_id=client_obj.id,
            amount=50.00,
            payment_date=datetime.now(),
            payment_method='check',
            payment_type='session',
            status='pending'
        )
        db_session.add(payment)
        db_session.commit()
        payment_id = payment.id
        
        # Update payment
        update_data = {
            'status': 'completed',
            'transaction_id': 'TXN123456'
        }
        response = client.put(f'/api/payments/{payment_id}', json=update_data)
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['status'] == 'completed'
        assert data['transaction_id'] == 'TXN123456'
    
    @pytest.mark.api
    def test_delete_payment(self, client, db_session, sample_client):
        """Test DELETE /api/payments/<id> deletes payment."""
        # Create client and payment
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        payment = Payment(
            client_id=client_obj.id,
            amount=25.00,
            payment_date=datetime.now(),
            payment_method='cash',
            payment_type='product',
            status='completed'
        )
        db_session.add(payment)
        db_session.commit()
        payment_id = payment.id
        
        # Delete payment
        response = client.delete(f'/api/payments/{payment_id}')
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get(f'/api/payments/{payment_id}')
        assert response.status_code == 404
    
    @pytest.mark.api
    def test_filter_payments_by_client(self, client, db_session, sample_client):
        """Test filtering payments by client_id."""
        # Create clients
        client1 = Client(**sample_client)
        client2_data = sample_client.copy()
        client2_data['email'] = 'client2@example.com'
        client2 = Client(**client2_data)
        db_session.add_all([client1, client2])
        db_session.commit()
        
        # Create payments for different clients
        payment1 = Payment(
            client_id=client1.id,
            amount=100.00,
            payment_date=datetime.now(),
            payment_method='credit_card',
            payment_type='membership',
            status='completed'
        )
        payment2 = Payment(
            client_id=client2.id,
            amount=50.00,
            payment_date=datetime.now(),
            payment_method='cash',
            payment_type='session',
            status='completed'
        )
        db_session.add_all([payment1, payment2])
        db_session.commit()
        
        # Filter by client1
        response = client.get(f'/api/payments?client_id={client1.id}')
        assert response.status_code == 200
        data = response.get_json()
        
        # Handle both paginated and non-paginated responses
        payments = data.get('payments', data) if isinstance(data, dict) else data
        assert len(payments) >= 1
        assert all(p['client_id'] == client1.id for p in payments)
    
    @pytest.mark.api
    def test_filter_payments_by_status(self, client, db_session, sample_client):
        """Test filtering payments by status."""
        # Create client
        client_obj = Client(**sample_client)
        db_session.add(client_obj)
        db_session.commit()
        
        # Create payments with different statuses
        payment1 = Payment(
            client_id=client_obj.id,
            amount=100.00,
            payment_date=datetime.now(),
            payment_method='credit_card',
            payment_type='membership',
            status='completed'
        )
        payment2 = Payment(
            client_id=client_obj.id,
            amount=50.00,
            payment_date=datetime.now(),
            payment_method='cash',
            payment_type='session',
            status='pending'
        )
        db_session.add_all([payment1, payment2])
        db_session.commit()
        
        # Filter by pending status
        response = client.get('/api/payments?status=pending')
        assert response.status_code == 200
        data = response.get_json()
        
        # Handle both paginated and non-paginated responses
        payments = data.get('payments', data) if isinstance(data, dict) else data
        assert all(p['status'] == 'pending' for p in payments)
    
    @pytest.mark.api
    def test_payment_validation_missing_fields(self, client):
        """Test POST /api/payments with missing required fields."""
        incomplete_payment = {
            'amount': 100.00
            # Missing client_id, payment_date, etc.
        }
        response = client.post('/api/payments', json=incomplete_payment)
        # Should return 400 or 422 for validation error
        assert response.status_code in [400, 422]
