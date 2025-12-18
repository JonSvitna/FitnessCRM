"""
Audit log routes
Phase 7: Advanced Features - M7.4: Security & Compliance
"""

from flask import Blueprint, request, jsonify
from utils.audit_log import audit_log
from utils.auth import require_auth, require_role
from datetime import datetime
from utils.logger import logger

audit_bp = Blueprint('audit', __name__, url_prefix='/api/audit')

@audit_bp.route('/logs', methods=['GET'])
@require_auth
@require_role('admin')
def get_audit_logs():
    """Get audit logs (admin only)"""
    try:
        resource_type = request.args.get('resource_type')
        user_id = request.args.get('user_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        logs = audit_log.get_logs(
            resource_type=resource_type,
            user_id=user_id,
            start_date=start,
            end_date=end,
            limit=limit
        )
        
        return jsonify({
            'logs': logs,
            'total': len(logs)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

