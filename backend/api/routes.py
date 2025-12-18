from flask import Blueprint, request, jsonify
from models.database import db, Trainer, Client, Assignment
from models.user import User
from sqlalchemy.exc import IntegrityError
from utils.logger import log_activity, logger
from utils.auth import hash_password

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Trainer Routes
@api_bp.route('/trainers', methods=['GET'])
def get_trainers():
    """Get all trainers with optional search and filter"""
    query = Trainer.query
    
    # Search by name, email, or phone
    search = request.args.get('search', '').strip()
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                Trainer.name.ilike(search_pattern),
                Trainer.email.ilike(search_pattern),
                Trainer.phone.ilike(search_pattern)
            )
        )
    
    # Filter by specialization
    specialization = request.args.get('specialization', '').strip()
    if specialization:
        query = query.filter(Trainer.specialization.ilike(f'%{specialization}%'))
    
    # Filter by active status
    active = request.args.get('active')
    if active is not None:
        active_bool = active.lower() in ['true', '1', 'yes']
        query = query.filter(Trainer.active == active_bool)
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    per_page = min(per_page, 100)  # Max 100 items per page
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    query = query.order_by(Trainer.name)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [trainer.to_dict() for trainer in pagination.items],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }), 200

@api_bp.route('/trainers/<int:trainer_id>', methods=['GET'])
def get_trainer(trainer_id):
    """Get a specific trainer"""
    trainer = Trainer.query.get_or_404(trainer_id)
    return jsonify(trainer.to_dict()), 200

@api_bp.route('/trainers', methods=['POST'])
def create_trainer():
    """Create a new trainer and associated user account"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Name and email are required'}), 400
    
    if not data.get('password'):
        return jsonify({'error': 'Password is required'}), 400
    
    if len(data.get('password', '')) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    try:
        # Create trainer
        trainer = Trainer(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            specialization=data.get('specialization'),
            certification=data.get('certification'),
            experience=data.get('experience')
        )
        db.session.add(trainer)
        db.session.flush()  # Get trainer ID without committing
        
        # Create user account for trainer
        user = User(
            email=data['email'],
            password_hash=hash_password(data['password']),
            role='trainer',
            active=True
        )
        db.session.add(user)
        db.session.commit()
        
        log_activity('create', 'trainer', trainer.id, user_identifier=trainer.email,
                    details={'name': trainer.name})
        logger.info(f"Trainer created: {trainer.name} (ID: {trainer.id}) with user account")
        
        return jsonify(trainer.to_dict()), 201
    except IntegrityError as e:
        db.session.rollback()
        logger.warning(f"Duplicate trainer/user email attempted: {data.get('email')}")
        if 'users.email' in str(e) or 'users_email_key' in str(e):
            return jsonify({'error': 'User account with this email already exists'}), 409
        return jsonify({'error': 'Trainer with this email already exists'}), 409
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating trainer: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trainers/<int:trainer_id>', methods=['PUT'])
def update_trainer(trainer_id):
    """Update a trainer"""
    trainer = Trainer.query.get_or_404(trainer_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        if 'name' in data:
            trainer.name = data['name']
        if 'email' in data:
            trainer.email = data['email']
        if 'phone' in data:
            trainer.phone = data['phone']
        if 'specialization' in data:
            trainer.specialization = data['specialization']
        if 'certification' in data:
            trainer.certification = data['certification']
        if 'experience' in data:
            trainer.experience = data['experience']
        
        db.session.commit()
        return jsonify(trainer.to_dict()), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Trainer with this email already exists'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trainers/<int:trainer_id>', methods=['DELETE'])
def delete_trainer(trainer_id):
    """Delete a trainer"""
    trainer = Trainer.query.get_or_404(trainer_id)
    
    try:
        db.session.delete(trainer)
        db.session.commit()
        return jsonify({'message': 'Trainer deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trainers/<int:trainer_id>/check-user', methods=['GET'])
def check_trainer_user(trainer_id):
    """Check if trainer has a User account"""
    trainer = Trainer.query.get_or_404(trainer_id)
    user = User.query.filter_by(email=trainer.email).first()
    
    return jsonify({
        'trainer_id': trainer.id,
        'trainer_email': trainer.email,
        'has_user_account': user is not None,
        'user_role': user.role if user else None,
        'user_active': user.active if user else None,
        'user_id': user.id if user else None
    }), 200

@api_bp.route('/check-email', methods=['POST'])
def check_email():
    """Check if a User account exists for an email address"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    user = User.query.filter_by(email=email).first()
    trainer = Trainer.query.filter_by(email=email).first()
    client = Client.query.filter_by(email=email).first()
    
    return jsonify({
        'email': email,
        'has_user_account': user is not None,
        'user_role': user.role if user else None,
        'user_active': user.active if user else None,
        'is_trainer': trainer is not None,
        'is_client': client is not None,
        'trainer_id': trainer.id if trainer else None,
        'client_id': client.id if client else None,
        'message': 'User account found' if user else 'No User account found. Set password via admin dashboard.'
    }), 200

