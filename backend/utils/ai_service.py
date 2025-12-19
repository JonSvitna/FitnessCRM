"""
AI Service Abstraction Layer
Phase 7: Advanced Features - M7.1: AI-Powered Features

This module provides an abstraction layer for AI features.
Can use either seed data or the AI Orchestrator service.

To integrate with AI Orchestrator:
1. Set AI_ORCHESTRATOR_URL environment variable
2. Set AI_ORCHESTRATOR_KEY environment variable
The service will automatically use the orchestrator when configured.

Fallback to seed data if orchestrator is not configured or fails.
"""

import os
import random
import requests
from typing import List, Dict, Any, Optional
from utils.logger import logger

# Seed data for AI recommendations
WORKOUT_RECOMMENDATIONS_SEED = [
    {
        "exercise": "Squats",
        "sets": 3,
        "reps": 12,
        "reason": "Great for building lower body strength and improving balance",
        "difficulty": "intermediate"
    },
    {
        "exercise": "Push-ups",
        "sets": 3,
        "reps": 15,
        "reason": "Excellent upper body workout, no equipment needed",
        "difficulty": "beginner"
    },
    {
        "exercise": "Deadlifts",
        "sets": 3,
        "reps": 8,
        "reason": "Compound movement targeting multiple muscle groups",
        "difficulty": "advanced"
    },
    {
        "exercise": "Plank",
        "sets": 3,
        "reps": "60 seconds",
        "reason": "Core strengthening exercise",
        "difficulty": "beginner"
    },
    {
        "exercise": "Pull-ups",
        "sets": 3,
        "reps": 10,
        "reason": "Builds back and arm strength",
        "difficulty": "intermediate"
    }
]

PROGRESS_PREDICTIONS_SEED = [
    "Based on current progress, client is on track to reach goal in 8-10 weeks",
    "Progress is slightly ahead of schedule. Consider increasing difficulty",
    "Client may need additional support. Progress is slower than expected",
    "Excellent progress! Client is exceeding expectations",
    "Steady progress observed. Continue current program"
]

SCHEDULING_SUGGESTIONS_SEED = [
    "Best time: Morning sessions show 20% better attendance",
    "Consider spacing sessions 48-72 hours apart for recovery",
    "Client prefers afternoon sessions based on history",
    "Avoid scheduling on Mondays - lowest attendance day",
    "Weekend sessions have highest completion rate for this client"
]

