"""
SMS API routes for Phase 5: Communication
Handles SMS sending, templates, scheduling, and analytics
"""

from flask import Blueprint, request, jsonify
from models.database import db, SMSLog, SMSTemplate, SMSSchedule, Client, Trainer, Session, Settings
from utils.sms import send_sms, format_phone_number
from utils.logger import logger
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_

sms_bp = Blueprint('sms', __name__, url_prefix='/api/sms')

@sms_bp.route('/send', methods=['POST'])
def send_sms_message():
    """Send an SMS message"""
    try:
        data = request.get_json()
        
        to_number = data.get('to_number')
        message = data.get('message')
        from_number = data.get('from_number')
        client_id = data.get('client_id')
        trainer_id = data.get('trainer_id')
        session_id = data.get('session_id')
        template_id = data.get('template_id')
        
        if not to_number or not message:
            return jsonify({'error': 'to_number and message are required'}), 400
        
        # Format phone number
        to_number = format_phone_number(to_number)
        
        # Get settings for from_number
        settings = Settings.query.first()
        from_number = from_number or (settings.twilio_phone_number if settings else None)
        
        # Send SMS
        result = send_sms(to_number, message, from_number)
        
        if not result.get('success'):
            return jsonify({'error': result.get('error', 'Failed to send SMS')}), 400
        
        # Log SMS
        sms_log = SMSLog(
            to_number=to_number,
            from_number=from_number or settings.twilio_phone_number if settings else None,
            message=message,
            message_sid=result.get('message_sid'),
            client_id=client_id,
            trainer_id=trainer_id,
            session_id=session_id,
            template_id=template_id,
            status='sent',
            twilio_status=result.get('status')
        )
        db.session.add(sms_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message_sid': result.get('message_sid'),
            'log_id': sms_log.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error sending SMS: {str(e)}")
        return jsonify({'error': str(e)}), 500

@sms_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get all SMS templates"""
    try:
        category = request.args.get('category')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = SMSTemplate.query
        
        if category:
            query = query.filter_by(category=category)
        
        if active_only:
            query = query.filter_by(active=True)
        
        templates = query.order_by(SMSTemplate.name).all()
        
        return jsonify({
            'templates': [t.to_dict() for t in templates]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        return jsonify({'error': str(e)}), 500

@sms_bp.route('/templates', methods=['POST'])
def create_template():
    """Create a new SMS template"""
    try:
        data = request.get_json()
        
        name = data.get('name')
        category = data.get('category', 'custom')
        message = data.get('message')
        variables = data.get('variables', [])
        
        if not name or not message:
            return jsonify({'error': 'name and message are required'}), 400
        
        template = SMSTemplate(
            name=name,
            category=category,
            message=message,
            variables=','.join(variables) if isinstance(variables, list) else variables,
            active=True
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({'template': template.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating template: {str(e)}")
        return jsonify({'error': str(e)}), 500

@sms_bp.route('/templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """Update an SMS template"""
    try:
        template = SMSTemplate.query.get_or_404(template_id)
        data = request.get_json()
        
        if 'name' in data:
            template.name = data['name']
        if 'category' in data:
            template.category = data['category']
        if 'message' in data:
            template.message = data['message']
        if 'variables' in data:
            variables = data['variables']
            template.variables = ','.join(variables) if isinstance(variables, list) else variables
        if 'active' in data:
            template.active = data['active']
        
        db.session.commit()
        
        return jsonify({'template': template.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating template: {str(e)}")
        return jsonify({'error': str(e)}), 500

@sms_bp.route('/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete an SMS template"""
    try:
        template = SMSTemplate.query.get_or_404(template_id)
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({'message': 'Template deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting template: {str(e)}")
        return jsonify({'error': str(e)}), 500

@sms_bp.route('/templates/<int:template_id>/send', methods=['POST'])
def send_template(template_id):
    """Send SMS using a template"""
    try:
        template = SMSTemplate.query.get_or_404(template_id)
        data = request.get_json()
        
        to_number = data.get('to_number')
        variables = data.get('variables', {})  # Template variable values
        client_id = data.get('client_id')
        trainer_id = data.get('trainer_id')
        session_id = data.get('session_id')
        
        if not to_number:
            return jsonify({'error': 'to_number is required'}), 400
        
        # Replace template variables
        message = template.message
        for key, value in variables.items():
            message = message.replace(f'{{{key}}}', str(value))
        
        # Format phone number
        to_number = format_phone_number(to_number)
        
        # Send SMS
        result = send_sms(to_number, message)
        
        if not result.get('success'):
            return jsonify({'error': result.get('error', 'Failed to send SMS')}), 400
        
        # Log SMS
        sms_log = SMSLog(
            to_number=to_number,
            message=message,
            message_sid=result.get('message_sid'),
            client_id=client_id,
            trainer_id=trainer_id,
            session_id=session_id,
            template_id=template_id,
            status='sent',
            twilio_status=result.get('status')
        )
        db.session.add(sms_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message_sid': result.get('message_sid'),
            'log_id': sms_log.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error sending template SMS: {str(e)}")
        return jsonify({'error': str(e)}), 500

@sms_bp.route('/logs', methods=['GET'])
def get_sms_logs():
    """Get SMS logs with filtering"""
    try:
        client_id = request.args.get('client_id', type=int)
        trainer_id = request.args.get('trainer_id', type=int)
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        per_page = min(per_page, 100)
        
        query = SMSLog.query
        
        if client_id:
            query = query.filter_by(client_id=client_id)
        if trainer_id:
            query = query.filter_by(trainer_id=trainer_id)
        if status:
            query = query.filter_by(status=status)
        if start_date:
            query = query.filter(SMSLog.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(SMSLog.created_at <= datetime.fromisoformat(end_date))
        
        logs = query.order_by(SMSLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': logs.total,
                'pages': logs.pages,
                'has_next': logs.has_next,
                'has_prev': logs.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting SMS logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@sms_bp.route('/schedules', methods=['GET'])
def get_schedules():
    """Get scheduled SMS messages"""
    try:
        status = request.args.get('status')
        client_id = request.args.get('client_id', type=int)
        
        query = SMSSchedule.query
        
        if status:
            query = query.filter_by(status=status)
        if client_id:
            query = query.filter_by(client_id=client_id)
        
        schedules = query.order_by(SMSSchedule.scheduled_time).all()
        
        return jsonify({
            'schedules': [s.to_dict() for s in schedules]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting schedules: {str(e)}")
        return jsonify({'error': str(e)}), 500

@sms_bp.route('/schedules', methods=['POST'])
def create_schedule():
    """Create a scheduled SMS"""
    try:
        data = request.get_json()
        
        name = data.get('name')
        template_id = data.get('template_id')
        message = data.get('message')
        to_number = data.get('to_number')
        client_id = data.get('client_id')
        trainer_id = data.get('trainer_id')
        schedule_type = data.get('schedule_type', 'once')
        scheduled_time = data.get('scheduled_time')
        template_variables = data.get('template_variables', {})
        
        if not to_number or not scheduled_time:
            return jsonify({'error': 'to_number and scheduled_time are required'}), 400
        
        if not template_id and not message:
            return jsonify({'error': 'template_id or message is required'}), 400
        
        # Format phone number
        to_number = format_phone_number(to_number)
        
        # Parse scheduled_time
        if isinstance(scheduled_time, str):
            scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        
        schedule = SMSSchedule(
            name=name,
            template_id=template_id,
            message=message,
            to_number=to_number,
            client_id=client_id,
            trainer_id=trainer_id,
            schedule_type=schedule_type,
            scheduled_time=scheduled_time,
            template_variables=template_variables,
            next_send_at=scheduled_time,
            status='scheduled'
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({'schedule': schedule.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating schedule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@sms_bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
def cancel_schedule(schedule_id):
    """Cancel a scheduled SMS"""
    try:
        schedule = SMSSchedule.query.get_or_404(schedule_id)
        schedule.status = 'cancelled'
        db.session.commit()
        
        return jsonify({'message': 'Schedule cancelled successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cancelling schedule: {str(e)}")
        return jsonify({'error': str(e)}), 500

@sms_bp.route('/analytics', methods=['GET'])
def get_sms_analytics():
    """Get SMS analytics"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = SMSLog.query
        
        if start_date:
            query = query.filter(SMSLog.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(SMSLog.created_at <= datetime.fromisoformat(end_date))
        
        # Total SMS sent
        total_sent = query.count()
        
        # Status breakdown
        status_counts = db.session.query(
            SMSLog.status,
            func.count(SMSLog.id).label('count')
        ).group_by(SMSLog.status).all()
        
        # Cost analysis
        total_cost = db.session.query(func.sum(SMSLog.price)).scalar() or 0
        
        # Daily breakdown (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_stats = db.session.query(
            func.date(SMSLog.created_at).label('date'),
            func.count(SMSLog.id).label('count')
        ).filter(
            SMSLog.created_at >= thirty_days_ago
        ).group_by(
            func.date(SMSLog.created_at)
        ).order_by(
            func.date(SMSLog.created_at).desc()
        ).all()
        
        return jsonify({
            'total_sent': total_sent,
            'status_breakdown': {status: count for status, count in status_counts},
            'total_cost': float(total_cost),
            'daily_stats': [
                {'date': str(date), 'count': count}
                for date, count in daily_stats
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting SMS analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500

