"""
Authentication and Authorization utilities
Phase 7: Advanced Features - M7.4: Security & Compliance

Basic authentication system ready for production use.
"""

from functools import wraps
from flask import request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import db, User
from utils.logger import logger
import jwt
import os
from datetime import datetime, timedelta

# JWT configuration
JWT_SECRET = os.getenv('JWT_SECRET', os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'))
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def hash_password(password: str) -> str:
    """Hash a password using werkzeug"""
    return generate_password_hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return check_password_hash(password_hash, password)

def generate_token(user_id: int, email: str, role: str = 'user') -> str:
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid authorization header'}), 401
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Verify token
        payload = verify_token(token)
        if 'error' in payload:
            return jsonify({'error': payload['error']}), 401
        
        # Store user info in g
        g.current_user_id = payload['user_id']
        g.current_user_email = payload['email']
        g.current_user_role = payload.get('role', 'user')
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(*allowed_roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            if g.current_user_role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Get current authenticated user"""
    if hasattr(g, 'current_user_id'):
        return User.query.get(g.current_user_id)
    return None

def change_user_password(email: str, new_password: str, role: str, name: str = None) -> tuple:
    """
    Change or create user password for a given email
    
    Args:
        email: User email address
        new_password: New password to set
        role: User role (trainer, client, admin, etc.)
        name: Optional name for logging purposes
    
    Returns:
        Tuple of (success: bool, message: str, status_code: int)
    """
    if len(new_password) < 6:
        return False, 'Password must be at least 6 characters', 400
    
    try:
        # Find user account by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create user account if it doesn't exist
            user = User(
                email=email,
                password_hash=hash_password(new_password),
                role=role,
                active=True
            )
            db.session.add(user)
            log_msg = f"Created User account for {role}"
            if name:
                log_msg += f": {name}"
            logger.info(log_msg)
        else:
            # Update password
            user.password_hash = hash_password(new_password)
            log_msg = f"Password changed for {role}"
            if name:
                log_msg += f": {name}"
            logger.info(log_msg)
        
        db.session.commit()
        
        # Verify User account was created/updated successfully
        verify_user = User.query.filter_by(email=email).first()
        if not verify_user:
            logger.error(f"CRITICAL: User account was not saved for email: {email}")
            return False, 'Failed to save User account. Please try again.', 500
        
        logger.info(f"✓ Verified User account: {verify_user.email} (ID: {verify_user.id}, Role: {verify_user.role})")
        return True, 'Password set successfully', 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error changing password for {email}: {str(e)}", exc_info=True)
        return False, str(e), 500

