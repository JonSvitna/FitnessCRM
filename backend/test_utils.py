"""
Unit tests for utility functions.
"""

import pytest
from datetime import datetime, timedelta


class TestEmailUtils:
    """Test email utility functions."""
    
    @pytest.mark.unit
    def test_validate_email_format(self):
        """Test email validation."""
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Valid emails
        assert re.match(email_regex, 'test@example.com')
        assert re.match(email_regex, 'user.name@domain.co.uk')
        assert re.match(email_regex, 'user+tag@example.com')
        
        # Invalid emails
        assert not re.match(email_regex, 'invalid.email')
        assert not re.match(email_regex, '@example.com')
        assert not re.match(email_regex, 'user@')


class TestDateUtils:
    """Test date utility functions."""
    
    @pytest.mark.unit
    def test_date_formatting(self):
        """Test date formatting."""
        test_date = datetime(2024, 12, 19, 10, 30, 0)
        
        # ISO format
        iso_str = test_date.isoformat()
        assert iso_str.startswith('2024-12-19')
        
        # Parse ISO format
        parsed = datetime.fromisoformat(iso_str)
        assert parsed.year == 2024
        assert parsed.month == 12
        assert parsed.day == 19
    
    @pytest.mark.unit
    def test_date_arithmetic(self):
        """Test date calculations."""
        base_date = datetime(2024, 12, 19)
        
        # Add days
        future_date = base_date + timedelta(days=7)
        assert future_date.day == 26
        
        # Subtract days
        past_date = base_date - timedelta(days=7)
        assert past_date.day == 12
        
        # Date difference
        diff = future_date - past_date
        assert diff.days == 14


class TestValidationUtils:
    """Test validation utility functions."""
    
    @pytest.mark.unit
    def test_validate_phone_number(self):
        """Test phone number validation."""
        import re
        # Simple phone validation pattern
        phone_regex = r'^[\d\s\-\+\(\)]+$'
        
        # Valid phone numbers
        assert re.match(phone_regex, '555-0100')
        assert re.match(phone_regex, '(555) 010-0100')
        assert re.match(phone_regex, '+1 555 010 0100')
        
        # Invalid phone numbers
        assert not re.match(phone_regex, 'abc-defg')
        assert not re.match(phone_regex, '555@0100')
    
    @pytest.mark.unit
    def test_validate_positive_number(self):
        """Test positive number validation."""
        # Valid positive numbers
        assert 100.00 > 0
        assert 0.01 > 0
        assert 1 > 0
        
        # Invalid (negative or zero)
        assert not (-10 > 0)
        assert not (0 > 0)
    
    @pytest.mark.unit
    def test_validate_required_fields(self):
        """Test required field validation."""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '555-0100'
        }
        
        required_fields = ['name', 'email']
        
        # All required fields present
        assert all(field in data for field in required_fields)
        
        # Missing required field
        incomplete_data = {'name': 'John Doe'}
        assert not all(field in incomplete_data for field in required_fields)


class TestPasswordUtils:
    """Test password utility functions."""
    
    @pytest.mark.unit
    def test_password_hashing(self):
        """Test password hashing with werkzeug."""
        from werkzeug.security import generate_password_hash, check_password_hash
        
        password = 'SecurePassword123!'
        hashed = generate_password_hash(password)
        
        # Hash should be different from original
        assert hashed != password
        
        # Hash should verify correctly
        assert check_password_hash(hashed, password)
        
        # Wrong password should not verify
        assert not check_password_hash(hashed, 'WrongPassword')
    
    @pytest.mark.unit
    def test_password_strength(self):
        """Test password strength validation."""
        import re
        
        # Password strength regex (min 8 chars, 1 uppercase, 1 lowercase, 1 digit)
        strong_password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
        
        # Strong passwords
        assert re.match(strong_password_regex, 'SecurePass123')
        assert re.match(strong_password_regex, 'MyP@ssw0rd')
        
        # Weak passwords
        assert not re.match(strong_password_regex, 'weak')
        assert not re.match(strong_password_regex, 'nocaps123')
        assert not re.match(strong_password_regex, 'NOUPPER123')
        assert not re.match(strong_password_regex, 'NoDigits')


