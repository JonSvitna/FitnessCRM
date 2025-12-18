"""
Advanced Analytics API routes
Phase 7: Advanced Features - M7.3: Advanced Analytics & Insights
"""

from flask import Blueprint, request, jsonify
from models.database import db, Client, Trainer
from utils.analytics_service import (
    predict_client_churn,
    forecast_revenue,
    benchmark_trainer_performance,
    get_predictive_insights
)
from utils.logger import logger

advanced_analytics_bp = Blueprint('advanced_analytics', __name__, url_prefix='/api/analytics/advanced')

@advanced_analytics_bp.route('/churn-prediction/<int:client_id>', methods=['GET'])
def get_churn_prediction(client_id):
    """Get churn prediction for a client"""
    try:
        days_lookback = request.args.get('days_lookback', 90, type=int)
        
        prediction = predict_client_churn(client_id, days_lookback)
        
        if 'error' in prediction:
            return jsonify(prediction), 404 if prediction['error'] == 'Client not found' else 500
        
        return jsonify(prediction), 200
        
    except Exception as e:
        logger.error(f"Error getting churn prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

@advanced_analytics_bp.route('/churn-prediction/batch', methods=['POST'])
def get_batch_churn_predictions():
    """Get churn predictions for multiple clients"""
    data = request.get_json() or {}
    client_ids = data.get('client_ids', [])
    
    if not client_ids:
        return jsonify({'error': 'client_ids array is required'}), 400
    
    try:
        predictions = []
        for client_id in client_ids:
            prediction = predict_client_churn(client_id)
            if 'error' not in prediction:
                predictions.append(prediction)
        
        # Sort by churn probability (highest first)
        predictions.sort(key=lambda x: x['churn_probability'], reverse=True)
        
        return jsonify({
            'predictions': predictions,
            'total': len(predictions),
            'high_risk': len([p for p in predictions if p['risk_level'] == 'high'])
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting batch churn predictions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@advanced_analytics_bp.route('/revenue-forecast', methods=['GET'])
def get_revenue_forecast():
    """Get revenue forecast"""
    try:
        months = request.args.get('months', 6, type=int)
        months = min(max(months, 1), 12)  # Limit to 1-12 months
        
        forecast = forecast_revenue(months)
        
        if 'error' in forecast:
            return jsonify(forecast), 500
        
        return jsonify(forecast), 200
        
    except Exception as e:
        logger.error(f"Error getting revenue forecast: {str(e)}")
        return jsonify({'error': str(e)}), 500

@advanced_analytics_bp.route('/trainer-benchmark/<int:trainer_id>', methods=['GET'])
def get_trainer_benchmark(trainer_id):
    """Get trainer performance benchmark"""
    try:
        benchmark = benchmark_trainer_performance(trainer_id)
        
        if 'error' in benchmark:
            return jsonify(benchmark), 404 if benchmark['error'] == 'Trainer not found' else 500
        
        return jsonify(benchmark), 200
        
    except Exception as e:
        logger.error(f"Error getting trainer benchmark: {str(e)}")
        return jsonify({'error': str(e)}), 500

@advanced_analytics_bp.route('/trainer-benchmark/all', methods=['GET'])
def get_all_trainer_benchmarks():
    """Get benchmarks for all trainers"""
    try:
        trainers = Trainer.query.filter_by(active=True).all()
        
        benchmarks = []
        for trainer in trainers:
            benchmark = benchmark_trainer_performance(trainer.id)
            if 'error' not in benchmark:
                benchmarks.append(benchmark)
        
        # Sort by performance score (highest first)
        benchmarks.sort(key=lambda x: x['performance_score'], reverse=True)
        
        return jsonify({
            'benchmarks': benchmarks,
            'total': len(benchmarks),
            'average_score': round(sum(b['performance_score'] for b in benchmarks) / len(benchmarks), 1) if benchmarks else 0
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting all trainer benchmarks: {str(e)}")
        return jsonify({'error': str(e)}), 500

@advanced_analytics_bp.route('/predictive-insights', methods=['GET'])
def get_predictive_insights_route():
    """Get predictive insights across the platform"""
    try:
        days_lookback = request.args.get('days_lookback', 30, type=int)
        
        insights = get_predictive_insights(days_lookback)
        
        if 'error' in insights:
            return jsonify(insights), 500
        
        return jsonify(insights), 200
        
    except Exception as e:
        logger.error(f"Error getting predictive insights: {str(e)}")
        return jsonify({'error': str(e)}), 500

