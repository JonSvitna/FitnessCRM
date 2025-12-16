"""
Workout template API routes
Handles workout template CRUD operations and client assignments
"""
from flask import Blueprint, request, jsonify
from models.database import db, WorkoutTemplate, WorkoutExercise, ClientWorkout, WorkoutLog, Exercise
from datetime import datetime

workout_bp = Blueprint('workouts', __name__, url_prefix='/api/workouts')

@workout_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get all workout templates"""
    try:
        query = WorkoutTemplate.query
        
        # Filter by creator
        created_by = request.args.get('created_by', type=int)
        if created_by:
            query = query.filter_by(created_by=created_by)
        
        # Filter public templates
        show_public = request.args.get('show_public', 'true').lower() == 'true'
        if show_public and not created_by:
            # Show all public templates or user's own templates
            user_id = request.args.get('user_id', type=int)
            if user_id:
                query = query.filter((WorkoutTemplate.is_public == True) | (WorkoutTemplate.created_by == user_id))
        
        # Filter by category
        category = request.args.get('category')
        if category:
            query = query.filter_by(category=category)
        
        # Search by name
        search = request.args.get('search')
        if search:
            query = query.filter(WorkoutTemplate.name.ilike(f'%{search}%'))
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        templates_paginated = query.order_by(WorkoutTemplate.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'templates': [t.to_dict() for t in templates_paginated.items],
            'total': templates_paginated.total,
            'pages': templates_paginated.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workout_bp.route('/templates', methods=['POST'])
def create_template():
    """Create a new workout template"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'created_by']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        template = WorkoutTemplate(
            name=data['name'],
            description=data.get('description'),
            category=data.get('category'),
            difficulty=data.get('difficulty'),
            duration_minutes=data.get('duration_minutes'),
            created_by=data['created_by'],
            is_public=data.get('is_public', False)
        )
        
        db.session.add(template)
        db.session.flush()  # Get the template ID
        
        # Add exercises if provided
        if 'exercises' in data and isinstance(data['exercises'], list):
            for idx, ex_data in enumerate(data['exercises']):
                workout_exercise = WorkoutExercise(
                    workout_template_id=template.id,
                    exercise_id=ex_data['exercise_id'],
                    order=ex_data.get('order', idx),
                    sets=ex_data.get('sets'),
                    reps=ex_data.get('reps'),
                    duration_seconds=ex_data.get('duration_seconds'),
                    rest_seconds=ex_data.get('rest_seconds'),
                    weight=ex_data.get('weight'),
                    notes=ex_data.get('notes')
                )
                db.session.add(workout_exercise)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Workout template created successfully',
            'template': template.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@workout_bp.route('/templates/<int:template_id>', methods=['GET'])
