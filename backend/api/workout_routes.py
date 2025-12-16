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

# Exercise endpoints
@workout_bp.route('/exercises', methods=['GET'])
def get_exercises():
    """Get all exercises with optional filters"""
    try:
        query = Exercise.query
        
        # Filter by category
        category = request.args.get('category')
        if category:
            query = query.filter_by(category=category)
        
        # Filter by muscle group
        muscle_group = request.args.get('muscle_group')
        if muscle_group:
            query = query.filter_by(muscle_group=muscle_group)
        
        # Filter by equipment
        equipment = request.args.get('equipment')
        if equipment:
            query = query.filter_by(equipment=equipment)
        
        # Filter by difficulty
        difficulty = request.args.get('difficulty')
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        
        # Search by name
        search = request.args.get('search')
        if search:
            query = query.filter(Exercise.name.ilike(f'%{search}%'))
        
        # Filter custom/public exercises
        show_custom = request.args.get('show_custom', 'true').lower() == 'true'
        if not show_custom:
            query = query.filter_by(is_custom=False)
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        
        exercises = query.order_by(Exercise.name).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'exercises': [e.to_dict() for e in exercises.items],
            'total': exercises.total,
            'pages': exercises.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@workout_bp.route('/exercises/categories', methods=['GET'])
def get_exercise_categories():
    """Get exercise categories"""
    categories = [
        {'value': 'strength', 'label': 'Strength'},
        {'value': 'cardio', 'label': 'Cardio'},
        {'value': 'flexibility', 'label': 'Flexibility'},
        {'value': 'core', 'label': 'Core'},
        {'value': 'plyometric', 'label': 'Plyometric'},
        {'value': 'balance', 'label': 'Balance'}
    ]
    return jsonify({'categories': categories})

@workout_bp.route('/exercises/muscle-groups', methods=['GET'])
def get_muscle_groups():
    """Get muscle groups"""
    muscle_groups = [
        {'value': 'chest', 'label': 'Chest'},
        {'value': 'back', 'label': 'Back'},
        {'value': 'shoulders', 'label': 'Shoulders'},
        {'value': 'arms', 'label': 'Arms'},
        {'value': 'legs', 'label': 'Legs'},
        {'value': 'core', 'label': 'Core'},
        {'value': 'cardio', 'label': 'Cardio'},
        {'value': 'flexibility', 'label': 'Flexibility'},
        {'value': 'full-body', 'label': 'Full Body'}
    ]
    return jsonify({'muscle_groups': muscle_groups})

@workout_bp.route('/exercises/equipment', methods=['GET'])
def get_equipment():
    """Get equipment types"""
    equipment = [
        {'value': 'barbell', 'label': 'Barbell'},
        {'value': 'dumbbells', 'label': 'Dumbbells'},
        {'value': 'machine', 'label': 'Machine'},
        {'value': 'bodyweight', 'label': 'Bodyweight'},
        {'value': 'cables', 'label': 'Cables'},
        {'value': 'resistance-bands', 'label': 'Resistance Bands'},
        {'value': 'kettlebell', 'label': 'Kettlebell'},
        {'value': 'medicine-ball', 'label': 'Medicine Ball'},
        {'value': 'jump-rope', 'label': 'Jump Rope'},
        {'value': 'none', 'label': 'None'}
    ]
    return jsonify({'equipment': equipment})

