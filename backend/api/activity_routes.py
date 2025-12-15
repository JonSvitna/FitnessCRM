"""
Activity logging API routes
"""

from flask import Blueprint, request, jsonify
from utils.logger import get_activity_logs, get_recent_activity, logger

activity_bp = Blueprint('activity', __name__, url_prefix='/api/activity')

@activity_bp.route('', methods=['GET'])
def list_activities():
    """Get activity logs with optional filtering"""
    try:
        entity_type = request.args.get('entity_type')
        entity_id = request.args.get('entity_id', type=int)
        limit = request.args.get('limit', 100, type=int)
        
        # Limit maximum results
        limit = min(limit, 1000)
        
        logs = get_activity_logs(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit
        )
        
        return jsonify({
            'count': len(logs),
            'activities': logs
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving activity logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@activity_bp.route('/recent', methods=['GET'])
def recent_activities():
    """Get recent activity across all entities"""
    try:
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 500)
        
        logs = get_recent_activity(limit=limit)
        
        return jsonify({
            'count': len(logs),
            'activities': logs
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving recent activities: {str(e)}")
        return jsonify({'error': str(e)}), 500

@activity_bp.route('/stats', methods=['GET'])
def activity_stats():
    """Get activity statistics"""
    try:
        from models.database import ActivityLog, db
        from sqlalchemy import func
        
        # Get counts by action
        action_stats = db.session.query(
            ActivityLog.action,
            func.count(ActivityLog.id).label('count')
        ).group_by(ActivityLog.action).all()
        
        # Get counts by entity type
        entity_stats = db.session.query(
            ActivityLog.entity_type,
            func.count(ActivityLog.id).label('count')
        ).group_by(ActivityLog.entity_type).all()
        
        # Total activities
        total = ActivityLog.query.count()
        
        return jsonify({
            'total_activities': total,
            'by_action': [{'action': a, 'count': c} for a, c in action_stats],
            'by_entity_type': [{'entity_type': e, 'count': c} for e, c in entity_stats]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting activity stats: {str(e)}")
        return jsonify({'error': str(e)}), 500
