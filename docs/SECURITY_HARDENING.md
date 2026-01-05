# FitnessCRM Security Hardening Guide

## Table of Contents
1. [Security Headers](#security-headers)
2. [Authentication & Authorization](#authentication--authorization)
3. [Input Validation](#input-validation)
4. [Rate Limiting](#rate-limiting)
5. [HTTPS & TLS](#https--tls)
6. [Database Security](#database-security)
7. [API Security](#api-security)
8. [Secrets Management](#secrets-management)
9. [Security Monitoring](#security-monitoring)
10. [Compliance](#compliance)

---

## Security Headers

### 1. Implement Flask-Talisman

Already included in `backend/Dockerfile.prod`. Configure in `backend/app.py`:

```python
from flask_talisman import Talisman

# Production security headers
if os.getenv('FLASK_ENV') == 'production':
    Talisman(app,
        force_https=True,
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,  # 1 year
        content_security_policy={
            'default-src': "'self'",
            'script-src': ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net'],
            'style-src': ["'self'", "'unsafe-inline'", 'fonts.googleapis.com'],
            'font-src': ["'self'", 'fonts.gstatic.com'],
            'img-src': ["'self'", 'data:', 'https:'],
            'connect-src': ["'self'"],
        },
        content_security_policy_nonce_in=['script-src'],
        feature_policy={
            'geolocation': "'none'",
            'microphone': "'none'",
            'camera': "'none'",
        }
    )
```

### 2. Nginx Security Headers

Already configured in `nginx/nginx.conf`. Verify these headers are present:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

# When HTTPS is enabled, add:
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 3. Test Security Headers

```bash
# Install security headers checker
npm install -g observatory-cli

# Test headers
observatory yourdomain.com
```

---

## Authentication & Authorization

### 1. Password Security

Update `backend/models/user.py`:

```python
from werkzeug.security import generate_password_hash, check_password_hash
import re

class User(db.Model):
    def set_password(self, password):
        """Set hashed password with strong requirements"""
        # Validate password strength
        if len(password) < 12:
            raise ValueError("Password must be at least 12 characters")
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain uppercase letter")
        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain lowercase letter")
        if not re.search(r'\d', password):
            raise ValueError("Password must contain number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain special character")
        
        # Use strong hashing (pbkdf2:sha256 with high iterations)
        self.password_hash = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=16
        )
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
```

### 2. Session Management

Update `backend/config/session.py`:

```python
import os

SESSION_CONFIG = {
    'SESSION_TYPE': 'redis',
    'SESSION_PERMANENT': False,
    'SESSION_USE_SIGNER': True,
    'SESSION_KEY_PREFIX': 'fitnesscrm:session:',
    'SESSION_REDIS': None,  # Set at runtime
    'PERMANENT_SESSION_LIFETIME': 3600,  # 1 hour
    
    # Cookie security
    'SESSION_COOKIE_SECURE': True,  # HTTPS only
    'SESSION_COOKIE_HTTPONLY': True,  # No JavaScript access
    'SESSION_COOKIE_SAMESITE': 'Lax',  # CSRF protection
    'SESSION_COOKIE_NAME': 'fitness_session'
}
```

### 3. JWT Token Security

If using JWT tokens:

```python
import jwt
from datetime import datetime, timedelta

def generate_token(user_id, expires_in=3600):
    """Generate secure JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow(),
        'nbf': datetime.utcnow()
    }
    return jwt.encode(
        payload,
        os.getenv('SECRET_KEY'),
        algorithm='HS256'
    )

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            os.getenv('SECRET_KEY'),
            algorithms=['HS256']
        )
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

### 4. Role-Based Access Control (RBAC)

Create `backend/utils/rbac.py`:

```python
from functools import wraps
from flask import jsonify

def require_role(*roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            if current_user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage
@app.route('/api/admin/users')
@require_role('admin', 'super_admin')
def manage_users():
    # Only admins can access
    pass
```

---

## Input Validation

### 1. Request Validation

Create `backend/utils/validators.py`:

```python
from marshmallow import Schema, fields, validate, ValidationError
import bleach

class ClientSchema(Schema):
    """Validate client input"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    phone = fields.Str(validate=validate.Regexp(r'^\+?1?\d{9,15}$'))
    age = fields.Int(validate=validate.Range(min=13, max=120))
    
    @validates('name')
    def sanitize_name(self, value):
        """Sanitize HTML from name"""
        return bleach.clean(value, tags=[], strip=True)

def validate_request(schema):
    """Decorator for request validation"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = schema().load(request.get_json())
                request.validated_data = data
                return f(*args, **kwargs)
            except ValidationError as err:
                return jsonify({'errors': err.messages}), 400
        return decorated_function
    return decorator

# Usage
@app.route('/api/clients', methods=['POST'])
@validate_request(ClientSchema)
def create_client():
    data = request.validated_data
    # Data is validated and sanitized
    pass
```

### 2. SQL Injection Prevention

Always use SQLAlchemy ORM with parameterized queries:

```python
# NEVER do this (SQL injection vulnerable):
query = f"SELECT * FROM users WHERE email = '{user_email}'"

# ALWAYS do this (safe with SQLAlchemy):
user = User.query.filter_by(email=user_email).first()

# For raw SQL, always use parameters:
result = db.session.execute(
    text("SELECT * FROM users WHERE email = :email"),
    {"email": user_email}
)
```

### 3. XSS Prevention

```python
from markupsafe import escape

def safe_render(text):
    """Escape HTML to prevent XSS"""
    return escape(text)

# In templates
{{ user_input | e }}  # Jinja2 auto-escaping
```

---

## Rate Limiting

### 1. Flask-Limiter Implementation

Install and configure:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri=os.getenv('REDIS_URL'),
    default_limits=["200 per day", "50 per hour"]
)

# Apply to sensitive endpoints
@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Login logic
    pass

@app.route('/api/register', methods=['POST'])
@limiter.limit("3 per hour")
def register():
    # Registration logic
    pass
```

### 2. Nginx Rate Limiting

Already configured in `nginx/nginx.conf`:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/s;

location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    # ...
}

location ~ ^/api/(login|register|auth) {
    limit_req zone=auth_limit burst=5 nodelay;
    # ...
}
```

---

## HTTPS & TLS

### 1. SSL/TLS Configuration

Best practices already in `nginx/nginx.conf`:

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_stapling on;
ssl_stapling_verify on;
```

### 2. Test SSL Configuration

```bash
# Test SSL configuration
openssl s_client -connect yourdomain.com:443 -tls1_2

# Check SSL rating
# Visit: https://www.ssllabs.com/ssltest/
```

---

## Database Security

### 1. Secure Database Credentials

- Never commit database credentials to Git
- Use strong passwords (32+ characters)
- Rotate passwords regularly (every 90 days)
- Use environment variables only

### 2. Database Access Control

```yaml
# In docker-compose.prod.yml
db:
  # Remove public port exposure
  # ports:  # COMMENTED OUT - not exposed
  networks:
    - fitnesscrm_network  # Internal network only
```

### 3. Database Encryption

Enable encryption at rest (provider-specific):

```bash
# PostgreSQL with encryption
# Use encrypted volumes or provider encryption
# AWS RDS: Enable encryption at creation
# Azure: Transparent Data Encryption (TDE)
```

---

## API Security

### 1. CORS Configuration

Update `backend/app.py`:

```python
from flask_cors import CORS

# Restrict CORS to specific origins
allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
CORS(app, 
     origins=allowed_origins,
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     expose_headers=['Content-Range', 'X-Content-Range'],
     supports_credentials=True,
     max_age=3600
)
```

### 2. API Key Authentication

For public API access:

```python
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not verify_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/v2/clients')
@require_api_key
def api_v2_clients():
    pass
```

---

## Secrets Management

### 1. Environment Variables

```bash
# NEVER hardcode secrets
BAD:  SECRET_KEY = "my-secret-key-123"
GOOD: SECRET_KEY = os.getenv('SECRET_KEY')
```

### 2. Secrets Rotation

Create rotation script:

```bash
#!/bin/bash
# Rotate database password
NEW_PASSWORD=$(openssl rand -base64 32)

# Update environment
sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$NEW_PASSWORD/" .env.production

# Update database
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -c "ALTER USER fitnesscrm_user WITH PASSWORD '$NEW_PASSWORD';"

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

---

## Security Monitoring

### 1. Audit Logging

Already implemented in `backend/models/activity_log.py`. Ensure all sensitive operations are logged:

```python
def log_security_event(event_type, user_id, details):
    """Log security-related events"""
    ActivityLog.create(
        action=event_type,
        entity_type='security',
        user_id=user_id,
        details=details
    )

# Usage
log_security_event('login_failure', None, {'ip': request.remote_addr})
log_security_event('password_change', user.id, {'success': True})
```

### 2. Failed Login Monitoring

```python
from datetime import datetime, timedelta

def check_failed_logins(email, ip_address):
    """Check for brute force attempts"""
    recent_failures = ActivityLog.query.filter(
        ActivityLog.action == 'login_failure',
        ActivityLog.details['email'] == email,
        ActivityLog.timestamp > datetime.utcnow() - timedelta(minutes=15)
    ).count()
    
    if recent_failures >= 5:
        # Lock account or add delay
        raise SecurityError('Account temporarily locked due to failed login attempts')
```

---

## Compliance

### 1. GDPR Compliance

Implement data export:

```python
@app.route('/api/users/<int:user_id>/export', methods=['GET'])
@require_authentication
def export_user_data(user_id):
    """Export all user data (GDPR Right to Access)"""
    if current_user.id != user_id and not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    data = {
        'user': user.to_dict(),
        'clients': [c.to_dict() for c in user.clients],
        'sessions': [s.to_dict() for s in user.sessions],
        # ... other data
    }
    
    return jsonify(data)
```

Implement data deletion:

```python
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@require_authentication
def delete_user_data(user_id):
    """Delete all user data (GDPR Right to Erasure)"""
    if current_user.id != user_id and not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    # Anonymize instead of hard delete (for records)
    user.email = f"deleted_{user.id}@deleted.local"
    user.name = "Deleted User"
    user.phone = None
    user.is_active = False
    
    db.session.commit()
    
    return jsonify({'message': 'User data deleted'})
```

---

## Security Checklist

### Pre-Production

- [ ] All default passwords changed
- [ ] SECRET_KEY is cryptographically random
- [ ] HTTPS enabled and enforced
- [ ] Security headers implemented
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention verified
- [ ] XSS prevention verified
- [ ] CSRF protection enabled
- [ ] Session security configured
- [ ] Database not exposed to internet
- [ ] Redis password protected
- [ ] File upload restrictions in place
- [ ] Error messages don't leak information

### Post-Production

- [ ] Security monitoring enabled
- [ ] Failed login tracking active
- [ ] Audit logging comprehensive
- [ ] Regular security updates scheduled
- [ ] Backup encryption verified
- [ ] Incident response plan documented
- [ ] Regular security audits scheduled
- [ ] Penetration testing performed

---

## Security Incident Response

### 1. Incident Response Plan

1. **Detect**: Monitor logs, alerts, user reports
2. **Contain**: Isolate affected systems
3. **Investigate**: Analyze logs, identify scope
4. **Remediate**: Fix vulnerability, patch systems
5. **Recover**: Restore normal operations
6. **Review**: Post-incident analysis

### 2. Emergency Contacts

```yaml
# Store securely, not in repository
security_team:
  - name: "Security Lead"
    email: "security@yourdomain.com"
    phone: "+1-XXX-XXX-XXXX"
  
external_contacts:
  - service: "AWS Support"
    contact: "aws-support-contact"
  - service: "Sentry"
    contact: "sentry-support"
```

---

**Last Updated**: January 2026
