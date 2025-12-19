"""
Main API routes for AI Orchestrator
"""
from flask import Blueprint, request, jsonify
from models import db
from models.agent import Agent, AgentExecution, AgentMetric, SystemHealth, CodeSuggestion
from agents.orchestrator import AgentOrchestrator
from agents.workout_optimizer import WorkoutOptimizerAgent
from agents.progress_monitor import ProgressMonitorAgent
from agents.health_checker import HealthCheckerAgent
from agents.code_analyzer import CodeAnalyzerAgent
from utils.logger import logger
import os
import asyncio

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize orchestrator
orchestrator = None

def get_orchestrator():
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        orchestrator = AgentOrchestrator(api_key, model)
    return orchestrator


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ai-orchestrator',
        'version': '1.0.0'
    }), 200


@api_bp.route('/agents', methods=['GET'])
def list_agents():
    """List all configured agents"""
    try:
        agents = Agent.query.all()
        return jsonify({
            'agents': [agent.to_dict() for agent in agents],
            'total': len(agents)
        }), 200
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/agents', methods=['POST'])
def create_agent():
    """Create new agent configuration"""
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        if not data.get('name') or not data.get('type'):
            return jsonify({'error': 'name and type are required'}), 400
        
        # Check if agent with same name exists
        existing = Agent.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': 'Agent with this name already exists'}), 400
        
        agent = Agent(
            name=data['name'],
            type=data['type'],
            description=data.get('description', ''),
            config=data.get('config', {}),
            enabled=data.get('enabled', True),
            status='inactive'
        )
        
        db.session.add(agent)
        db.session.commit()
        
        logger.info(f"Created agent: {agent.name} (ID: {agent.id})")
        
        return jsonify({
            'message': 'Agent created successfully',
            'agent': agent.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/agents/<int:agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get specific agent"""
    try:
        agent = Agent.query.get(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        return jsonify({'agent': agent.to_dict()}), 200
    except Exception as e:
        logger.error(f"Error getting agent: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/agents/<int:agent_id>', methods=['PUT'])
def update_agent(agent_id):
    """Update agent configuration"""
    try:
        agent = Agent.query.get(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        data = request.get_json() or {}
        
        # Update fields
        if 'name' in data:
            agent.name = data['name']
        if 'description' in data:
            agent.description = data['description']
        if 'config' in data:
            agent.config = data['config']
        if 'enabled' in data:
            agent.enabled = data['enabled']
        if 'status' in data:
            agent.status = data['status']
        
        db.session.commit()
        
        logger.info(f"Updated agent: {agent.name} (ID: {agent.id})")
        
        return jsonify({
            'message': 'Agent updated successfully',
            'agent': agent.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating agent: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/agents/<int:agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    """Delete agent"""
    try:
        agent = Agent.query.get(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        db.session.delete(agent)
        db.session.commit()
        
        logger.info(f"Deleted agent: {agent.name} (ID: {agent.id})")
        
        return jsonify({'message': 'Agent deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting agent: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/execute', methods=['POST'])
def execute_agent():
    """Execute an agent or orchestrated workflow"""
    try:
        data = request.get_json() or {}
        
        task_type = data.get('task_type')
        if not task_type:
            return jsonify({'error': 'task_type is required'}), 400
        
        input_data = data.get('input_data', {})
        
        # Execute using orchestrator
        orch = get_orchestrator()
        result = asyncio.run(orch.execute(task_type, input_data))
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error executing agent: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@api_bp.route('/executions', methods=['GET'])
def list_executions():
    """List agent executions"""
    try:
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        agent_id = request.args.get('agent_id', type=int)
        status = request.args.get('status')
        
        query = AgentExecution.query
        
        if agent_id:
            query = query.filter_by(agent_id=agent_id)
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(AgentExecution.started_at.desc())
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'executions': [ex.to_dict() for ex in paginated.items],
            'total': paginated.total,
            'page': page,
            'per_page': per_page,
            'pages': paginated.pages
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing executions: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/health-status', methods=['GET'])
def get_health_status():
    """Get system health status"""
    try:
        # Get latest health checks
        health_checks = SystemHealth.query.order_by(
            SystemHealth.checked_at.desc()
        ).limit(10).all()
        
        return jsonify({
            'health_checks': [hc.to_dict() for hc in health_checks],
            'total': len(health_checks)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting health status: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/suggestions', methods=['GET'])
def list_suggestions():
    """List code suggestions"""
    try:
        status = request.args.get('status', 'pending')
        severity = request.args.get('severity')
        
        query = CodeSuggestion.query
        
        if status:
            query = query.filter_by(status=status)
        if severity:
            query = query.filter_by(severity=severity)
        
        query = query.order_by(CodeSuggestion.created_at.desc())
        
        suggestions = query.limit(100).all()
        
        return jsonify({
            'suggestions': [s.to_dict() for s in suggestions],
            'total': len(suggestions)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing suggestions: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/suggestions/<int:suggestion_id>', methods=['PUT'])
def update_suggestion(suggestion_id):
    """Update suggestion status"""
    try:
        suggestion = CodeSuggestion.query.get(suggestion_id)
        if not suggestion:
            return jsonify({'error': 'Suggestion not found'}), 404
        
        data = request.get_json() or {}
        
        if 'status' in data:
            suggestion.status = data['status']
            if data['status'] in ['accepted', 'rejected', 'applied']:
                from datetime import datetime
                suggestion.resolved_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Suggestion updated successfully',
            'suggestion': suggestion.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating suggestion: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get agent performance metrics"""
    try:
        agent_id = request.args.get('agent_id', type=int)
        
        query = AgentMetric.query
        
        if agent_id:
            query = query.filter_by(agent_id=agent_id)
        
        metrics = query.order_by(AgentMetric.created_at.desc()).limit(100).all()
        
        return jsonify({
            'metrics': [m.to_dict() for m in metrics],
            'total': len(metrics)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500