@workout_bp.route('/exercises/seed', methods=['POST'])
def seed_exercises():
    """Seed sample exercises (development only)"""
    try:
        # Check if exercises already exist
        if Exercise.query.count() > 0:
            return jsonify({'message': 'Exercises already seeded', 'count': Exercise.query.count()}), 200
        
        # Get trainer ID from request or use first available
        data = request.get_json() or {}
        trainer_id = data.get('trainer_id')
        
        if not trainer_id:
            from models.database import Trainer
            trainer = Trainer.query.first()
            trainer_id = trainer.id if trainer else None
        
        exercises = [
            Exercise(name='Barbell Bench Press', category='strength', muscle_group='chest', equipment='barbell', difficulty='intermediate', description='Classic chest exercise', is_custom=False, created_by=trainer_id),
            Exercise(name='Dumbbell Flyes', category='strength', muscle_group='chest', equipment='dumbbells', difficulty='beginner', description='Isolation exercise for chest', is_custom=False, created_by=trainer_id),
            Exercise(name='Push-ups', category='strength', muscle_group='chest', equipment='bodyweight', difficulty='beginner', description='Bodyweight chest exercise', is_custom=False, created_by=trainer_id),
            Exercise(name='Pull-ups', category='strength', muscle_group='back', equipment='bodyweight', difficulty='intermediate', description='Upper back and lat exercise', is_custom=False, created_by=trainer_id),
            Exercise(name='Barbell Rows', category='strength', muscle_group='back', equipment='barbell', difficulty='intermediate', description='Compound back exercise', is_custom=False, created_by=trainer_id),
            Exercise(name='Lat Pulldowns', category='strength', muscle_group='back', equipment='machine', difficulty='beginner', description='Cable back exercise', is_custom=False, created_by=trainer_id),
            Exercise(name='Barbell Squats', category='strength', muscle_group='legs', equipment='barbell', difficulty='intermediate', description='King of leg exercises', is_custom=False, created_by=trainer_id),
            Exercise(name='Leg Press', category='strength', muscle_group='legs', equipment='machine', difficulty='beginner', description='Machine-based leg exercise', is_custom=False, created_by=trainer_id),
            Exercise(name='Romanian Deadlifts', category='strength', muscle_group='legs', equipment='barbell', difficulty='intermediate', description='Hamstring and glute exercise', is_custom=False, created_by=trainer_id),
            Exercise(name='Walking Lunges', category='strength', muscle_group='legs', equipment='dumbbells', difficulty='beginner', description='Unilateral leg exercise', is_custom=False, created_by=trainer_id),
            Exercise(name='Overhead Press', category='strength', muscle_group='shoulders', equipment='barbell', difficulty='intermediate', description='Shoulder press movement', is_custom=False, created_by=trainer_id),
            Exercise(name='Lateral Raises', category='strength', muscle_group='shoulders', equipment='dumbbells', difficulty='beginner', description='Shoulder isolation exercise', is_custom=False, created_by=trainer_id),
            Exercise(name='Barbell Curls', category='strength', muscle_group='arms', equipment='barbell', difficulty='beginner', description='Classic bicep exercise', is_custom=False, created_by=trainer_id),
            Exercise(name='Tricep Dips', category='strength', muscle_group='arms', equipment='bodyweight', difficulty='intermediate', description='Bodyweight tricep exercise', is_custom=False, created_by=trainer_id),
            Exercise(name='Plank', category='core', muscle_group='core', equipment='bodyweight', difficulty='beginner', description='Isometric core exercise', is_custom=False, created_by=trainer_id),
            Exercise(name='Russian Twists', category='core', muscle_group='core', equipment='bodyweight', difficulty='beginner', description='Rotational core exercise', is_custom=False, created_by=trainer_id),
            Exercise(name='Running', category='cardio', muscle_group='cardio', equipment='none', difficulty='beginner', description='Cardiovascular endurance', is_custom=False, created_by=trainer_id),
            Exercise(name='Jump Rope', category='cardio', muscle_group='cardio', equipment='jump-rope', difficulty='beginner', description='High-intensity cardio', is_custom=False, created_by=trainer_id),
            Exercise(name='Burpees', category='cardio', muscle_group='cardio', equipment='bodyweight', difficulty='intermediate', description='Full-body cardio exercise', is_custom=False, created_by=trainer_id),
            Exercise(name='Downward Dog', category='flexibility', muscle_group='flexibility', equipment='none', difficulty='beginner', description='Yoga pose for flexibility', is_custom=False, created_by=trainer_id),
        ]
        
        db.session.bulk_save_objects(exercises)
        db.session.commit()
        
        return jsonify({
            'message': 'Exercises seeded successfully',
            'count': len(exercises)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
