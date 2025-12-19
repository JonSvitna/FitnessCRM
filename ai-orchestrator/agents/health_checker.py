"""
Health Checker Agent
Monitors system health and identifies potential issues
"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from .base_agent import BaseAgent
from models import db
from models.agent import SystemHealth
from datetime import datetime
import os
import requests


class HealthCheckerAgent(BaseAgent):
    """Agent for system health monitoring"""
    
    def __init__(self, agent_id: int, name: str, config: Dict[str, Any] = None):
        super().__init__(agent_id, name, config)
        self.llm = ChatOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            model=self.get_config_value('model', 'gpt-4-turbo-preview'),
            temperature=self.get_config_value('temperature', 0.3)  # Lower temp for factual analysis
        )
        self.main_app_url = os.getenv('MAIN_APP_URL', 'http://localhost:5000')
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute health check
        
        Args:
            input_data: Optional filters and parameters
        
        Returns:
            System health status and recommendations
        """
        health_checks = []
        
        # Check database connectivity
        db_health = self._check_database()
        health_checks.append(db_health)
        
        # Check main app API
        api_health = self._check_main_api()
        health_checks.append(api_health)
        
        # Check agent system
        agent_health = self._check_agents()
        health_checks.append(agent_health)
        
        # Store health check results
        for check in health_checks:
            health_record = SystemHealth(
                component=check['component'],
                status=check['status'],
                message=check['message'],
                metrics=check.get('metrics', {}),
                checked_at=datetime.utcnow()
            )
            db.session.add(health_record)
        
        db.session.commit()
        
        # Use LLM to analyze health and provide recommendations
        system_prompt = """You are a system reliability engineer AI that analyzes health check data 
and provides actionable recommendations for maintaining system health."""
        
        user_prompt = f"""Analyze the following system health checks:

{health_checks}

Provide:
1. Overall system health assessment
2. Critical issues that need immediate attention
3. Warnings that should be monitored
4. Recommendations for improvement
5. Preventive measures

Format as JSON."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            'health_checks': health_checks,
            'analysis': response.content,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity and health"""
        try:
            # Simple query to check DB
            db.session.execute(db.text('SELECT 1'))
            return {
                'component': 'database',
                'status': 'healthy',
                'message': 'Database connection is healthy',
                'metrics': {
                    'responsive': True
                }
            }
        except Exception as e:
            return {
                'component': 'database',
                'status': 'critical',
                'message': f'Database connection failed: {str(e)}',
                'metrics': {
                    'responsive': False,
                    'error': str(e)
                }
            }
    
    def _check_main_api(self) -> Dict[str, Any]:
        """Check main application API health"""
        try:
            response = requests.get(f"{self.main_app_url}/api/health", timeout=5)
            if response.status_code == 200:
                return {
                    'component': 'main_api',
                    'status': 'healthy',
                    'message': 'Main API is responsive',
                    'metrics': {
                        'responsive': True,
                        'response_time': response.elapsed.total_seconds()
                    }
                }
            else:
                return {
                    'component': 'main_api',
                    'status': 'warning',
                    'message': f'Main API returned status {response.status_code}',
                    'metrics': {
                        'responsive': True,
                        'status_code': response.status_code
                    }
                }
        except Exception as e:
            return {
                'component': 'main_api',
                'status': 'critical',
                'message': f'Main API check failed: {str(e)}',
                'metrics': {
                    'responsive': False,
                    'error': str(e)
                }
            }
    
    def _check_agents(self) -> Dict[str, Any]:
        """Check AI agent system health"""
        try:
            from models.agent import Agent, AgentExecution
            
            # Count active agents
            active_agents = Agent.query.filter_by(enabled=True).count()
            
            # Check recent executions
            recent_executions = AgentExecution.query.order_by(
                AgentExecution.started_at.desc()
            ).limit(10).all()
            
            failed_recent = sum(1 for ex in recent_executions if ex.status == 'failed')
            
            status = 'healthy'
            if active_agents == 0:
                status = 'warning'
            elif failed_recent > 5:
                status = 'warning'
            
            return {
                'component': 'agents',
                'status': status,
                'message': f'{active_agents} active agents, {failed_recent}/10 recent failures',
                'metrics': {
                    'active_agents': active_agents,
                    'recent_failures': failed_recent,
                    'total_recent_executions': len(recent_executions)
                }
            }
        except Exception as e:
            return {
                'component': 'agents',
                'status': 'warning',
                'message': f'Agent health check failed: {str(e)}',
                'metrics': {
                    'error': str(e)
                }
            }
