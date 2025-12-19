"""
AI Orchestrator Flask Application
Main entry point for the AI orchestrator service
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config.settings import config
from models import db
from api.routes import api_bp
from utils.logger import logger
import os


def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # CORS Configuration - Allow all origins for AI orchestrator
    CORS(app,
         resources={r"/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'service': 'AI Orchestrator',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'agents': '/api/agents',
                'execute': '/api/execute',
                'executions': '/api/executions',
                'health_status': '/api/health-status',
                'suggestions': '/api/suggestions',
                'metrics': '/api/metrics'
            },
            'features': {
                'self_healing': app.config.get('ENABLE_SELF_HEALING', False),
                'code_monitoring': app.config.get('ENABLE_CODE_MONITORING', False),
                'workout_optimization': app.config.get('ENABLE_WORKOUT_OPTIMIZATION', False),
                'progress_monitoring': app.config.get('ENABLE_PROGRESS_MONITORING', False),
                'scheduling_intelligence': app.config.get('ENABLE_SCHEDULING_INTELLIGENCE', False)
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {error}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    # Create tables
    if os.getenv('SKIP_DB_INIT') != 'true':
        with app.app_context():
            try:
                db.create_all()
                logger.info("Database tables created/verified for AI Orchestrator")
                
                # Initialize default agents if none exist
                from models.agent import Agent
                if Agent.query.count() == 0:
                    logger.info("Initializing default agents...")
                    _initialize_default_agents()
                    
            except Exception as e:
                logger.warning(f"Database initialization failed: {str(e)}. App will start but database operations will fail.")
    else:
        logger.info("Skipping database initialization (SKIP_DB_INIT=true)")
    
    return app


def _initialize_default_agents():
    """Initialize default AI agents"""
    from models.agent import Agent
    from models import db
    
    default_agents = [
        {
            'name': 'Workout Optimizer',
            'type': 'workout_optimization',
            'description': 'Analyzes client data and generates personalized workout recommendations',
            'config': {
                'model': 'gpt-4-turbo-preview',
                'temperature': 0.7
            },
            'enabled': True
        },
        {
            'name': 'Progress Monitor',
            'type': 'progress_monitoring',
            'description': 'Tracks and analyzes client progress, providing insights and predictions',
            'config': {
                'model': 'gpt-4-turbo-preview',
                'temperature': 0.7
            },
            'enabled': True
        },
        {
            'name': 'Scheduling Intelligence',
            'type': 'scheduling',
            'description': 'Optimizes trainer-client scheduling based on availability and preferences',
            'config': {
                'model': 'gpt-4-turbo-preview',
                'temperature': 0.7
            },
            'enabled': True
        },
        {
            'name': 'Health Checker',
            'type': 'health_check',
            'description': 'Monitors system health and identifies potential issues',
            'config': {
                'model': 'gpt-4-turbo-preview',
                'temperature': 0.3
            },
            'enabled': True
        },
        {
            'name': 'Code Analyzer',
            'type': 'code_analysis',
            'description': 'Analyzes code quality, identifies bugs, and suggests improvements',
            'config': {
                'model': 'gpt-4-turbo-preview',
                'temperature': 0.3
            },
            'enabled': True
        }
    ]
    
    for agent_data in default_agents:
        agent = Agent(**agent_data)
        db.session.add(agent)
    
    db.session.commit()
    logger.info(f"Initialized {len(default_agents)} default agents")


# Create app instance for WSGI servers
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    logger.info(f"Starting AI Orchestrator on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
