# Phase 7: AI Configuration Guide

## Overview

Phase 7 M7.1 implements AI-powered features using an abstraction layer that currently uses seed data. The system is designed to easily swap seed data with an external AI service when configured.

## Current Implementation

**Status**: Using seed/mock data  
**AI Service**: Not configured (using seed data)

## Features Implemented (with seed data)

1. **Workout Recommendations** - `/api/ai/workout-recommendations`
2. **Progress Predictions** - `/api/ai/progress-prediction`
3. **Scheduling Suggestions** - `/api/ai/scheduling-suggestions`
4. **Workout Plan Generation** - `/api/ai/generate-workout-plan`

## Configuration for External AI Service

To use an external AI service (OpenAI, Anthropic, custom ML service, etc.):

### 1. Set Environment Variables

```bash
# Required
AI_SERVICE_URL=https://your-ai-service.com/api
AI_API_KEY=your-api-key-here

# Optional (for specific providers)
AI_MODEL=gpt-4
AI_TEMPERATURE=0.7
```

### 2. Update AI Service Implementation

Edit `backend/utils/ai_service.py` and update the `_call_ai_service()` function:

```python
def _call_ai_service(endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ai_service_url = os.getenv('AI_SERVICE_URL')
    ai_api_key = os.getenv('AI_API_KEY')
    
    if not ai_service_url or not ai_api_key:
        return None
    
    import requests
    
    try:
        response = requests.post(
            f"{ai_service_url}/{endpoint}",
            json=data,
            headers={
                "Authorization": f"Bearer {ai_api_key}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"AI service call failed: {str(e)}")
        return None  # Fallback to seed data
```

### 3. Expected AI Service API Format

The AI service should accept POST requests with the following structure:

#### Workout Recommendations
```
POST /recommendations
{
  "client_id": 1,
  "goals": ["weight_loss", "strength"],
  "fitness_level": "intermediate"
}

Response:
{
  "recommendations": [
    {
      "exercise": "Squats",
      "sets": 3,
      "reps": 12,
      "reason": "...",
      "difficulty": "intermediate"
    }
  ]
}
```

#### Progress Predictions
```
POST /predictions
{
  "client_id": 1,
  "current_metrics": {"weight": 180, "body_fat": 20},
  "goal_metrics": {"weight": 170, "body_fat": 15}
}

Response:
{
  "prediction": "Based on current progress...",
  "estimated_weeks": 8,
  "confidence": 0.85
}
```

#### Scheduling Suggestions
```
POST /scheduling
{
  "client_id": 1,
  "trainer_id": 1,
  "preferred_times": ["morning", "afternoon"]
}

Response:
{
  "suggestions": [
    {
      "suggestion": "Best time: Morning sessions...",
      "priority": 1
    }
  ]
}
```

#### Workout Plan Generation
```
POST /workout_plan
{
  "client_id": 1,
  "duration_weeks": 4,
  "focus_areas": ["strength", "cardio"]
}

Response:
{
  "client_id": 1,
  "duration_weeks": 4,
  "focus_areas": ["strength", "cardio"],
  "weeks": [
    {
      "week": 1,
      "workouts": [
        {
          "day": 1,
          "exercises": [...]
        }
      ]
    }
  ]
}
```

## Testing

### Check AI Status
```bash
curl http://localhost:5000/api/ai/status
```

Response:
```json
{
  "configured": false,
  "using_seed_data": true,
  "note": "Currently using seed data..."
}
```

### Test Workout Recommendations
```bash
curl -X POST http://localhost:5000/api/ai/workout-recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "goals": ["strength"],
    "fitness_level": "intermediate"
  }'
```

## Roadmap Review

⚠️ **REVIEW NEEDED**: AI service integration

- [ ] Select AI service provider (OpenAI, Anthropic, custom)
- [ ] Configure API endpoints
- [ ] Implement authentication
- [ ] Test AI responses
- [ ] Update `_call_ai_service()` implementation
- [ ] Add error handling and fallbacks
- [ ] Monitor AI usage and costs
- [ ] Add rate limiting if needed

## Notes

- All AI endpoints work with seed data by default
- No breaking changes when switching to external AI
- Seed data provides realistic examples for testing
- Easy to A/B test seed vs AI responses
- Fallback to seed data if AI service fails