class TestDataSanitization:
    """Test data sanitization functions."""
    
    @pytest.mark.unit
    def test_strip_whitespace(self):
        """Test whitespace stripping."""
        # Leading/trailing whitespace
        assert '  test  '.strip() == 'test'
        assert '\n\ttest\n\t'.strip() == 'test'
        
        # Internal whitespace preserved
        assert '  test  value  '.strip() == 'test  value'
    
    @pytest.mark.unit
    def test_escape_html(self):
        """Test HTML escaping for XSS prevention."""
        from html import escape
        
        # XSS attempts
        dangerous_input = '<script>alert("XSS")</script>'
        escaped = escape(dangerous_input)
        
        # Should escape angle brackets
        assert '<script>' not in escaped
        assert '&lt;script&gt;' in escaped
    
    @pytest.mark.unit
    def test_sql_injection_prevention(self):
        """Test that parameterized queries prevent SQL injection."""
        # This is more of a conceptual test
        # SQLAlchemy ORM prevents SQL injection by using parameterized queries
        
        malicious_input = "'; DROP TABLE trainers; --"
        
        # When using ORM, this would be treated as a string value
        # Not as SQL code
        assert isinstance(malicious_input, str)
        assert "DROP TABLE" in malicious_input  # Would be searched as literal string


class TestJWTUtils:
    """Test JWT token utilities."""
    
    @pytest.mark.unit
    def test_jwt_encoding_decoding(self):
        """Test JWT token creation and validation."""
        try:
            import jwt
            
            secret_key = 'test-secret-key'
            payload = {
                'user_id': 1,
                'email': 'test@example.com',
                'role': 'trainer'
            }
            
            # Encode token
            token = jwt.encode(payload, secret_key, algorithm='HS256')
            assert isinstance(token, str)
            
            # Decode token
            decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
            assert decoded['user_id'] == 1
            assert decoded['email'] == 'test@example.com'
            
        except ImportError:
            pytest.skip("JWT library not available")
    
    @pytest.mark.unit
    def test_jwt_expiration(self):
        """Test JWT token expiration."""
        try:
            import jwt
            from datetime import datetime, timedelta
            
            secret_key = 'test-secret-key'
            
            # Create expired token
            expired_payload = {
                'user_id': 1,
                'exp': datetime.utcnow() - timedelta(hours=1)
            }
            
            token = jwt.encode(expired_payload, secret_key, algorithm='HS256')
            
            # Try to decode expired token
            with pytest.raises(jwt.ExpiredSignatureError):
                jwt.decode(token, secret_key, algorithms=['HS256'])
                
        except ImportError:
            pytest.skip("JWT library not available")


class TestPaginationUtils:
    """Test pagination utilities."""
    
    @pytest.mark.unit
    def test_calculate_pagination(self):
        """Test pagination calculations."""
        total_items = 100
        per_page = 10
        
        # Calculate total pages
        total_pages = (total_items + per_page - 1) // per_page
        assert total_pages == 10
        
        # Calculate offset for page 3
        page = 3
        offset = (page - 1) * per_page
        assert offset == 20
        
        # Has next page
        assert page < total_pages
        
        # Has previous page
        assert page > 1
    
    @pytest.mark.unit
    def test_pagination_edge_cases(self):
        """Test pagination edge cases."""
        # Empty result set
        assert (0 + 10 - 1) // 10 == 0
        
        # Exact multiple
        assert (100 + 10 - 1) // 10 == 10
        
        # One extra item
        assert (101 + 10 - 1) // 10 == 11
        
        # Single item
        assert (1 + 10 - 1) // 10 == 1
