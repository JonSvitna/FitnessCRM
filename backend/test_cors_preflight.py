"""
Tests for CORS preflight OPTIONS request handling.
"""

import pytest


class TestCORSPreflight:
    """Test CORS preflight OPTIONS request handling."""
    
    @pytest.mark.api
    def test_options_request_auth_login(self, client):
        """Test OPTIONS /api/auth/login returns proper CORS headers."""
        response = client.options('/api/auth/login')
        
        # Should return 200 status
        assert response.status_code == 200
        
        # Should have CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        
        # Verify allowed methods include OPTIONS
        allowed_methods = response.headers.get('Access-Control-Allow-Methods', '')
        assert 'OPTIONS' in allowed_methods
        assert 'POST' in allowed_methods
    
    @pytest.mark.api
    def test_options_request_root(self, client):
        """Test OPTIONS / returns proper CORS headers."""
        response = client.options('/')
        
        # Should return 200 status
        assert response.status_code == 200
        
        # Should have CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers
    
    @pytest.mark.api
    def test_options_request_api_endpoint(self, client):
        """Test OPTIONS on API endpoint returns proper CORS headers."""
        response = client.options('/api/trainers')
        
        # Should return 200 status
        assert response.status_code == 200
        
        # Should have CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
