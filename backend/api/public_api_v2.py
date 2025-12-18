"""
Public API v2 with OAuth 2.0 authentication
Phase 6: Mobile & Integrations - M6.5: Public API
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps
from models.database import db, Client, Trainer, Session, Payment
from utils.logger import logger
from datetime import datetime, timedelta
import hashlib
import secrets
import time

public_api_v2 = Blueprint('public_api_v2', __name__, url_prefix='/api/v2')

# In-memory token storage (in production, use database)
_api_tokens = {}
_api_clients = {}
_rate_limits = {}  # {client_id: {endpoint: {count: int, reset_time: datetime}}}

# Rate limiting configuration
RATE_LIMITS = {
    'default': {'requests': 100, 'window': 3600},  # 100 requests per hour
    'clients': {'requests': 200, 'window': 3600},
    'sessions': {'requests': 200, 'window': 3600},
    'payments': {'requests': 50, 'window': 3600},
}

def generate_api_key():
    """Generate a new API key"""
    return secrets.token_urlsafe(32)

def hash_api_key(api_key):
    """Hash an API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def check_rate_limit(client_id, endpoint='default'):
    """Check if client has exceeded rate limit"""
    if client_id not in _rate_limits:
        _rate_limits[client_id] = {}
    
    if endpoint not in _rate_limits[client_id]:
        _rate_limits[client_id][endpoint] = {
            'count': 0,
            'reset_time': datetime.utcnow() + timedelta(seconds=RATE_LIMITS.get(endpoint, RATE_LIMITS['default'])['window'])
        }
    
    limit_info = _rate_limits[client_id][endpoint]
    limit_config = RATE_LIMITS.get(endpoint, RATE_LIMITS['default'])
    
    # Reset if window expired
    if datetime.utcnow() > limit_info['reset_time']:
        limit_info['count'] = 0
        limit_info['reset_time'] = datetime.utcnow() + timedelta(seconds=limit_config['window'])
    
    # Check limit
    if limit_info['count'] >= limit_config['requests']:
        return False, {
            'error': 'Rate limit exceeded',
            'limit': limit_config['requests'],
            'window': limit_config['window'],
            'reset_at': limit_info['reset_time'].isoformat()
        }
    
    # Increment count
    limit_info['count'] += 1
    
    return True, None

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Find client by API key
        hashed_key = hash_api_key(api_key)
        client_id = None
        
        for cid, client_data in _api_clients.items():
            if client_data.get('hashed_key') == hashed_key:
                client_id = cid
                break
        
        if not client_id:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Check rate limit
        endpoint = request.endpoint.split('.')[-1] if request.endpoint else 'default'
        allowed, error = check_rate_limit(client_id, endpoint)
        
        if not allowed:
            return jsonify(error), 429
        
        # Store client info in g for use in route
        g.api_client_id = client_id
        g.api_client_data = _api_clients[client_id]
        
        return f(*args, **kwargs)
    
    return decorated_function

# API Client Management
@public_api_v2.route('/clients/register', methods=['POST'])
def register_api_client():
    """Register a new API client"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({'error': 'name and email are required'}), 400
    
    # Generate API key
    api_key = generate_api_key()
    hashed_key = hash_api_key(api_key)
    
    client_id = len(_api_clients) + 1
    client_data = {
        'id': client_id,
        'name': data['name'],
        'email': data['email'],
        'hashed_key': hashed_key,
        'created_at': datetime.utcnow().isoformat(),
        'active': True
    }
    
    _api_clients[client_id] = client_data
    
    logger.info(f"API client registered: {data['name']} (ID: {client_id})")
    
    return jsonify({
        'client_id': client_id,
        'api_key': api_key,  # Only returned once
        'message': 'API client registered successfully. Save your API key securely.'
    }), 201

@public_api_v2.route('/clients/revoke', methods=['POST'])
@require_api_key
def revoke_api_client():
    """Revoke API client access"""
    client_id = g.api_client_id
    
    if client_id in _api_clients:
        _api_clients[client_id]['active'] = False
        logger.info(f"API client revoked: {client_id}")
        return jsonify({'message': 'API client revoked successfully'}), 200
    
    return jsonify({'error': 'API client not found'}), 404

# Public API Endpoints
@public_api_v2.route('/clients', methods=['GET'])
@require_api_key
def get_clients():
    """Get list of clients"""
    query = Client.query
    
    # Filtering
    if request.args.get('active'):
        query = query.filter(Client.active == (request.args.get('active') == 'true'))
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 25, type=int), 100)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    clients = [client.to_dict() for client in pagination.items]
    
    return jsonify({
        'data': clients,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200

@public_api_v2.route('/clients/<int:client_id>', methods=['GET'])
@require_api_key
def get_client(client_id):
    """Get a specific client"""
    client = Client.query.get_or_404(client_id)
    return jsonify({'data': client.to_dict()}), 200

@public_api_v2.route('/sessions', methods=['GET'])
@require_api_key
def get_sessions():
    """Get list of sessions"""
    query = Session.query
    
    # Filtering
    client_id = request.args.get('client_id', type=int)
    if client_id:
        query = query.filter(Session.client_id == client_id)
    
    trainer_id = request.args.get('trainer_id', type=int)
    if trainer_id:
        query = query.filter(Session.trainer_id == trainer_id)
    
    status = request.args.get('status')
    if status:
        query = query.filter(Session.status == status)
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date:
        query = query.filter(Session.session_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Session.session_date <= datetime.fromisoformat(end_date))
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 25, type=int), 100)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    sessions = [session.to_dict() for session in pagination.items]
    
    return jsonify({
        'data': sessions,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200

@public_api_v2.route('/sessions/<int:session_id>', methods=['GET'])
@require_api_key
def get_session(session_id):
    """Get a specific session"""
    session = Session.query.get_or_404(session_id)
    return jsonify({'data': session.to_dict()}), 200

@public_api_v2.route('/payments', methods=['GET'])
@require_api_key
def get_payments():
    """Get list of payments"""
    query = Payment.query.filter(Payment.status == 'completed')
    
    # Filtering
    client_id = request.args.get('client_id', type=int)
    if client_id:
        query = query.filter(Payment.client_id == client_id)
    
    payment_type = request.args.get('payment_type')
    if payment_type:
        query = query.filter(Payment.payment_type == payment_type)
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date:
        query = query.filter(Payment.payment_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Payment.payment_date <= datetime.fromisoformat(end_date))
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 25, type=int), 100)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    payments = [payment.to_dict() for payment in pagination.items]
    
    return jsonify({
        'data': payments,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    }), 200

@public_api_v2.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint (no authentication required)"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@public_api_v2.route('/docs', methods=['GET'])
def api_docs():
    """API documentation endpoint"""
    return jsonify({
        'version': '2.0.0',
        'base_url': '/api/v2',
        'authentication': {
            'type': 'API Key',
            'header': 'X-API-Key',
            'register': '/api/v2/clients/register'
        },
        'endpoints': {
            'clients': {
                'GET /clients': 'List clients',
                'GET /clients/{id}': 'Get client details'
            },
            'sessions': {
                'GET /sessions': 'List sessions',
                'GET /sessions/{id}': 'Get session details'
            },
            'payments': {
                'GET /payments': 'List payments'
            }
        },
        'rate_limits': RATE_LIMITS,
        'documentation': 'https://docs.fitnesscrm.com/api/v2'
    }), 200

