"""
AI-powered features API routes
Phase 7: Advanced Features - M7.1: AI-Powered Features

Currently uses seed data. Configure AI_SERVICE_URL and AI_API_KEY
to use external AI service.
"""

from flask import Blueprint, request, jsonify
from models.database import db, Client, Trainer, Session, Goal
from utils.ai_service import (
    get_workout_recommendations,
    predict_client_progress,
    suggest_session_times,
    generate_workout_plan,
    is_ai_configured
)
from utils.logger import logger

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

@ai_bp.route('/status', methods=['GET'])
def get_ai_status():
    """Get AI service status"""
    return jsonify({
        'configured': is_ai_configured(),
        'using_seed_data': not is_ai_configured(),
        'note': 'Currently using seed data. Configure AI_SERVICE_URL and AI_API_KEY for external AI.'
    }), 200

@ai_bp.route('/workout-recommendations', methods=['POST'])
def get_workout_recommendations_route():
    """Get AI-powered workout recommendations"""
    data = request.get_json() or {}
    
    client_id = data.get('client_id')
    if not client_id:
        return jsonify({'error': 'client_id is required'}), 400
    
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    try:
        goals = data.get('goals', [])
        fitness_level = data.get('fitness_level', 'intermediate')
        
        recommendations = get_workout_recommendations(
            client_id=client_id,
            goals=goals,
            fitness_level=fitness_level
        )
        
        return jsonify({
            'recommendations': recommendations,
            'client_id': client_id,
            'fitness_level': fitness_level,
            'source': 'seed_data' if not is_ai_configured() else 'ai_service'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting workout recommendations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/progress-prediction', methods=['POST'])
def get_progress_prediction():
    """Predict client progress"""
    data = request.get_json() or {}
    
    client_id = data.get('client_id')
    if not client_id:
        return jsonify({'error': 'client_id is required'}), 400
    
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    try:
        current_metrics = data.get('current_metrics', {})
        goal_metrics = data.get('goal_metrics', {})
        
        # If not provided, try to get from client's goals
        if not goal_metrics:
            goals = Goal.query.filter_by(client_id=client_id, status='active').all()
            if goals:
                goal_metrics = {
                    goal.category: goal.target_value
                    for goal in goals
                    if goal.target_value
                }
        
        prediction = predict_client_progress(
            client_id=client_id,
            current_metrics=current_metrics,
            goal_metrics=goal_metrics
        )
        
        return jsonify(prediction), 200
        
    except Exception as e:
        logger.error(f"Error predicting progress: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/scheduling-suggestions', methods=['POST'])
def get_scheduling_suggestions():
    """Get AI-powered session scheduling suggestions"""
    data = request.get_json() or {}
    
    client_id = data.get('client_id')
    trainer_id = data.get('trainer_id')
    
    if not client_id or not trainer_id:
        return jsonify({'error': 'client_id and trainer_id are required'}), 400
    
    client = Client.query.get(client_id)
    trainer = Trainer.query.get(trainer_id)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    if not trainer:
        return jsonify({'error': 'Trainer not found'}), 404
    
    try:
        preferred_times = data.get('preferred_times', [])
        
        suggestions = suggest_session_times(
            client_id=client_id,
            trainer_id=trainer_id,
            preferred_times=preferred_times
        )
        
        return jsonify({
            'suggestions': suggestions,
            'client_id': client_id,
            'trainer_id': trainer_id,
            'source': 'seed_data' if not is_ai_configured() else 'ai_service'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting scheduling suggestions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/generate-workout-plan', methods=['POST'])
def generate_workout_plan_route():
    """Generate automated workout plan"""
    data = request.get_json() or {}
    
    client_id = data.get('client_id')
    if not client_id:
        return jsonify({'error': 'client_id is required'}), 400
    
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    try:
        duration_weeks = data.get('duration_weeks', 4)
        focus_areas = data.get('focus_areas', [])
        
        plan = generate_workout_plan(
            client_id=client_id,
            duration_weeks=duration_weeks,
            focus_areas=focus_areas
        )
        
        return jsonify({
            'plan': plan,
            'source': 'seed_data' if not is_ai_configured() else 'ai_service'
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating workout plan: {str(e)}")
        return jsonify({'error': str(e)}), 500

