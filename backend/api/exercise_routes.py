"""
Exercise library API routes
Handles exercise CRUD operations and library management
"""
from flask import Blueprint, request, jsonify
from models.database import db, Exercise, WorkoutTemplate, WorkoutExercise, ClientWorkout, WorkoutLog
from sqlalchemy import or_

exercise_bp = Blueprint('exercises', __name__, url_prefix='/api/exercises')

@exercise_bp.route('', methods=['GET'])
def get_exercises():
    """Get all exercises with optional filters"""
    try:
        query = Exercise.query
        
        # Search by name
        search = request.args.get('search')
        if search:
            query = query.filter(Exercise.name.ilike(f'%{search}%'))
        
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
        
        # Filter custom exercises
        show_custom = request.args.get('show_custom', 'true').lower() == 'true'
        if not show_custom:
            query = query.filter_by(is_custom=False)
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        exercises_paginated = query.order_by(Exercise.name).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'exercises': [e.to_dict() for e in exercises_paginated.items],
            'total': exercises_paginated.total,
            'pages': exercises_paginated.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exercise_bp.route('', methods=['POST'])
def create_exercise():
    """Create a new exercise"""
    try:
        data = request.get_json()
        
        required_fields = ['name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        exercise = Exercise(
            name=data['name'],
            category=data.get('category'),
            muscle_group=data.get('muscle_group'),
            equipment=data.get('equipment'),
            difficulty=data.get('difficulty'),
            description=data.get('description'),
            instructions=data.get('instructions'),
            tips=data.get('tips'),
            image_url=data.get('image_url'),
            video_url=data.get('video_url'),
            is_custom=data.get('is_custom', True),
            created_by=data.get('created_by')
        )
        
        db.session.add(exercise)
        db.session.commit()
        
        return jsonify({
            'message': 'Exercise created successfully',
            'exercise': exercise.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exercise_bp.route('/<int:exercise_id>', methods=['GET'])
def get_exercise(exercise_id):
    """Get a specific exercise"""
    try:
        exercise = Exercise.query.get_or_404(exercise_id)
        return jsonify(exercise.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exercise_bp.route('/<int:exercise_id>', methods=['PUT'])
def update_exercise(exercise_id):
    """Update an exercise"""
    try:
        exercise = Exercise.query.get_or_404(exercise_id)
        data = request.get_json()
        
        # Update fields
        updatable_fields = ['name', 'category', 'muscle_group', 'equipment', 'difficulty',
                           'description', 'instructions', 'tips', 'image_url', 'video_url']
        
        for field in updatable_fields:
            if field in data:
                setattr(exercise, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Exercise updated successfully',
            'exercise': exercise.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exercise_bp.route('/<int:exercise_id>', methods=['DELETE'])
def delete_exercise(exercise_id):
    """Delete an exercise"""
    try:
        exercise = Exercise.query.get_or_404(exercise_id)
        
        # Check if exercise is used in any workout templates
        workout_exercises = WorkoutExercise.query.filter_by(exercise_id=exercise_id).count()
        if workout_exercises > 0:
            return jsonify({
                'error': f'Cannot delete exercise. It is used in {workout_exercises} workout template(s).'
            }), 400
        
        db.session.delete(exercise)
        db.session.commit()
        
        return jsonify({'message': 'Exercise deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exercise_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get exercise categories"""
    categories = [
        {'value': 'strength', 'label': 'Strength Training'},
        {'value': 'cardio', 'label': 'Cardiovascular'},
        {'value': 'flexibility', 'label': 'Flexibility'},
        {'value': 'balance', 'label': 'Balance'},
        {'value': 'sports', 'label': 'Sports Specific'},
        {'value': 'functional', 'label': 'Functional Training'}
    ]
    return jsonify({'categories': categories})

@exercise_bp.route('/muscle-groups', methods=['GET'])
def get_muscle_groups():
    """Get muscle groups"""
    muscle_groups = [
        {'value': 'chest', 'label': 'Chest'},
        {'value': 'back', 'label': 'Back'},
        {'value': 'legs', 'label': 'Legs'},
        {'value': 'shoulders', 'label': 'Shoulders'},
        {'value': 'arms', 'label': 'Arms'},
        {'value': 'core', 'label': 'Core'},
        {'value': 'full_body', 'label': 'Full Body'}
    ]
    return jsonify({'muscle_groups': muscle_groups})

@exercise_bp.route('/equipment', methods=['GET'])
def get_equipment():
    """Get equipment types"""
    equipment = [
        {'value': 'bodyweight', 'label': 'Bodyweight'},
        {'value': 'dumbbells', 'label': 'Dumbbells'},
        {'value': 'barbell', 'label': 'Barbell'},
        {'value': 'kettlebell', 'label': 'Kettlebell'},
        {'value': 'machine', 'label': 'Machine'},
        {'value': 'bands', 'label': 'Resistance Bands'},
        {'value': 'cable', 'label': 'Cable Machine'},
        {'value': 'trx', 'label': 'TRX/Suspension'},
        {'value': 'medicine_ball', 'label': 'Medicine Ball'},
        {'value': 'other', 'label': 'Other'}
    ]
    return jsonify({'equipment': equipment})

@exercise_bp.route('/seed', methods=['POST'])
def seed_exercises():
    """Seed database with common exercises"""
    try:
        # Check if exercises already exist
        if Exercise.query.count() > 0:
            return jsonify({'message': 'Exercises already seeded'}), 200
        
        exercises = [
            # Chest
            Exercise(name='Push-ups', category='strength', muscle_group='chest', equipment='bodyweight', difficulty='beginner',
                    description='Classic upper body exercise', instructions='Start in plank position, lower chest to ground, push back up'),
            Exercise(name='Bench Press', category='strength', muscle_group='chest', equipment='barbell', difficulty='intermediate',
                    description='Fundamental chest exercise', instructions='Lie on bench, lower bar to chest, press up'),
            Exercise(name='Dumbbell Flyes', category='strength', muscle_group='chest', equipment='dumbbells', difficulty='intermediate',
                    description='Chest isolation exercise', instructions='Lie on bench, arc dumbbells out and together'),
            
            # Back
            Exercise(name='Pull-ups', category='strength', muscle_group='back', equipment='bodyweight', difficulty='intermediate',
                    description='Bodyweight back exercise', instructions='Hang from bar, pull chin over bar, lower with control'),
            Exercise(name='Bent-Over Rows', category='strength', muscle_group='back', equipment='barbell', difficulty='intermediate',
                    description='Compound back exercise', instructions='Hinge at hips, row bar to lower chest'),
            Exercise(name='Lat Pulldowns', category='strength', muscle_group='back', equipment='machine', difficulty='beginner',
                    description='Lat development exercise', instructions='Pull bar down to upper chest, control release'),
            
            # Legs
            Exercise(name='Squats', category='strength', muscle_group='legs', equipment='barbell', difficulty='intermediate',
                    description='Fundamental leg exercise', instructions='Bar on back, squat down, drive through heels'),
            Exercise(name='Lunges', category='strength', muscle_group='legs', equipment='bodyweight', difficulty='beginner',
                    description='Unilateral leg exercise', instructions='Step forward, drop back knee, push back up'),
            Exercise(name='Deadlifts', category='strength', muscle_group='legs', equipment='barbell', difficulty='advanced',
                    description='Full body strength exercise', instructions='Hip hinge, grip bar, extend hips and knees'),
            Exercise(name='Leg Press', category='strength', muscle_group='legs', equipment='machine', difficulty='beginner',
                    description='Quad and glute exercise', instructions='Press platform away with feet, control descent'),
            
            # Shoulders
            Exercise(name='Overhead Press', category='strength', muscle_group='shoulders', equipment='barbell', difficulty='intermediate',
                    description='Shoulder strength exercise', instructions='Press bar overhead from shoulders, full extension'),
            Exercise(name='Lateral Raises', category='strength', muscle_group='shoulders', equipment='dumbbells', difficulty='beginner',
                    description='Shoulder isolation', instructions='Raise dumbbells to sides until parallel to ground'),
            
            # Arms
            Exercise(name='Bicep Curls', category='strength', muscle_group='arms', equipment='dumbbells', difficulty='beginner',
                    description='Bicep isolation', instructions='Curl dumbbells up, squeeze bicep, lower with control'),
            Exercise(name='Tricep Dips', category='strength', muscle_group='arms', equipment='bodyweight', difficulty='intermediate',
                    description='Tricep bodyweight exercise', instructions='Lower body between parallel bars, press back up'),
            
            # Core
            Exercise(name='Planks', category='strength', muscle_group='core', equipment='bodyweight', difficulty='beginner',
                    description='Core stability exercise', instructions='Hold rigid plank position on forearms'),
            Exercise(name='Crunches', category='strength', muscle_group='core', equipment='bodyweight', difficulty='beginner',
                    description='Abdominal exercise', instructions='Lie on back, crunch shoulders toward hips'),
            Exercise(name='Russian Twists', category='strength', muscle_group='core', equipment='bodyweight', difficulty='intermediate',
                    description='Oblique exercise', instructions='Sit at 45 degrees, rotate torso side to side'),
            
            # Cardio
            Exercise(name='Running', category='cardio', muscle_group='full_body', equipment='bodyweight', difficulty='beginner',
                    description='Cardiovascular exercise', instructions='Maintain steady pace for duration'),
            Exercise(name='Jump Rope', category='cardio', muscle_group='full_body', equipment='other', difficulty='intermediate',
                    description='High intensity cardio', instructions='Jump over rope with quick foot turnover'),
            Exercise(name='Burpees', category='cardio', muscle_group='full_body', equipment='bodyweight', difficulty='intermediate',
                    description='Full body conditioning', instructions='Drop to push-up, jump feet in, jump up'),
        ]
        
        db.session.add_all(exercises)
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully seeded {len(exercises)} exercises',
            'count': len(exercises)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
