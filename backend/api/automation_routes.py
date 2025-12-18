"""
Automation API routes for Phase 5: Communication
Handles automated reminders and notifications
"""

from flask import Blueprint, request, jsonify
from models.database import db, AutomationRule, AutomationLog, Client, Trainer, Session, Payment
from utils.email import send_email
from utils.sms import send_sms
from utils.logger import logger
from utils.automation import _execute_automation_rule as execute_automation_rule_func, process_time_based_triggers
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_

automation_bp = Blueprint('automation', __name__, url_prefix='/api/automation')

@automation_bp.route('/rules', methods=['GET'])
def get_rules():
    """Get all automation rules"""
    try:
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        rule_type = request.args.get('rule_type')
        
        query = AutomationRule.query
        
        if enabled_only:
            query = query.filter_by(enabled=True)
        if rule_type:
            query = query.filter_by(rule_type=rule_type)
        
        rules = query.order_by(AutomationRule.name).all()
        
        return jsonify({
            'rules': [r.to_dict() for r in rules]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting rules: {str(e)}")
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/rules', methods=['POST'])
def create_rule():
    """Create a new automation rule"""
    try:
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description')
        rule_type = data.get('rule_type')
        trigger_event = data.get('trigger_event')
        trigger_conditions = data.get('trigger_conditions', {})
        action_type = data.get('action_type', 'email')
        template_id = data.get('template_id')
        sms_template_id = data.get('sms_template_id')
        custom_message = data.get('custom_message')
        target_audience = data.get('target_audience', 'all')
        target_filters = data.get('target_filters', {})
        target_ids = data.get('target_ids', [])
        enabled = data.get('enabled', True)
        
        if not name or not rule_type or not trigger_event:
            return jsonify({'error': 'name, rule_type, and trigger_event are required'}), 400
        
        rule = AutomationRule(
            name=name,
            description=description,
            rule_type=rule_type,
            trigger_event=trigger_event,
            trigger_conditions=trigger_conditions,
            action_type=action_type,
            template_id=template_id,
            sms_template_id=sms_template_id,
            custom_message=custom_message,
            target_audience=target_audience,
            target_filters=target_filters,
            target_ids=target_ids,
            enabled=enabled
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return jsonify({'rule': rule.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/rules/<int:rule_id>', methods=['GET'])
def get_rule(rule_id):
    """Get a specific automation rule"""
    try:
        rule = AutomationRule.query.get_or_404(rule_id)
        return jsonify({'rule': rule.to_dict()}), 200
    except Exception as e:
        logger.error(f"Error getting rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/rules/<int:rule_id>', methods=['PUT'])
def update_rule(rule_id):
    """Update an automation rule"""
    try:
        rule = AutomationRule.query.get_or_404(rule_id)
        data = request.get_json()
        
        if 'name' in data:
            rule.name = data['name']
        if 'description' in data:
            rule.description = data['description']
        if 'rule_type' in data:
            rule.rule_type = data['rule_type']
        if 'trigger_event' in data:
            rule.trigger_event = data['trigger_event']
        if 'trigger_conditions' in data:
            rule.trigger_conditions = data['trigger_conditions']
        if 'action_type' in data:
            rule.action_type = data['action_type']
        if 'template_id' in data:
            rule.template_id = data['template_id']
        if 'sms_template_id' in data:
            rule.sms_template_id = data['sms_template_id']
        if 'custom_message' in data:
            rule.custom_message = data['custom_message']
        if 'target_audience' in data:
            rule.target_audience = data['target_audience']
        if 'target_filters' in data:
            rule.target_filters = data['target_filters']
        if 'target_ids' in data:
            rule.target_ids = data['target_ids']
        if 'enabled' in data:
            rule.enabled = data['enabled']
        
        db.session.commit()
        
        return jsonify({'rule': rule.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/rules/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """Delete an automation rule"""
    try:
        rule = AutomationRule.query.get_or_404(rule_id)
        db.session.delete(rule)
        db.session.commit()
        
        return jsonify({'message': 'Rule deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/rules/<int:rule_id>/toggle', methods=['POST'])
def toggle_rule(rule_id):
    """Enable or disable an automation rule"""
    try:
        rule = AutomationRule.query.get_or_404(rule_id)
        rule.enabled = not rule.enabled
        db.session.commit()
        
        return jsonify({
            'rule': rule.to_dict(),
            'message': f'Rule {"enabled" if rule.enabled else "disabled"}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error toggling rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/rules/<int:rule_id>/execute', methods=['POST'])
def execute_rule(rule_id):
    """Manually execute an automation rule"""
    try:
        rule = AutomationRule.query.get_or_404(rule_id)
        
        if not rule.enabled:
            return jsonify({'error': 'Rule is disabled'}), 400
        
        context = request.get_json() or {}
        result = execute_automation_rule_func(rule, context)
        
        return jsonify({
            'message': 'Rule executed',
            'result': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error executing rule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/logs', methods=['GET'])
def get_logs():
    """Get automation execution logs"""
    try:
        rule_id = request.args.get('rule_id', type=int)
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        per_page = min(per_page, 100)
        
        query = AutomationLog.query
        
        if rule_id:
            query = query.filter_by(rule_id=rule_id)
        if status:
            query = query.filter_by(status=status)
        if start_date:
            query = query.filter(AutomationLog.executed_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(AutomationLog.executed_at <= datetime.fromisoformat(end_date))
        
        logs = query.order_by(AutomationLog.executed_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': logs.total,
                'pages': logs.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Get automation analytics"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = AutomationLog.query
        
        if start_date:
            query = query.filter(AutomationLog.executed_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(AutomationLog.executed_at <= datetime.fromisoformat(end_date))
        
        # Total executions
        total_executions = query.count()
        
        # Success/failure breakdown
        success_count = query.filter_by(status='success').count()
        failure_count = query.filter_by(status='failed').count()
        
        # Total actions sent
        total_sent = db.session.query(func.sum(AutomationLog.sent_count)).scalar() or 0
        
        # Rule performance
        rule_stats = db.session.query(
            AutomationRule.name,
            func.count(AutomationLog.id).label('executions'),
            func.sum(AutomationLog.sent_count).label('sent')
        ).join(
            AutomationLog, AutomationRule.id == AutomationLog.rule_id
        ).group_by(
            AutomationRule.id, AutomationRule.name
        ).all()
        
        return jsonify({
            'total_executions': total_executions,
            'success_count': success_count,
            'failure_count': failure_count,
            'success_rate': round((success_count / total_executions * 100) if total_executions > 0 else 0, 2),
            'total_actions_sent': int(total_sent),
            'rule_performance': [
                {'rule_name': name, 'executions': execs, 'sent': int(sent)}
                for name, execs, sent in rule_stats
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/process-triggers', methods=['POST'])
def process_triggers():
    """
    Background worker endpoint to process time-based automation triggers
    This should be called periodically (e.g., via cron job or scheduled task)
    """
    try:
        # Optional: Add authentication/authorization check here
        # For example, check for an API key or admin token
        
        results = process_time_based_triggers()
        
        return jsonify({
            'message': 'Time-based triggers processed',
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing time-based triggers: {str(e)}")
        return jsonify({'error': str(e)}), 500