# Client Routes
@api_bp.route('/clients', methods=['GET'])
def get_clients():
    """Get all clients with optional search and filter"""
    query = Client.query
    
    # Search by name, email, or phone
    search = request.args.get('search', '').strip()
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                Client.name.ilike(search_pattern),
                Client.email.ilike(search_pattern),
                Client.phone.ilike(search_pattern)
            )
        )
    
    # Filter by status
    status = request.args.get('status', '').strip()
    if status:
        query = query.filter(Client.status == status)
    
    # Filter by goals
    goals = request.args.get('goals', '').strip()
    if goals:
        query = query.filter(Client.goals.ilike(f'%{goals}%'))
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    per_page = min(per_page, 100)  # Max 100 items per page
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    query = query.order_by(Client.name)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [client.to_dict() for client in pagination.items],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }), 200

@api_bp.route('/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    """Get a specific client"""
    client = Client.query.get_or_404(client_id)
    return jsonify(client.to_dict()), 200

@api_bp.route('/clients', methods=['POST'])
def create_client():
    """Create a new client and associated user account"""
    from utils.email import send_welcome_email
    
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Name and email are required'}), 400
    
    if not data.get('password'):
        return jsonify({'error': 'Password is required'}), 400
    
    if len(data.get('password', '')) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    try:
        # Create client
        client = Client(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            age=data.get('age'),
            goals=data.get('goals'),
            medical_conditions=data.get('medical_conditions')
        )
        db.session.add(client)
        db.session.flush()  # Get client ID without committing
        
        # Create user account for client
        user = User(
            email=data['email'],
            password_hash=hash_password(data['password']),
            role='client',
            active=True
        )
        db.session.add(user)
        db.session.commit()
        
        # Send welcome email
        send_welcome_email(client.name, client.email)
        
        log_activity('create', 'client', client.id, user_identifier=client.email,
                    details={'name': client.name})
        logger.info(f"Client created: {client.name} (ID: {client.id}) with user account")
        
        return jsonify(client.to_dict()), 201
    except IntegrityError as e:
        db.session.rollback()
        logger.warning(f"Duplicate client/user email attempted: {data.get('email')}")
        if 'users.email' in str(e) or 'users_email_key' in str(e):
            return jsonify({'error': 'User account with this email already exists'}), 409
        return jsonify({'error': 'Client with this email already exists'}), 409
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating client: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/clients/<int:client_id>/change-password', methods=['POST'])
def change_client_password(client_id):
    """Change password for a client's user account. Creates User account if it doesn't exist."""
    client = Client.query.get_or_404(client_id)
    data = request.get_json()
    
    if not data or not data.get('password'):
        return jsonify({'error': 'Password is required'}), 400
    
    if len(data['password']) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    try:
        # Find user account by email
        user = User.query.filter_by(email=client.email).first()
        
        if not user:
            # Create user account if it doesn't exist
            user = User(
                email=client.email,
                password_hash=hash_password(data['password']),
                role='client',
                active=True
            )
            db.session.add(user)
            logger.info(f"Created User account for client: {client.name} (ID: {client.id})")
        else:
            # Update password
            user.password_hash = hash_password(data['password'])
            logger.info(f"Password changed for client: {client.name} (ID: {client.id})")
        
        db.session.commit()
        return jsonify({'message': 'Password set successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error changing client password: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    """Update a client"""
    client = Client.query.get_or_404(client_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        if 'name' in data:
            client.name = data['name']
        if 'email' in data:
            client.email = data['email']
        if 'phone' in data:
            client.phone = data['phone']
        if 'age' in data:
            client.age = data['age']
        if 'goals' in data:
            client.goals = data['goals']
        if 'medical_conditions' in data:
            client.medical_conditions = data['medical_conditions']
        
        db.session.commit()
        return jsonify(client.to_dict()), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Client with this email already exists'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    """Delete a client"""
    client = Client.query.get_or_404(client_id)
    
    try:
        db.session.delete(client)
        db.session.commit()
        return jsonify({'message': 'Client deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# CRM Routes
@api_bp.route('/crm/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard statistics"""
    trainers_count = Trainer.query.count()
    clients_count = Client.query.count()
    assignments_count = Assignment.query.count()
    
    return jsonify({
        'trainers_count': trainers_count,
        'clients_count': clients_count,
        'assignments_count': assignments_count
    }), 200

@api_bp.route('/crm/stats', methods=['GET'])
def get_stats():
    """Get CRM statistics"""
    trainers = Trainer.query.all()
    clients = Client.query.all()
    
    stats = {
        'total_trainers': len(trainers),
        'total_clients': len(clients),
        'trainers_with_clients': len([t for t in trainers if len(t.assignments) > 0]),
        'clients_assigned': len([c for c in clients if len(c.assignments) > 0]),
    }
    
    return jsonify(stats), 200

@api_bp.route('/crm/assign', methods=['POST'])
def assign_client_to_trainer():
    """Assign a client to a trainer"""
    from utils.email import send_assignment_notification, send_client_assignment_notification
    
    data = request.get_json()
    
    if not data or not data.get('trainer_id') or not data.get('client_id'):
        return jsonify({'error': 'trainer_id and client_id are required'}), 400
    
    # Verify trainer and client exist
    trainer = Trainer.query.get(data['trainer_id'])
    client = Client.query.get(data['client_id'])
    
    if not trainer:
        return jsonify({'error': 'Trainer not found'}), 404
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    try:
        assignment = Assignment(
            trainer_id=data['trainer_id'],
            client_id=data['client_id'],
            notes=data.get('notes')
        )
        db.session.add(assignment)
        db.session.commit()
        
        # Send email notifications
        send_assignment_notification(trainer.email, trainer.name, client.name)
        send_client_assignment_notification(client.email, client.name, trainer.name)
        
        log_activity('create', 'assignment', assignment.id,
                    details={'trainer': trainer.name, 'client': client.name})
        logger.info(f"Assignment created: {trainer.name} <-> {client.name}")
        
        return jsonify(assignment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating assignment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/crm/assignments', methods=['GET'])
def get_assignments():
    """Get all assignments"""
    assignments = Assignment.query.all()
    return jsonify([assignment.to_dict() for assignment in assignments]), 200

@api_bp.route('/crm/assignments/<int:assignment_id>', methods=['DELETE'])
def delete_assignment(assignment_id):
    """Delete an assignment"""
    assignment = Assignment.query.get_or_404(assignment_id)
    
    try:
        db.session.delete(assignment)
        db.session.commit()
        return jsonify({'message': 'Assignment deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    health_status = {
        'status': 'healthy',
        'message': 'API is running'
    }
    
    # Check database connectivity
    try:
        db.session.execute(db.text('SELECT 1'))
        health_status['database'] = 'connected'
    except Exception as e:
        health_status['database'] = 'disconnected'
        health_status['database_error'] = str(e)
        logger.warning(f"Database health check failed: {str(e)}")
    finally:
        # Ensure session is cleaned up
        db.session.remove()
    
    return jsonify(health_status), 200
