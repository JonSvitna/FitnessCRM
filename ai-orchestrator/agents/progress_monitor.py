"""
Progress Monitor Agent
Tracks and analyzes client progress, providing insights and predictions
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from .base_agent import BaseAgent
import os


class ProgressMonitorAgent(BaseAgent):
    """Agent for monitoring client progress"""
    
    def __init__(self, agent_id: int, name: str, config: Dict[str, Any] = None):
        super().__init__(agent_id, name, config)
        self.llm = ChatOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            model=self.get_config_value('model', 'gpt-4-turbo-preview'),
            temperature=self.get_config_value('temperature', 0.7)
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute progress monitoring
        
        Args:
            input_data: Must contain client_id and optionally:
                - current_metrics: Dict of current measurements
                - historical_data: List of past measurements
                - goals: Target metrics
                - time_period: Analysis time period
        
        Returns:
            Progress analysis and predictions
        """
        # Validate input
        if not self.validate_input(input_data, ['client_id']):
            raise ValueError("client_id is required")
        
        client_id = input_data['client_id']
        current_metrics = input_data.get('current_metrics', {})
        historical_data = input_data.get('historical_data', [])
        goals = input_data.get('goals', {})
        time_period = input_data.get('time_period', '30 days')
        
        # Create prompt for LLM
        system_prompt = """You are an expert fitness data analyst AI specializing in progress tracking and prediction.
Your role is to analyze client fitness data, identify trends, and provide actionable insights."""
        
        user_prompt = f"""Analyze the progress for a client over the past {time_period}:

Current Metrics: {current_metrics}
Historical Data: {historical_data}
Target Goals: {goals}

Please provide:
1. Progress summary (what's improved, what's stagnated)
2. Trend analysis (positive/negative patterns)
3. Predictions (estimated time to reach goals)
4. Recommendations (adjustments to training or nutrition)
5. Motivational insights (celebrate wins, address challenges)

Format the response as a structured JSON object."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Get LLM response
        response = self.llm.invoke(messages)
        
        return {
            'client_id': client_id,
            'progress_analysis': response.content,
            'analysis_period': time_period,
            'metrics_analyzed': list(current_metrics.keys())
        }