def get_template(template_id):
    """Get a specific workout template with exercises"""
    try:
        template = WorkoutTemplate.query.get_or_404(template_id)
        template_dict = template.to_dict()
        
        # Add exercises
        exercises = WorkoutExercise.query.filter_by(workout_template_id=template_id).order_by(WorkoutExercise.order).all()
        template_dict['exercises'] = [e.to_dict() for e in exercises]
        
        return jsonify(template_dict)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workout_bp.route('/templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """Update a workout template"""
    try:
        template = WorkoutTemplate.query.get_or_404(template_id)
        data = request.get_json()
        
        # Update template fields
        updatable_fields = ['name', 'description', 'category', 'difficulty', 'duration_minutes', 'is_public']
        for field in updatable_fields:
            if field in data:
                setattr(template, field, data[field])
        
        # Update exercises if provided
        if 'exercises' in data:
            # Remove existing exercises
            WorkoutExercise.query.filter_by(workout_template_id=template_id).delete()
            
            # Add new exercises
            for idx, ex_data in enumerate(data['exercises']):
                workout_exercise = WorkoutExercise(
                    workout_template_id=template.id,
                    exercise_id=ex_data['exercise_id'],
                    order=ex_data.get('order', idx),
                    sets=ex_data.get('sets'),
                    reps=ex_data.get('reps'),
                    duration_seconds=ex_data.get('duration_seconds'),
                    rest_seconds=ex_data.get('rest_seconds'),
                    weight=ex_data.get('weight'),
                    notes=ex_data.get('notes')
                )
                db.session.add(workout_exercise)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Workout template updated successfully',
            'template': template.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@workout_bp.route('/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete a workout template"""
    try:
        template = WorkoutTemplate.query.get_or_404(template_id)
        
        # Check if template is assigned to any clients
        assignments = ClientWorkout.query.filter_by(workout_template_id=template_id, status='active').count()
        if assignments > 0:
            return jsonify({
                'error': f'Cannot delete template. It is assigned to {assignments} active client(s).'
            }), 400
        
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({'message': 'Workout template deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@workout_bp.route('/assign', methods=['POST'])
def assign_workout():
    """Assign a workout template to a client"""
    try:
        data = request.get_json()
        
        required_fields = ['client_id', 'workout_template_id', 'assigned_by']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        assignment = ClientWorkout(
            client_id=data['client_id'],
            workout_template_id=data['workout_template_id'],
            assigned_by=data['assigned_by'],
            start_date=datetime.fromisoformat(data['start_date']) if 'start_date' in data else None,
            end_date=datetime.fromisoformat(data['end_date']) if 'end_date' in data else None,
            frequency_per_week=data.get('frequency_per_week'),
            notes=data.get('notes'),
            status=data.get('status', 'active')
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        return jsonify({
            'message': 'Workout assigned successfully',
            'assignment': assignment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@workout_bp.route('/assignments/<int:client_id>', methods=['GET'])
def get_client_assignments(client_id):
    """Get all workout assignments for a client"""
    try:
        status = request.args.get('status', 'active')
        
        query = ClientWorkout.query.filter_by(client_id=client_id)
        if status:
            query = query.filter_by(status=status)
        
        assignments = query.order_by(ClientWorkout.assigned_date.desc()).all()
        
        return jsonify({
            'assignments': [a.to_dict() for a in assignments]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workout_bp.route('/assignments/<int:assignment_id>', methods=['PUT'])
def update_assignment(assignment_id):
    """Update a workout assignment"""
    try:
        assignment = ClientWorkout.query.get_or_404(assignment_id)
        data = request.get_json()
        
        updatable_fields = ['start_date', 'end_date', 'frequency_per_week', 'notes', 'status']
        for field in updatable_fields:
            if field in data:
                if field in ['start_date', 'end_date'] and data[field]:
                    setattr(assignment, field, datetime.fromisoformat(data[field]).date())
                else:
                    setattr(assignment, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Assignment updated successfully',
            'assignment': assignment.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@workout_bp.route('/log', methods=['POST'])
def log_workout():
    """Log a completed workout"""
    try:
        data = request.get_json()
        
        required_fields = ['client_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        log = WorkoutLog(
            client_id=data['client_id'],
            client_workout_id=data.get('client_workout_id'),
            workout_template_id=data.get('workout_template_id'),
            duration_minutes=data.get('duration_minutes'),
            difficulty_rating=data.get('difficulty_rating'),
            notes=data.get('notes')
        )
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': 'Workout logged successfully',
            'log': log.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@workout_bp.route('/logs/<int:client_id>', methods=['GET'])
def get_client_logs(client_id):
    """Get workout logs for a client"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        logs = WorkoutLog.query.filter_by(client_id=client_id).order_by(
            WorkoutLog.completed_date.desc()
        ).limit(limit).all()
        
        return jsonify({
            'logs': [log.to_dict() for log in logs]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workout_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get workout categories"""
    categories = [
        {'value': 'strength', 'label': 'Strength Training'},
        {'value': 'cardio', 'label': 'Cardiovascular'},
        {'value': 'hiit', 'label': 'HIIT'},
        {'value': 'circuit', 'label': 'Circuit Training'},
        {'value': 'flexibility', 'label': 'Flexibility'},
        {'value': 'sports', 'label': 'Sports Specific'},
        {'value': 'recovery', 'label': 'Recovery/Mobility'}
    ]
    return jsonify({'categories': categories})
