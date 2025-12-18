"""
Audit logging system
Phase 7: Advanced Features - M7.4: Security & Compliance
"""

from models.database import db
from datetime import datetime
from utils.logger import logger
from flask import g, request

class AuditLog:
    """Audit log model (in-memory for now, can be moved to database)"""
    def __init__(self):
        self.logs = []
    
    def log(self, action: str, resource_type: str, resource_id: int = None,
            user_id: int = None, details: dict = None, ip_address: str = None):
        """Log an audit event"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,  # create, update, delete, view, login, logout
            'resource_type': resource_type,  # client, trainer, payment, etc.
            'resource_id': resource_id,
            'user_id': user_id or (getattr(g, 'current_user_id', None) if 'g' in globals() else None),
            'ip_address': ip_address or (request.remote_addr if 'request' in globals() else None),
            'details': details or {}
        }
        
        self.logs.append(log_entry)
        logger.info(f"Audit: {action} {resource_type} {resource_id} by user {user_id}")
        
        # In production, save to database
        # For now, keep in memory (last 1000 entries)
        if len(self.logs) > 1000:
            self.logs.pop(0)
    
    def get_logs(self, resource_type: str = None, user_id: int = None, 
                 start_date: datetime = None, end_date: datetime = None, limit: int = 100):
        """Get audit logs with filters"""
        filtered_logs = self.logs
        
        if resource_type:
            filtered_logs = [log for log in filtered_logs if log['resource_type'] == resource_type]
        
        if user_id:
            filtered_logs = [log for log in filtered_logs if log['user_id'] == user_id]
        
        if start_date:
            filtered_logs = [
                log for log in filtered_logs 
                if datetime.fromisoformat(log['timestamp']) >= start_date
            ]
        
        if end_date:
            filtered_logs = [
                log for log in filtered_logs 
                if datetime.fromisoformat(log['timestamp']) <= end_date
            ]
        
        # Sort by timestamp (newest first) and limit
        filtered_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return filtered_logs[:limit]

# Global audit log instance
audit_log = AuditLog()

def log_audit_event(action: str, resource_type: str, resource_id: int = None,
                   details: dict = None):
    """Helper function to log audit events"""
    audit_log.log(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details
    )

