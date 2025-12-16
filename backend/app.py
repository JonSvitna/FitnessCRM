from flask import Flask, jsonify
from flask_cors import CORS
from config.settings import config
from models.database import db
from api.routes import api_bp
from api.settings_routes import settings_bp
from api.activity_routes import activity_bp
from utils.logger import logger, LoggerMiddleware
import os

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Add logging middleware
    app.wsgi_app = LoggerMiddleware(app.wsgi_app)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(activity_bp)
    
    # Root endpoint
    @app.route('/')
    def index():
        logger.info("Root endpoint accessed")
        return jsonify({
            'message': 'Fitness CRM API',
            'version': '1.0.0',
            'endpoints': {
                'trainers': '/api/trainers',
                'clients': '/api/clients',
                'crm': '/api/crm',
                'settings': '/api/settings',
                'activity': '/api/activity',
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
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.warning(f"Database initialization failed: {str(e)}. App will start but database operations will fail.")
    
    return app

# Create app instance for WSGI servers (gunicorn, etc.)
# This is required for the Procfile command "gunicorn app:app" to work
app = create_app()

if __name__ == '__main__':
    # Development server uses the same app instance created above
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting Fitness CRM API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
