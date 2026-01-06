from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, timedelta
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configure CORS with proper settings for production
# Allow all origins for development/testing - in production, set specific origins via environment variable
cors_origins = os.environ.get('CORS_ORIGINS', '*')
CORS(app, 
     resources={r"/*": {"origins": cors_origins}},
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
     supports_credentials=False,  # Set to False when using wildcard origins
     expose_headers=["Content-Type", "Authorization"],
     max_age=3600  # Cache preflight responses for 1 hour
)

# JWT Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database connection
def get_db_connection():
    """Get database connection using DATABASE_URL environment variable"""
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/fitnesscrm')
    
    # Fix for Railway/Heroku postgres URLs (postgres:// -> postgresql://)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    conn = psycopg2.connect(database_url)
    return conn

# JWT token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated

# Initialize database tables
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create clients table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(120),
            phone VARCHAR(20),
            user_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create sessions table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id SERIAL PRIMARY KEY,
            client_id INTEGER REFERENCES clients(id),
            session_date TIMESTAMP NOT NULL,
            duration INTEGER,
            notes TEXT,
            user_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()

# Auth Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password or not email:
        return jsonify({'message': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if user already exists
    cur.execute('SELECT id FROM users WHERE username = %s OR email = %s', (username, email))
    if cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'message': 'User already exists'}), 400
    
    # Create new user
    password_hash = generate_password_hash(password)
    cur.execute(
        'INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s) RETURNING id',
        (username, password_hash, email)
    )
    user_id = cur.fetchone()[0]
    
    conn.commit()
    cur.close()
    conn.close()
    
    # Generate token
    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({'token': token, 'user_id': user_id}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Missing credentials'}), 400
    
    # Normalize email to lowercase for consistent lookup
    email = email.strip().lower()
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Generate token
    token = jwt.encode({
        'user_id': user['id'],
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    # Construct user object for response (matching expected frontend format)
    # Note: role and active may not exist in legacy database schema
    # Defaults are provided for backward compatibility
    user_data = {
        'id': user['id'],
        'email': user['email'],
        'role': user.get('role', 'user'),  # default to 'user' if not present
        'active': user.get('active', True),
        'created_at': user['created_at'].isoformat() if user.get('created_at') else None,
    }
    
    return jsonify({'token': token, 'user': user_data, 'message': 'Login successful'}), 200

# Client Routes
@app.route('/api/clients', methods=['GET'])
@token_required
def get_clients(current_user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute('SELECT * FROM clients WHERE user_id = %s ORDER BY created_at DESC', (current_user_id,))
    clients = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify(clients), 200

@app.route('/api/clients', methods=['POST'])
@token_required
def create_client(current_user_id):
    data = request.get_json()
    
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    
    if not name:
        return jsonify({'message': 'Name is required'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute(
        'INSERT INTO clients (name, email, phone, user_id) VALUES (%s, %s, %s, %s) RETURNING *',
        (name, email, phone, current_user_id)
    )
    client = cur.fetchone()
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify(client), 201

@app.route('/api/clients/<int:client_id>', methods=['PUT'])
@token_required
def update_client(current_user_id, client_id):
    data = request.get_json()
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Verify ownership
    cur.execute('SELECT * FROM clients WHERE id = %s AND user_id = %s', (client_id, current_user_id))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'message': 'Client not found'}), 404
    
    cur.execute(
        'UPDATE clients SET name = %s, email = %s, phone = %s WHERE id = %s RETURNING *',
        (data.get('name'), data.get('email'), data.get('phone'), client_id)
    )
    client = cur.fetchone()
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify(client), 200

@app.route('/api/clients/<int:client_id>', methods=['DELETE'])
@token_required
def delete_client(current_user_id, client_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verify ownership
    cur.execute('SELECT * FROM clients WHERE id = %s AND user_id = %s', (client_id, current_user_id))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'message': 'Client not found'}), 404
    
    cur.execute('DELETE FROM clients WHERE id = %s', (client_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'message': 'Client deleted'}), 200

# Session Routes
@app.route('/api/sessions', methods=['GET'])
@token_required
def get_sessions(current_user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if end_time column exists, if not add it
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='sessions' AND column_name='end_time'
    """)
    if not cur.fetchone():
        cur.execute('ALTER TABLE sessions ADD COLUMN end_time TIMESTAMP')
        conn.commit()
    
    # Check if location column exists, if not add it
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='sessions' AND column_name='location'
    """)
    if not cur.fetchone():
        cur.execute('ALTER TABLE sessions ADD COLUMN location VARCHAR(200)')
        conn.commit()
    
    cur.execute('''
        SELECT s.*, c.name as client_name 
        FROM sessions s 
        JOIN clients c ON s.client_id = c.id 
        WHERE s.user_id = %s 
        ORDER BY s.session_date DESC
    ''', (current_user_id,))
    sessions = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify(sessions), 200

@app.route('/api/sessions', methods=['POST'])
@token_required
def create_session(current_user_id):
    data = request.get_json()
    
    client_id = data.get('client_id')
    session_date = data.get('session_date')
    duration = data.get('duration')
    notes = data.get('notes')
    end_time = data.get('end_time')
    location = data.get('location')
    
    if not client_id or not session_date:
        return jsonify({'message': 'Client and session date are required'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Verify client ownership
    cur.execute('SELECT * FROM clients WHERE id = %s AND user_id = %s', (client_id, current_user_id))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'message': 'Client not found'}), 404
    
    cur.execute(
        'INSERT INTO sessions (client_id, session_date, duration, notes, end_time, location, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *',
        (client_id, session_date, duration, notes, end_time, location, current_user_id)
    )
    session = cur.fetchone()
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify(session), 201

@app.route('/api/sessions/<int:session_id>', methods=['PUT'])
@token_required
def update_session(current_user_id, session_id):
    data = request.get_json()
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Verify ownership
    cur.execute('SELECT * FROM sessions WHERE id = %s AND user_id = %s', (session_id, current_user_id))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'message': 'Session not found'}), 404
    
    cur.execute(
        'UPDATE sessions SET client_id = %s, session_date = %s, duration = %s, notes = %s, end_time = %s, location = %s WHERE id = %s RETURNING *',
        (data.get('client_id'), data.get('session_date'), data.get('duration'), data.get('notes'), data.get('end_time'), data.get('location'), session_id)
    )
    session = cur.fetchone()
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify(session), 200

@app.route('/api/sessions/<int:session_id>', methods=['DELETE'])
@token_required
def delete_session(current_user_id, session_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Verify ownership
    cur.execute('SELECT * FROM sessions WHERE id = %s AND user_id = %s', (session_id, current_user_id))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'message': 'Session not found'}), 404
    
    cur.execute('DELETE FROM sessions WHERE id = %s', (session_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'message': 'Session deleted'}), 200

# Global OPTIONS handler for CORS preflight requests
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    """Handle all OPTIONS requests for CORS preflight"""
    return '', 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
