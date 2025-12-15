from flask import Blueprint, request, jsonify
from models.database import db, Trainer, Client, Assignment
from sqlalchemy.exc import IntegrityError
from utils.logger import log_activity, logger

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Trainer Routes
@api_bp.route('/trainers', methods=['GET'])
def get_trainers():
    """Get all trainers"""
    trainers = Trainer.query.all()
    return jsonify([trainer.to_dict() for trainer in trainers]), 200

@api_bp.route('/trainers/<int:trainer_id>', methods=['GET'])
def get_trainer(trainer_id):
    """Get a specific trainer"""
    trainer = Trainer.query.get_or_404(trainer_id)
    return jsonify(trainer.to_dict()), 200

@api_bp.route('/trainers', methods=['POST'])
def create_trainer():
    """Create a new trainer"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Name and email are required'}), 400
    
    try:
        trainer = Trainer(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            specialization=data.get('specialization'),
            certification=data.get('certification'),
            experience=data.get('experience')
        )
        db.session.add(trainer)
        db.session.commit()
        
        log_activity('create', 'trainer', trainer.id, user_identifier=trainer.email,
                    details={'name': trainer.name})
        logger.info(f"Trainer created: {trainer.name} (ID: {trainer.id})")
        
        return jsonify(trainer.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        logger.warning(f"Duplicate trainer email attempted: {data.get('email')}")
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

# Client Routes
@api_bp.route('/clients', methods=['GET'])
def get_clients():
    """Get all clients"""
    clients = Client.query.all()
    return jsonify([client.to_dict() for client in clients]), 200

@api_bp.route('/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    """Get a specific client"""
    client = Client.query.get_or_404(client_id)
    return jsonify(client.to_dict()), 200

@api_bp.route('/clients', methods=['POST'])
def create_client():
    """Create a new client"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Name and email are required'}), 400
    
    try:
        client = Client(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            age=data.get('age'),
            goals=data.get('goals'),
            medical_conditions=data.get('medical_conditions')
        )
        db.session.add(client)
        db.session.commit()
        return jsonify(client.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Client with this email already exists'}), 409
    except Exception as e:
        db.session.rollback()
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
        return jsonify(assignment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
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
    
    return jsonify(health_status), 200
