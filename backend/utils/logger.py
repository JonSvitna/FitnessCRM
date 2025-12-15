"""
Logging utilities for FitnessCRM
Provides activity logging and system logging
"""

import logging
import os
from flask import request
from models.database import db, ActivityLog
from datetime import datetime

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure system logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('FitnessCRM')

def log_activity(action, entity_type, entity_id=None, user_identifier=None, details=None):
    """
    Log an activity to the database
    
    Args:
        action: The action performed (create, update, delete, view)
        entity_type: Type of entity (trainer, client, assignment, etc.)
        entity_id: ID of the entity (optional)
        user_identifier: Email or ID of user (optional)
        details: Additional details as dict (optional)
    """
    try:
        # Get request context if available
        ip_address = None
        user_agent = None
        
        try:
            if request:
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent', '')[:500]
        except RuntimeError:
            # No request context available
            pass
        
        # Create activity log entry
        activity = ActivityLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_identifier=user_identifier,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(activity)
        db.session.commit()
        
        # Also log to system logger
        logger.info(f"Activity: {action} {entity_type} (ID: {entity_id}) by {user_identifier}")
        
    except Exception as e:
        logger.error(f"Failed to log activity: {str(e)}")
        # Don't raise exception - logging failure shouldn't break the app
        try:
            db.session.rollback()
        except:
            pass

def get_activity_logs(entity_type=None, entity_id=None, limit=100):
    """
    Retrieve activity logs
    
    Args:
        entity_type: Filter by entity type (optional)
        entity_id: Filter by entity ID (optional)
        limit: Maximum number of logs to retrieve
    
    Returns:
        List of activity log dictionaries
    """
    try:
        query = ActivityLog.query
        
        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        if entity_id is not None:
            query = query.filter_by(entity_id=entity_id)
        
        logs = query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
        return [log.to_dict() for log in logs]
        
    except Exception as e:
        logger.error(f"Failed to retrieve activity logs: {str(e)}")
        return []

def get_recent_activity(limit=50):
    """Get recent activity across all entities"""
    return get_activity_logs(limit=limit)

class LoggerMiddleware:
    """Middleware to log all requests"""
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # Log request
        method = environ.get('REQUEST_METHOD')
        path = environ.get('PATH_INFO')
        
        logger.info(f"Request: {method} {path}")
        
        return self.app(environ, start_response)
