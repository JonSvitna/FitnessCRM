"""
AI Agent Models
Tracks agent configurations, executions, and performance
"""
from datetime import datetime
from typing import Optional, Dict, Any
import json
from models import db


class Agent(db.Model):
    """AI Agent Configuration"""
    __tablename__ = 'ai_agents'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type = db.Column(db.String(50), nullable=False)  # workout_optimization, progress_monitoring, etc.
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='inactive')  # active, inactive, error
    config = db.Column(db.JSON, default={})
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    executions = db.relationship('AgentExecution', back_populates='agent', cascade='all, delete-orphan')
    metrics = db.relationship('AgentMetric', back_populates='agent', cascade='all, delete-orphan')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'status': self.status,
            'config': self.config,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class AgentExecution(db.Model):
    """Agent Execution Log"""
    __tablename__ = 'ai_agent_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('ai_agents.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # running, completed, failed
    input_data = db.Column(db.JSON)
    output_data = db.Column(db.JSON)
    error_message = db.Column(db.Text)
    execution_time = db.Column(db.Float)  # in seconds
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    agent = db.relationship('Agent', back_populates='executions')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'status': self.status,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'error_message': self.error_message,
            'execution_time': self.execution_time,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class AgentMetric(db.Model):
    """Agent Performance Metrics"""
    __tablename__ = 'ai_agent_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('ai_agents.id'), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)  # success_rate, avg_time, error_count
    metric_value = db.Column(db.Float, nullable=False)
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = db.relationship('Agent', back_populates='metrics')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'metric_type': self.metric_type,
            'metric_value': self.metric_value,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SystemHealth(db.Model):
    """System Health Monitoring"""
    __tablename__ = 'ai_system_health'
    
    id = db.Column(db.Integer, primary_key=True)
    component = db.Column(db.String(100), nullable=False)  # api, database, agents, etc.
    status = db.Column(db.String(20), nullable=False)  # healthy, warning, critical
    message = db.Column(db.Text)
    metrics = db.Column(db.JSON)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'component': self.component,
            'status': self.status,
            'message': self.message,
            'metrics': self.metrics,
            'checked_at': self.checked_at.isoformat() if self.checked_at else None
        }


class CodeSuggestion(db.Model):
    """Code Improvement Suggestions from AI"""
    __tablename__ = 'ai_code_suggestions'
    
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(500), nullable=False)
    issue_type = db.Column(db.String(50), nullable=False)  # bug, performance, security, style
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    description = db.Column(db.Text, nullable=False)
    suggestion = db.Column(db.Text, nullable=False)
    code_snippet = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, applied
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'file_path': self.file_path,
            'issue_type': self.issue_type,
            'severity': self.severity,
            'description': self.description,
            'suggestion': self.suggestion,
            'code_snippet': self.code_snippet,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }
