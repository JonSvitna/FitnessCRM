"""
Flask Application Factory
Creates and configures the Flask application with EspoCRM-inspired architecture
"""
import os
from flask import Flask
from flask_cors import CORS
from models.database import db
from bootstrap import bootstrap_application

def create_app(config=None):
    """
    Create and configure the Flask application.
    
    Args:
        config: Optional configuration dict
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 
            'postgresql://postgres:postgres@localhost:5432/fitnesscrm'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TESTING=os.environ.get('TESTING', 'false').lower() == 'true',
    )
    
    # Fix for Railway/Heroku postgres URLs (postgres:// -> postgresql://)
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace(
            'postgres://', 'postgresql://', 1
        )
    
    # Override with provided config
    if config:
        app.config.from_mapping(config)
    
    # Configure CORS
    cors_origins = os.environ.get('CORS_ORIGINS', '*')
    CORS(app, 
         resources={r"/*": {"origins": cors_origins}},
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
         supports_credentials=False,
         expose_headers=["Content-Type", "Authorization"],
         max_age=3600
    )
    
    # Initialize database
    db.init_app(app)
    
    # Bootstrap the EspoCRM-inspired architecture
    with app.app_context():
        bootstrap_application()
    
    # Register blueprints
    register_blueprints(app)
    
    # Global OPTIONS handler for CORS preflight requests
    @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        """Handle all OPTIONS requests for CORS preflight"""
        return '', 200
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return {'status': 'ok', 'message': 'FitnessCRM API is running'}, 200
    
    return app


def register_blueprints(app):
    """Register all Flask blueprints"""
    
    # Import blueprints
    from api.routes import api_bp
    from api.entity_routes import entity_api_bp
    from api.auth_routes import auth_bp
    from api.session_routes import sessions_bp
    from api.workout_routes import workout_bp
    from api.exercise_routes import exercise_bp
    from api.goal_routes import goal_bp
    from api.measurement_routes import measurement_bp
    from api.payment_routes import payment_bp
    from api.analytics_routes import analytics_bp
    from api.message_routes import message_bp
    from api.campaign_routes import campaign_bp
    from api.automation_routes import automation_bp
    from api.settings_routes import settings_bp
    from api.activity_routes import activity_bp
    from api.report_routes import report_bp
    from api.advanced_analytics_routes import advanced_analytics_bp
    from api.progress_photo_routes import progress_photo_bp
    from api.ai_routes import ai_bp
    from api.integrations_routes import integrations_bp
    from api.file_routes import file_bp
    from api.sms_routes import sms_bp
    from api.stripe_routes import stripe_bp
    from api.exercisedb_routes import exercisedb_bp
    from api.public_api_v2 import public_api_v2_bp
    from api.audit_routes import audit_bp
    
    # Register core routes
    app.register_blueprint(api_bp)
    app.register_blueprint(entity_api_bp)  # New EspoCRM-inspired entity API
    
    # Register feature blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(workout_bp)
    app.register_blueprint(exercise_bp)
    app.register_blueprint(goal_bp)
    app.register_blueprint(measurement_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(campaign_bp)
    app.register_blueprint(automation_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(advanced_analytics_bp)
    app.register_blueprint(progress_photo_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(integrations_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(sms_bp)
    app.register_blueprint(stripe_bp)
    app.register_blueprint(exercisedb_bp)
    app.register_blueprint(public_api_v2_bp)
    app.register_blueprint(audit_bp)


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
