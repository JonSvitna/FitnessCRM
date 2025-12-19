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

def log_activity(action, entity_type, entity_id=None, user_identifier=None, details=None, name=None, email=None, contact=None, role=None):
    """
    Log an activity to the database with only necessary information
    
    Args:
        action: The action performed (create, update, delete, view)
        entity_type: Type of entity (trainer, client, assignment, etc.)
        entity_id: ID of the entity (optional)
        user_identifier: Email or ID of user (optional, for backward compatibility)
        details: Additional details as dict (optional, will be filtered to only include name, email, contact, role)
        name: Name of the person (optional, extracted from details if not provided)
        email: Email address (optional, extracted from details or user_identifier)
        contact: Phone/contact information (optional, extracted from details)
        role: Trainer or Client (optional, extracted from details or entity_type)
    """
    try:
        # Extract necessary information from details if provided
        if details:
            if isinstance(details, dict):
                name = name or details.get('name')
                email = email or details.get('email')
                contact = contact or details.get('phone') or details.get('contact')
                role = role or details.get('role')
        
        # Determine role from entity_type if not provided
        if not role:
            if entity_type == 'trainer':
                role = 'Trainer'
            elif entity_type == 'client':
                role = 'Client'
            else:
                role = entity_type.capitalize()
        
        # Use user_identifier as email if email not provided
        if not email and user_identifier:
            email = user_identifier
        
        # Create simplified details with only necessary information
        simplified_details = {}
        if name:
            simplified_details['name'] = name
        if email:
            simplified_details['email'] = email
        if contact:
            simplified_details['contact'] = contact
        if role:
            simplified_details['role'] = role
        
        # Create activity log entry (store minimal information)
        activity = ActivityLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_identifier=email or user_identifier,  # Store email as user_identifier
            details=simplified_details if simplified_details else None,  # Only store necessary fields
            ip_address=None,  # Remove IP address
            user_agent=None   # Remove user agent
        )
        
        db.session.add(activity)
        db.session.commit()
        
        # Also log to system logger
        logger.info(f"Activity: {action} {entity_type} (ID: {entity_id}) - {name or 'Unknown'} ({email or 'No email'})")
        
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
