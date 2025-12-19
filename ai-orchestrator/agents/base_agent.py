"""
Base Agent Class
All AI agents inherit from this base class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import time
from utils.logger import logger
from models import db
from models.agent import AgentExecution


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, agent_id: int, name: str, config: Dict[str, Any] = None):
        """
        Initialize base agent
        
        Args:
            agent_id: Database ID of the agent
            name: Agent name
            config: Agent configuration dictionary
        """
        self.agent_id = agent_id
        self.name = name
        self.config = config or {}
        self.logger = logger
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent logic
        Must be implemented by subclasses
        
        Args:
            input_data: Input data for the agent
        
        Returns:
            Output data from agent execution
        """
        pass
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run agent with execution tracking
        
        Args:
            input_data: Input data for the agent
        
        Returns:
            Execution result with metadata
        """
        # Create execution record
        execution = AgentExecution(
            agent_id=self.agent_id,
            status='running',
            input_data=input_data,
            started_at=datetime.utcnow()
        )
        db.session.add(execution)
        db.session.commit()
        
        start_time = time.time()
        
        try:
            self.logger.info(f"Agent {self.name} starting execution {execution.id}")
            
            # Execute agent logic
            output_data = await self.execute(input_data)
            
            # Update execution record
            execution.status = 'completed'
            execution.output_data = output_data
            execution.execution_time = time.time() - start_time
            execution.completed_at = datetime.utcnow()
            db.session.commit()
            
            self.logger.info(f"Agent {self.name} completed execution {execution.id} in {execution.execution_time:.2f}s")
            
            return {
                'success': True,
                'execution_id': execution.id,
                'output': output_data,
                'execution_time': execution.execution_time
            }
            
        except Exception as e:
            # Update execution record with error
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.execution_time = time.time() - start_time
            execution.completed_at = datetime.utcnow()
            db.session.commit()
            
            self.logger.error(f"Agent {self.name} failed execution {execution.id}: {str(e)}", exc_info=True)
            
            return {
                'success': False,
                'execution_id': execution.id,
                'error': str(e),
                'execution_time': execution.execution_time
            }
    
    def validate_input(self, input_data: Dict[str, Any], required_fields: list) -> bool:
        """
        Validate input data has required fields
        
        Args:
            input_data: Input data to validate
            required_fields: List of required field names
        
        Returns:
            True if valid, False otherwise
        """
        for field in required_fields:
            if field not in input_data:
                self.logger.warning(f"Missing required field: {field}")
                return False
        return True
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
