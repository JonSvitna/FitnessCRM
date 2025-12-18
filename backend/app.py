from flask import Flask, jsonify
from flask_cors import CORS
from config.settings import config
from models.database import db
from utils.logger import logger, LoggerMiddleware
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
from api.integrations_routes import integrations_bp
from api.public_api_v2 import public_api_v2
from api.ai_routes import ai_bp
from api.advanced_analytics_routes import advanced_analytics_bp
from api.auth_routes import auth_bp
from api.audit_routes import audit_bp

# Import Stripe routes (optional - for Phase 6 M6.3)
stripe_bp = None
STRIPE_AVAILABLE = False
try:
    from api.stripe_routes import stripe_bp
    STRIPE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Failed to import Stripe routes: {e}. Stripe features will be disabled.")
except Exception as e:
    logger.warning(f"Failed to import Stripe routes: {e}. Stripe features will be disabled.")

# Import SMS routes (optional - for Phase 5 M5.2)
sms_bp = None
sms_import_error = None
try:
    from api.sms_routes import sms_bp
except Exception as e:
    import sys
    sms_import_error = str(e)
    print(f"Warning: Failed to import SMS routes: {e}. SMS features will be disabled.", file=sys.stderr)
    logger.error(f"SMS routes import error: {e}", exc_info=True)

# Import Campaign routes (optional - for Phase 5 M5.3)
campaign_bp = None
campaign_import_error = None
try:
    from api.campaign_routes import campaign_bp
except Exception as e:
    import sys
    campaign_import_error = str(e)
    print(f"Warning: Failed to import Campaign routes: {e}. Email campaign features will be disabled.", file=sys.stderr)
    logger.error(f"Campaign routes import error: {e}", exc_info=True)

# Import Automation routes (optional - for Phase 5 M5.4)
automation_bp = None
automation_import_error = None
try:
    from api.automation_routes import automation_bp
except Exception as e:
    import sys
    automation_import_error = str(e)
    print(f"Warning: Failed to import Automation routes: {e}. Automation features will be disabled.", file=sys.stderr)
    logger.error(f"Automation routes import error: {e}", exc_info=True)
from utils.email import init_mail
import os

# Import message routes (optional - for Phase 5 M5.1)
message_bp = None
message_import_error = None
try:
    from api.message_routes import message_bp
except Exception as e:
    import sys
    message_import_error = str(e)
    print(f"Warning: Failed to import message routes: {e}. Messaging features will be disabled.", file=sys.stderr)
    logger.error(f"Message routes import error: {e}", exc_info=True)

# Initialize SocketIO globally (optional - may fail in some environments)
socketio = None
try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
    socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')
except ImportError:
    import sys
    print("Warning: Flask-SocketIO not available. Real-time messaging will be disabled.", file=sys.stderr)
