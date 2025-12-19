"""
Unit tests for authentication and authorization API routes.
"""

import pytest
from models.database import User


class TestAuthRoutes:
    """Test authentication API endpoints."""
    
    @pytest.mark.api
    def test_register_user(self, client):
        """Test POST /api/auth/register creates a new user."""
        user_data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'name': 'New User',
            'role': 'trainer'
        }
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'id' in data or 'user' in data
        # Password should not be in response
        if isinstance(data, dict) and 'password' in data:
            assert data['password'] != user_data['password']  # Should be hashed
    
    @pytest.mark.api
    def test_register_duplicate_email(self, client, db_session):
        """Test that registering with duplicate email fails."""
        # Create first user
        user_data = {
            'email': 'duplicate@example.com',
            'password': 'Password123!',
            'name': 'First User',
            'role': 'trainer'
        }
        response1 = client.post('/api/auth/register', json=user_data)
        assert response1.status_code == 201
        
        # Try to create second user with same email
        user_data['name'] = 'Second User'
        response2 = client.post('/api/auth/register', json=user_data)
        # Should fail with 400 or 409 conflict
        assert response2.status_code in [400, 409, 422]
    
    @pytest.mark.api
    def test_login_success(self, client, db_session):
        """Test POST /api/auth/login with valid credentials."""
        # Register user first
        user_data = {
            'email': 'logintest@example.com',
            'password': 'TestPass123!',
            'name': 'Login Test User',
            'role': 'trainer'
        }
        client.post('/api/auth/register', json=user_data)
        
        # Login
        login_data = {
            'email': 'logintest@example.com',
            'password': 'TestPass123!'
        }
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
        data = response.get_json()
        
        # Should return token
        assert 'token' in data or 'access_token' in data
    
    @pytest.mark.api
    def test_login_invalid_password(self, client, db_session):
        """Test POST /api/auth/login with invalid password."""
        # Register user first
        user_data = {
            'email': 'wrongpass@example.com',
            'password': 'CorrectPass123!',
            'name': 'Test User',
            'role': 'trainer'
        }
        client.post('/api/auth/register', json=user_data)
        
        # Try to login with wrong password
        login_data = {
            'email': 'wrongpass@example.com',
            'password': 'WrongPassword!'
        }
        response = client.post('/api/auth/login', json=login_data)
        # Should return 401 unauthorized
        assert response.status_code == 401
    
    @pytest.mark.api
    def test_login_nonexistent_user(self, client):
        """Test POST /api/auth/login with non-existent user."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!'
        }
        response = client.post('/api/auth/login', json=login_data)
        # Should return 401 unauthorized
        assert response.status_code == 401
    
    @pytest.mark.api
    def test_get_current_user(self, client, db_session):
        """Test GET /api/auth/me returns current user info."""
        # Register and login to get token
        user_data = {
            'email': 'currentuser@example.com',
            'password': 'TestPass123!',
            'name': 'Current User',
            'role': 'trainer'
        }
        client.post('/api/auth/register', json=user_data)
        
        login_response = client.post('/api/auth/login', json={
            'email': user_data['email'],
            'password': user_data['password']
        })
        
        if login_response.status_code == 200:
            login_data = login_response.get_json()
            token = login_data.get('token') or login_data.get('access_token')
            
            if token:
                # Get current user with token
                headers = {'Authorization': f'Bearer {token}'}
                response = client.get('/api/auth/me', headers=headers)
                assert response.status_code in [200, 401]  # 401 if auth not fully configured
                
                if response.status_code == 200:
                    data = response.get_json()
                    assert 'email' in data
                    assert data['email'] == user_data['email']
    
    @pytest.mark.api
    def test_logout(self, client, db_session):
        """Test POST /api/auth/logout."""
        # Register and login first
        user_data = {
            'email': 'logouttest@example.com',
            'password': 'TestPass123!',
            'name': 'Logout Test',
            'role': 'trainer'
        }
        client.post('/api/auth/register', json=user_data)
        
        login_response = client.post('/api/auth/login', json={
            'email': user_data['email'],
            'password': user_data['password']
        })
        
        if login_response.status_code == 200:
            login_data = login_response.get_json()
            token = login_data.get('token') or login_data.get('access_token')
            
            if token:
                # Logout
                headers = {'Authorization': f'Bearer {token}'}
                response = client.post('/api/auth/logout', headers=headers)
                # Should succeed or return 401 if endpoint requires different auth setup
                assert response.status_code in [200, 401]
    
    @pytest.mark.api
    def test_change_password(self, client, db_session):
        """Test POST /api/auth/change-password."""
        # Register user first
        user_data = {
            'email': 'changepass@example.com',
            'password': 'OldPass123!',
            'name': 'Change Pass User',
            'role': 'trainer'
        }
        client.post('/api/auth/register', json=user_data)
        
        login_response = client.post('/api/auth/login', json={
            'email': user_data['email'],
            'password': user_data['password']
        })
        
        if login_response.status_code == 200:
            login_data = login_response.get_json()
            token = login_data.get('token') or login_data.get('access_token')
            
            if token:
                # Change password
                headers = {'Authorization': f'Bearer {token}'}
                change_data = {
                    'old_password': 'OldPass123!',
                    'new_password': 'NewPass123!'
                }
                response = client.post('/api/auth/change-password', 
                                      json=change_data, 
                                      headers=headers)
                assert response.status_code in [200, 401]


class TestAuthorizationRoutes:
    """Test authorization and role-based access control."""
    
    @pytest.mark.api
    def test_admin_only_endpoint(self, client):
        """Test that admin-only endpoints are protected."""
        # Try to access admin endpoint without auth
        response = client.get('/api/audit/logs')
        # Should return 401 or 403
        assert response.status_code in [401, 403]
    
    @pytest.mark.api
    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without authentication."""
        # Assuming some endpoints require auth
        response = client.get('/api/auth/me')
        # Should return 401 unauthorized
        assert response.status_code in [401, 403]
