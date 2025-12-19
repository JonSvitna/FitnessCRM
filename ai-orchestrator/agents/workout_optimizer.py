"""
Workout Optimizer Agent
Analyzes client data and generates personalized workout recommendations
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from .base_agent import BaseAgent
import os


class WorkoutOptimizerAgent(BaseAgent):
    """Agent for optimizing workout plans"""
    
    def __init__(self, agent_id: int, name: str, config: Dict[str, Any] = None):
        super().__init__(agent_id, name, config)
        self.llm = ChatOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            model=self.get_config_value('model', 'gpt-4-turbo-preview'),
            temperature=self.get_config_value('temperature', 0.7)
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute workout optimization
        
        Args:
            input_data: Must contain client_id and optionally:
                - goals: List of fitness goals
                - fitness_level: beginner/intermediate/advanced
                - available_equipment: List of available equipment
                - time_per_session: Minutes per workout
                - sessions_per_week: Number of workouts per week
        
        Returns:
            Optimized workout recommendations
        """
        # Validate input
        if not self.validate_input(input_data, ['client_id']):
            raise ValueError("client_id is required")
        
        client_id = input_data['client_id']
        goals = input_data.get('goals', ['general fitness'])
        fitness_level = input_data.get('fitness_level', 'intermediate')
        equipment = input_data.get('available_equipment', ['bodyweight'])
        time_per_session = input_data.get('time_per_session', 45)
        sessions_per_week = input_data.get('sessions_per_week', 3)
        
        # Create prompt for LLM
        system_prompt = """You are an expert fitness trainer AI specializing in personalized workout optimization.
Your role is to create effective, safe, and engaging workout plans tailored to individual clients.
Consider their fitness level, goals, available equipment, and time constraints."""
        
        user_prompt = f"""Create an optimized workout plan for a client with the following profile:

- Fitness Level: {fitness_level}
- Goals: {', '.join(goals)}
- Available Equipment: {', '.join(equipment)}
- Time per Session: {time_per_session} minutes
- Sessions per Week: {sessions_per_week}

Please provide:
1. A detailed workout structure for each session
2. Specific exercises with sets, reps, and rest periods
3. Progressive overload recommendations
4. Warm-up and cool-down routines
5. Safety considerations and form tips

Format the response as a structured JSON object."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Get LLM response
        response = self.llm.invoke(messages)
        
        return {
            'client_id': client_id,
            'workout_plan': response.content,
            'parameters': {
                'fitness_level': fitness_level,
                'goals': goals,
                'equipment': equipment,
                'time_per_session': time_per_session,
                'sessions_per_week': sessions_per_week
            }
        }