def _call_ai_service(endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Call AI Orchestrator service (when configured)
    
    Args:
        endpoint: Task type (e.g., 'workout_optimization', 'progress_monitoring')
        data: Input data for AI service
    
    Returns:
        AI service response or None if not configured/failed
    """
    orchestrator_url = os.getenv('AI_ORCHESTRATOR_URL')
    orchestrator_key = os.getenv('AI_ORCHESTRATOR_KEY')
    
    if not orchestrator_url:
        # AI orchestrator not configured, return None to use seed data
        logger.debug(f"AI orchestrator not configured, using seed data for {endpoint}")
        return None
    
    try:
        # Call AI Orchestrator
        headers = {"Content-Type": "application/json"}
        if orchestrator_key:
            headers["Authorization"] = f"Bearer {orchestrator_key}"
        
        response = requests.post(
            f"{orchestrator_url}/api/execute",
            json={
                "task_type": endpoint,
                "input_data": data
            },
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result.get('results', result.get('output', {}))
            else:
                logger.warning(f"AI orchestrator returned error: {result.get('error')}")
                return None
        else:
            logger.warning(f"AI orchestrator returned status {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        logger.warning(f"AI orchestrator request timeout for {endpoint}")
        return None
    except requests.exceptions.RequestException as e:
        logger.warning(f"AI orchestrator request failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error calling AI orchestrator: {str(e)}", exc_info=True)
        return None

def get_workout_recommendations(client_id: int, goals: List[str] = None, 
                                fitness_level: str = "intermediate") -> List[Dict[str, Any]]:
    """
    Get AI-powered workout recommendations
    
    Args:
        client_id: Client ID
        goals: List of client goals
        fitness_level: Client fitness level (beginner/intermediate/advanced)
    
    Returns:
        List of workout recommendations
    """
    # Try to call AI orchestrator
    ai_data = {
        "client_id": client_id,
        "goals": goals or [],
        "fitness_level": fitness_level
    }
    
    ai_response = _call_ai_service('workout_optimization', ai_data)
    
    if ai_response:
        # Extract recommendations from orchestrator response
        if 'workout_optimization' in ai_response:
            return ai_response.get('workout_optimization', [])
        return ai_response.get('recommendations', [])
    
    # Fallback to seed data
    logger.info(f"Using seed data for workout recommendations (client {client_id})")
    
    # Filter seed data by fitness level
    filtered_recommendations = [
        rec for rec in WORKOUT_RECOMMENDATIONS_SEED 
        if rec['difficulty'] == fitness_level or fitness_level == 'intermediate'
    ]
    
    # Return 3-5 random recommendations
    return random.sample(
        filtered_recommendations, 
        min(len(filtered_recommendations), random.randint(3, 5))
    )

def predict_client_progress(client_id: int, current_metrics: Dict[str, float],
                           goal_metrics: Dict[str, float]) -> Dict[str, Any]:
    """
    Predict client progress based on current metrics
    
    Args:
        client_id: Client ID
        current_metrics: Current client metrics (weight, body_fat, etc.)
        goal_metrics: Target metrics
    
    Returns:
        Progress prediction with timeline and confidence
    """
    # Try to call AI orchestrator
    ai_data = {
        "client_id": client_id,
        "current_metrics": current_metrics,
        "goal_metrics": goal_metrics
    }
    
    ai_response = _call_ai_service('progress_monitoring', ai_data)
    
    if ai_response:
        # Extract progress analysis from orchestrator response
        if 'progress_analysis' in ai_response:
            return ai_response
        return ai_response
    
    # Fallback to seed data
    logger.info(f"Using seed data for progress prediction (client {client_id})")
    
    prediction = random.choice(PROGRESS_PREDICTIONS_SEED)
    
    # Calculate estimated weeks to goal (mock calculation)
    weeks_estimate = random.randint(6, 12)
    confidence = random.uniform(0.75, 0.95)
    
    return {
        "prediction": prediction,
        "estimated_weeks": weeks_estimate,
        "confidence": round(confidence, 2),
        "source": "seed_data"
    }

def suggest_session_times(client_id: int, trainer_id: int,
                         preferred_times: List[str] = None) -> List[Dict[str, Any]]:
    """
    Get AI-powered session scheduling suggestions
    
    Args:
        client_id: Client ID
        trainer_id: Trainer ID
        preferred_times: List of preferred time slots
    
    Returns:
        List of scheduling suggestions
    """
    # Try to call AI orchestrator
    ai_data = {
        "client_id": client_id,
        "trainer_id": trainer_id,
        "preferred_times": preferred_times or []
    }
    
    ai_response = _call_ai_service('scheduling', ai_data)
    
    if ai_response:
        # Extract scheduling suggestions from orchestrator response
        if 'scheduling' in ai_response:
            return ai_response.get('scheduling', [])
        return ai_response.get('suggestions', [])
    
    # Fallback to seed data
    logger.info(f"Using seed data for scheduling suggestions (client {client_id})")
    
    suggestions = random.sample(SCHEDULING_SUGGESTIONS_SEED, 3)
    
    return [
        {"suggestion": s, "priority": i + 1, "source": "seed_data"}
        for i, s in enumerate(suggestions)
    ]

def generate_workout_plan(client_id: int, duration_weeks: int = 4,
                         focus_areas: List[str] = None) -> Dict[str, Any]:
    """
    Generate automated workout plan
    
    Args:
        client_id: Client ID
        duration_weeks: Plan duration in weeks
        focus_areas: Areas to focus on (strength, cardio, flexibility, etc.)
    
    Returns:
        Generated workout plan
    """
    # Try to call external AI service
    ai_data = {
        "client_id": client_id,
        "duration_weeks": duration_weeks,
        "focus_areas": focus_areas or []
    }
    
    ai_response = _call_ai_service('workout_plan', ai_data)
    
    if ai_response:
        return ai_response
    
    # Fallback to seed data
    logger.info(f"Using seed data for workout plan generation (client {client_id})")
    
    # Generate mock workout plan
    plan = {
        "client_id": client_id,
        "duration_weeks": duration_weeks,
        "focus_areas": focus_areas or ["strength", "cardio"],
        "weeks": []
    }
    
    for week in range(1, duration_weeks + 1):
        week_plan = {
            "week": week,
            "workouts": []
        }
        
        # 3-4 workouts per week
        num_workouts = random.randint(3, 4)
        for day in range(1, num_workouts + 1):
            workout = {
                "day": day,
                "exercises": random.sample(
                    WORKOUT_RECOMMENDATIONS_SEED,
                    random.randint(4, 6)
                )
            }
            week_plan["workouts"].append(workout)
        
        plan["weeks"].append(week_plan)
    
    plan["source"] = "seed_data"
    return plan

def is_ai_configured() -> bool:
    """Check if AI orchestrator service is configured"""
    return bool(os.getenv('AI_ORCHESTRATOR_URL'))

