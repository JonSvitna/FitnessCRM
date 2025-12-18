"""
Authentication routes
Phase 7: Advanced Features - M7.4: Security & Compliance
"""

from flask import Blueprint, request, jsonify
from models.database import db
from models.user import User
from utils.auth import hash_password, verify_password, generate_token, require_auth, get_current_user
from utils.logger import logger
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    try:
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Create new user
        user = User(
            email=data['email'],
            password_hash=hash_password(data['password']),
            role=data.get('role', 'user')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id, user.email, user.role)
        
        logger.info(f"User registered: {user.email}")
        
        return jsonify({
            'user': user.to_dict(),
            'token': token,
            'message': 'User registered successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    try:
        email = data['email'].strip().lower()  # Normalize email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not verify_password(data['password'], user.password_hash):
            logger.warning(f"Invalid password attempt for: {email}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.active:
            logger.warning(f"Login attempt for disabled account: {email}")
            return jsonify({'error': 'Account is disabled'}), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id, user.email, user.role)
        
        logger.info(f"User logged in: {user.email} (role: {user.role})")
        
        return jsonify({
            'user': user.to_dict(),
            'token': token,
            'message': 'Login successful'
        }), 200
        
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user_info():
    """Get current authenticated user info"""
    user = get_current_user()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user (client should discard token)"""
    # In a more advanced implementation, you could blacklist the token
    # For now, logout is handled client-side by discarding the token
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change user password"""
    data = request.get_json()
    
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current password and new password are required'}), 400
    
    try:
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        if not verify_password(data['current_password'], user.password_hash):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        user.password_hash = hash_password(data['new_password'])
        db.session.commit()
        
        logger.info(f"Password changed for user: {user.email}")
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error changing password: {str(e)}")
        return jsonify({'error': str(e)}), 500

