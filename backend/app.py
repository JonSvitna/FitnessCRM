from flask import Flask, jsonify
from flask_cors import CORS
from config.settings import config
from models.database import db
from api.routes import api_bp
from api.settings_routes import settings_bp
from api.activity_routes import activity_bp
from api.session_routes import session_bp
from api.measurement_routes import measurement_bp
from api.file_routes import file_bp
from api.exercise_routes import exercise_bp
from api.workout_routes import workout_bp
from api.progress_photo_routes import progress_photo_bp
from api.goal_routes import goal_bp
from api.payment_routes import payment_bp
from api.analytics_routes import analytics_bp
from api.report_routes import report_bp
from utils.logger import logger, LoggerMiddleware
from utils.email import init_mail
import os

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    init_mail(app)
    
    # CORS Configuration
    # Use regex to match all Vercel deployments (they change per deployment)
    import re
    
    # Match any Vercel URL and localhost
    vercel_pattern = r"^https://.*\.vercel\.app$"
    
    CORS(app,
         resources={r"/*": {"origins": "*"}},  # Allow all origins temporarily
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Add logging middleware
    app.wsgi_app = LoggerMiddleware(app.wsgi_app)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(measurement_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(exercise_bp)
    app.register_blueprint(workout_bp)
    app.register_blueprint(progress_photo_bp)
    app.register_blueprint(goal_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(report_bp)
    
    # Root endpoint
    @app.route('/')
    def index():
        logger.info("Root endpoint accessed")
        return jsonify({
            'message': 'Fitness CRM API',
            'version': '1.3.0',
            'endpoints': {
                'trainers': '/api/trainers',
                'clients': '/api/clients',
                'crm': '/api/crm',
                'settings': '/api/settings',
                'activity': '/api/activity',
                'sessions': '/api/sessions',
                'measurements': '/api/measurements',
                'files': '/api/files',
                'exercises': '/api/exercises',
                'workouts': '/api/workouts',
                'payments': '/api/payments',
                'analytics': '/api/analytics',
                'reports': '/api/reports',
                'health': '/api/health'
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"404 error: {error}")
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {error}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    # Create tables (non-blocking for health checks)
    # Skip during boot to allow Railway health checks to succeed
    # Tables will be created on first database access
    if os.getenv('SKIP_DB_INIT') != 'true':
        with app.app_context():
            try:
                db.create_all()
                logger.info("Database tables created/verified")
            except Exception as e:
                logger.warning(f"Database initialization failed: {str(e)}. App will start but database operations will fail.")
    else:
        logger.info("Skipping database initialization (SKIP_DB_INIT=true)")
    
    return app

# Create app instance for WSGI servers (gunicorn, etc.)
# This is required for the Procfile command "gunicorn app:app" to work
app = create_app()

if __name__ == '__main__':
    # Development server uses the same app instance created above
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting Fitness CRM API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
