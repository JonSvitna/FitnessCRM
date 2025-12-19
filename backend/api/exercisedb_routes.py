"""
ExerciseDB API Routes - External exercise library integration
These routes fetch from ExerciseDB API without caching to prevent API ban
"""
from flask import Blueprint, request, jsonify
from utils.exercisedb_service import exercisedb_service
from utils.logger import logger

exercisedb_bp = Blueprint('exercisedb', __name__, url_prefix='/api/exercisedb')

@exercisedb_bp.route('/exercises', methods=['GET'])
def get_exercises():
    """
    Get exercises from ExerciseDB API (NO CACHING - fetches live data)
    
    Query parameters:
        - body_part: Filter by body part (e.g., 'back', 'chest')
        - equipment: Filter by equipment (e.g., 'barbell', 'dumbbell')
        - target: Filter by target muscle (e.g., 'biceps', 'quads')
        - search: Search by exercise name
        - limit: Number of results (default: 20, max: 50)
        - offset: Pagination offset (default: 0)
    
    Returns:
        JSON with exercises array and metadata
    """
    try:
        body_part = request.args.get('body_part')
        equipment = request.args.get('equipment')
        target = request.args.get('target')
        search = request.args.get('search')
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Limit max request size to prevent excessive API usage
        if limit > 50:
            limit = 50
        
        exercises = None
        
        # Priority: Most specific filter first
        if search:
            exercises = exercisedb_service.search_exercises(search)
        elif target:
            exercises = exercisedb_service.get_exercises_by_target(target)
        elif body_part:
            exercises = exercisedb_service.get_exercises_by_body_part(body_part)
        elif equipment:
            exercises = exercisedb_service.get_exercises_by_equipment(equipment)
        else:
            exercises = exercisedb_service.get_all_exercises(limit=limit, offset=offset)
        
        if exercises is None:
            return jsonify({
                'error': 'ExerciseDB API not configured or unavailable',
                'message': 'Please configure EXERCISEDB_API_KEY in environment variables',
                'exercises': []
            }), 503
        
        # Format exercises to standardized format
        formatted_exercises = [
            exercisedb_service.format_exercise(ex) for ex in exercises
        ]
        
        # Apply limit for filtered results (API doesn't paginate filtered results)
        if (body_part or equipment or target or search) and limit:
            formatted_exercises = formatted_exercises[offset:offset + limit]
        
        # Get usage statistics
        usage = exercisedb_service.get_request_usage()
        
        return jsonify({
            'exercises': formatted_exercises,
            'count': len(formatted_exercises),
            'source': 'exercisedb',
            'cached': False,  # Always False - no caching
            'usage': usage
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching ExerciseDB exercises: {str(e)}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@exercisedb_bp.route('/exercises/<exercise_id>', methods=['GET'])
def get_exercise_detail(exercise_id):
    """
    Get specific exercise details from ExerciseDB API (NO CACHING)
    
    Args:
        exercise_id: ExerciseDB exercise ID
    
    Returns:
        JSON with exercise details
    """
    try:
        exercise = exercisedb_service.get_exercise_by_id(exercise_id)
        
        if not exercise:
            return jsonify({
                'error': 'Exercise not found or API unavailable',
                'exercise_id': exercise_id
            }), 404
        
        formatted = exercisedb_service.format_exercise(exercise)
        
        return jsonify({
            'exercise': formatted,
            'source': 'exercisedb',
            'cached': False
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching exercise detail {exercise_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@exercisedb_bp.route('/body-parts', methods=['GET'])
def get_body_parts():
    """
    Get list of available body parts from ExerciseDB (NO CACHING)
    
    Returns:
        JSON with array of body part names
    """
    try:
        body_parts = exercisedb_service.get_body_part_list()
        
        if not body_parts:
            return jsonify({
                'error': 'API unavailable',
                'body_parts': []
            }), 503
        
        return jsonify({
            'body_parts': sorted(body_parts),
            'count': len(body_parts),
            'cached': False
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching body parts: {str(e)}")
        return jsonify({'error': str(e)}), 500

@exercisedb_bp.route('/targets', methods=['GET'])
def get_targets():
    """
    Get list of available target muscles from ExerciseDB (NO CACHING)
    
    Returns:
        JSON with array of target muscle names
    """
    try:
        targets = exercisedb_service.get_target_list()
        
        if not targets:
            return jsonify({
                'error': 'API unavailable',
                'targets': []
            }), 503
        
        return jsonify({
            'targets': sorted(targets),
            'count': len(targets),
            'cached': False
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching targets: {str(e)}")
        return jsonify({'error': str(e)}), 500

@exercisedb_bp.route('/equipment', methods=['GET'])
def get_equipment():
    """
    Get list of available equipment types from ExerciseDB (NO CACHING)
    
    Returns:
        JSON with array of equipment type names
    """
    try:
        equipment = exercisedb_service.get_equipment_list()
        
        if not equipment:
            return jsonify({
                'error': 'API unavailable',
                'equipment': []
            }), 503
        
        return jsonify({
            'equipment': sorted(equipment),
            'count': len(equipment),
            'cached': False
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching equipment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@exercisedb_bp.route('/usage', methods=['GET'])
def get_usage():
    """
    Get current API usage statistics
    
    Returns:
        JSON with usage information
    """
    try:
        usage = exercisedb_service.get_request_usage()
        
        return jsonify({
            'usage': usage,
            'warning': usage['percentage_used'] > 90,
            'message': 'Approaching daily limit' if usage['percentage_used'] > 90 else 'Usage normal'
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching usage: {str(e)}")
        return jsonify({'error': str(e)}), 500