except Exception as e:
    import sys
    print(f"Warning: Failed to initialize SocketIO: {e}. Real-time messaging will be disabled.", file=sys.stderr)

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    init_mail(app)
    
    # Initialize SocketIO for real-time messaging (if available)
    if socketio:
        try:
            socketio.init_app(app)
        except Exception as e:
            logger.warning(f"Failed to initialize SocketIO with app: {e}")
    
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
    
    # Register Stripe routes if available
    if STRIPE_AVAILABLE and stripe_bp:
        try:
            app.register_blueprint(stripe_bp)
            logger.info("Stripe routes registered successfully")
        except Exception as e:
            logger.warning(f"Failed to register Stripe routes: {e}")
    
    # Register integrations routes
    app.register_blueprint(integrations_bp)
    
    # Register public API v2
    app.register_blueprint(public_api_v2)
    
    # Register AI routes
    app.register_blueprint(ai_bp)
    
    # Register advanced analytics routes
    app.register_blueprint(advanced_analytics_bp)
    
    # Register authentication routes
    app.register_blueprint(auth_bp)
    
    # Register audit routes
    app.register_blueprint(audit_bp)
    
    app.register_blueprint(analytics_bp)
    app.register_blueprint(report_bp)
    # Register communication blueprints
    if sms_bp:
        app.register_blueprint(sms_bp)
        logger.info("SMS routes registered")
    else:
        logger.warning("SMS routes not available - blueprint import failed")
    
    if campaign_bp:
        app.register_blueprint(campaign_bp)
        logger.info("Campaign routes registered")
    else:
        logger.warning("Campaign routes not available - blueprint import failed")
    
    if automation_bp:
        app.register_blueprint(automation_bp)
        logger.info("Automation routes registered")
    else:
        logger.warning("Automation routes not available - blueprint import failed")
    
    if message_bp:
        app.register_blueprint(message_bp)
        logger.info("Message routes registered")
    else:
        logger.warning("Message routes not available - blueprint import failed")
    
    # Root endpoint
    @app.route('/')
    def index():
        logger.info("Root endpoint accessed")
        endpoints = {
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
        }
        
        # Add communication endpoints if available
        if sms_bp:
            endpoints['sms'] = '/api/sms'
        if campaign_bp:
            endpoints['campaigns'] = '/api/campaigns'
        if automation_bp:
            endpoints['automation'] = '/api/automation'
        if message_bp:
            endpoints['messages'] = '/api/messages'
        
        endpoints['health'] = '/api/health'
        
        response_data = {
            'message': 'Fitness CRM API',
            'version': '1.4.0',
            'endpoints': endpoints,
            'communication_features': {
                'sms': sms_bp is not None,
                'campaigns': campaign_bp is not None,
                'automation': automation_bp is not None,
                'messages': message_bp is not None
            }
        }
        
        # Add import errors for debugging (if any occurred)
        import_errors = {}
        if sms_import_error:
            import_errors['sms'] = sms_import_error
        if campaign_import_error:
            import_errors['campaigns'] = campaign_import_error
        if automation_import_error:
            import_errors['automation'] = automation_import_error
        if message_import_error:
            import_errors['messages'] = message_import_error
        
        if import_errors:
            response_data['import_errors'] = import_errors
        
        return jsonify(response_data), 200
    
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
                
                # Create default admin user if it doesn't exist
                try:
                    from models.user import User
                    from utils.auth import hash_password
                    
                    admin = User.query.filter_by(email='admin@fitnesscrm.com').first()
                    if not admin:
                        default_password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')
                        admin = User(
                            email='admin@fitnesscrm.com',
                            password_hash=hash_password(default_password),
                            role='admin',
                            active=True
                        )
                        db.session.add(admin)
                        db.session.commit()
                        logger.info("Default admin user created: admin@fitnesscrm.com")
                except Exception as e:
                    logger.warning(f"Could not create default admin user: {str(e)}")
                    
            except Exception as e:
                logger.warning(f"Database initialization failed: {str(e)}. App will start but database operations will fail.")
    else:
        logger.info("Skipping database initialization (SKIP_DB_INIT=true)")
    
    # SocketIO event handlers (only if SocketIO is available)
    if socketio:
        @socketio.on('connect')
        def handle_connect():
            logger.info('Client connected to SocketIO')
        
        @socketio.on('disconnect')
        def handle_disconnect():
            logger.info('Client disconnected from SocketIO')
        
        @socketio.on('join_thread')
        def handle_join_thread(data):
            """Join a message thread room"""
            thread_id = data.get('thread_id')
            if thread_id:
                join_room(f'thread_{thread_id}')
                logger.info(f'User joined thread {thread_id}')
        
        @socketio.on('leave_thread')
        def handle_leave_thread(data):
            """Leave a message thread room"""
            thread_id = data.get('thread_id')
            if thread_id:
                leave_room(f'thread_{thread_id}')
                logger.info(f'User left thread {thread_id}')
        
        @socketio.on('new_message')
        def handle_new_message(data):
            """Broadcast new message to thread participants"""
            thread_id = data.get('thread_id')
            message_data = data.get('message')
            if thread_id and message_data:
                emit('message_received', message_data, room=f'thread_{thread_id}')
                logger.info(f'Message broadcasted to thread {thread_id}')
    
    return app

# Create app instance for WSGI servers (gunicorn, etc.)
# This is required for the Procfile command "gunicorn app:app" to work
app = create_app()

if __name__ == '__main__':
    # Development server uses the same app instance created above
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting Fitness CRM API on port {port}")
    if socketio:
        socketio.run(app, host='0.0.0.0', port=port, debug=True)
    else:
        app.run(host='0.0.0.0', port=port, debug=True)
