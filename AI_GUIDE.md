# FitnessCRM AI Orchestrator - Complete Guide

**Intelligent automation and personalization system**  
**Last Updated**: December 2024

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Agent Types](#agent-types)
5. [Integration Points](#integration-points)
6. [Configuration](#configuration)
7. [Deployment](#deployment)
8. [Usage Examples](#usage-examples)

---

## Overview

The AI Orchestrator is an intelligent system that coordinates multiple AI agents to provide personalized recommendations, automated planning, and intelligent analysis for FitnessCRM.

### Key Features

- **Multi-Agent Coordination**: Multiple specialized AI agents working together
- **Intelligent Planning**: Automated workout and meal plan generation
- **Personalization**: Recommendations based on client data and goals
- **Natural Language Processing**: Understand and generate human-like text
- **Context Awareness**: Maintains context across interactions
- **Extensible Architecture**: Easy to add new agents and capabilities

### Benefits

- **For Trainers**: Automated plan creation, intelligent insights
- **For Clients**: Personalized recommendations, progress analysis
- **For Admins**: System-wide analytics, optimization suggestions

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────┐
│           AI Orchestrator Core                  │
│  ┌──────────────────────────────────────┐      │
│  │     Agent Manager & Coordinator       │      │
│  └──────────────────────────────────────┘      │
│         │         │         │         │         │
│    ┌────┴────┐ ┌──┴──┐ ┌───┴───┐ ┌───┴────┐  │
│    │Planning │ │Comm.│ │Analysis│ │Recommend│  │
│    │ Agent   │ │Agent│ │ Agent  │ │ Agent   │  │
│    └─────────┘ └─────┘ └────────┘ └─────────┘  │
└─────────────────────────────────────────────────┘
          │                           │
          ▼                           ▼
┌──────────────────┐       ┌──────────────────┐
│  FitnessCRM API  │       │   LLM Provider   │
│  (Flask Backend) │       │ (OpenAI/Local)   │
└──────────────────┘       └──────────────────┘
```

### Agent Types

#### 1. Planning Agent
**Responsibility**: Create workout and meal plans

**Capabilities**:
- Generate personalized workout plans
- Create meal plans based on goals
- Schedule training sessions
- Adjust plans based on progress

**Input Data**:
- Client profile (age, fitness level, goals)
- Medical conditions and restrictions
- Equipment availability
- Time constraints

**Output**:
- Structured workout plans
- Meal plans with macros
- Exercise recommendations
- Scheduling suggestions

#### 2. Communication Agent
**Responsibility**: Generate intelligent messages

**Capabilities**:
- Compose personalized emails
- Generate SMS messages
- Create notification content
- Draft reports and summaries

**Input Data**:
- Client information
- Conversation history
- Message context
- Communication preferences

**Output**:
- Natural language messages
- Email templates
- SMS content
- Report text

#### 3. Analysis Agent
**Responsibility**: Analyze progress and performance

**Capabilities**:
- Progress trend analysis
- Performance evaluation
- Goal achievement tracking
- Anomaly detection

**Input Data**:
- Progress records
- Session history
- Measurement data
- Performance metrics

**Output**:
- Analysis reports
- Trend insights
- Achievement summaries
- Recommendations

#### 4. Recommendation Agent
**Responsibility**: Provide personalized suggestions

**Capabilities**:
- Exercise recommendations
- Nutrition suggestions
- Schedule optimization
- Goal adjustments

**Input Data**:
- Client profile
- Progress data
- Preferences
- Historical performance

**Output**:
- Personalized recommendations
- Alternative suggestions
- Optimization ideas
- Next steps

### Orchestration Flow

```
1. Request → Orchestrator
2. Orchestrator → Appropriate Agent(s)
3. Agent → LLM Provider
4. LLM Provider → Agent (response)
5. Agent → Orchestrator (processed result)
6. Orchestrator → FitnessCRM API
7. API → User Interface
```

---

## Quick Start

### Prerequisites

- FitnessCRM backend running
- Python 3.11+
- OpenAI API key (or local LLM setup)

### Installation

```bash
# Navigate to AI orchestrator directory
cd ai-orchestrator

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env
```

### Configuration

Edit `.env`:

```env
# LLM Provider
LLM_PROVIDER=openai  # or 'local'
OPENAI_API_KEY=your-api-key-here

# Model Selection
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
TEMPERATURE=0.7

# FitnessCRM API
FITNESSCRM_API_URL=http://localhost:5000

# Agent Configuration
MAX_RETRIES=3
TIMEOUT=30
```

### Start AI Orchestrator

```bash
# Start the orchestrator service
python orchestrator.py

# Or with Docker
docker-compose up ai-orchestrator
```

### Test Connection

```bash
# Test AI orchestrator
curl http://localhost:5001/health

# Test agent endpoint
curl -X POST http://localhost:5001/api/generate-plan \
  -H "Content-Type: application/json" \
  -d '{"client_id": 1, "plan_type": "workout"}'
```

---

## Integration Points

### 1. Workout Plan Generation

**Endpoint**: `POST /api/ai/workout-plan`

**Request**:
```json
{
  "client_id": 1,
  "duration_weeks": 8,
  "goals": ["strength", "weight_loss"],
  "fitness_level": "intermediate",
  "equipment": ["dumbbells", "barbell"]
}
```

**Response**:
```json
{
  "plan": {
    "name": "8-Week Strength & Weight Loss Program",
    "weeks": [
      {
        "week": 1,
        "sessions": [
          {
            "day": "Monday",
            "exercises": [
              {
                "name": "Barbell Squats",
                "sets": 3,
                "reps": 10,
                "rest": "90s"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### 2. Meal Plan Generation

**Endpoint**: `POST /api/ai/meal-plan`

**Request**:
```json
{
  "client_id": 1,
  "goal": "muscle_gain",
  "calories": 2500,
  "dietary_restrictions": ["gluten_free"]
}
```

**Response**:
```json
{
  "meal_plan": {
    "daily_calories": 2500,
    "macros": {
      "protein": "40%",
      "carbs": "35%",
      "fat": "25%"
    },
    "meals": [...]
  }
}
```

### 3. Progress Analysis

**Endpoint**: `POST /api/ai/analyze-progress`

**Request**:
```json
{
  "client_id": 1,
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-03-01"
  }
}
```

**Response**:
```json
{
  "analysis": {
    "summary": "Excellent progress...",
    "trends": {...},
    "recommendations": [...]
  }
}
```

### 4. Message Generation

**Endpoint**: `POST /api/ai/generate-message`

**Request**:
```json
{
  "client_id": 1,
  "message_type": "motivation",
  "context": "missed last two sessions"
}
```

**Response**:
```json
{
  "message": {
    "subject": "We Miss You!",
    "body": "Hey [Name], we noticed you've been away...",
    "tone": "encouraging"
  }
}
```

---

## Configuration

### LLM Provider Options

#### OpenAI (Recommended)
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
TEMPERATURE=0.7
MAX_TOKENS=2000
```

**Pros**:
- High quality responses
- Reliable and fast
- Well-documented

**Cons**:
- Requires API key
- Usage costs
- Internet dependency

#### Local LLM (Privacy-focused)
```env
LLM_PROVIDER=local
LOCAL_MODEL_PATH=/path/to/model
MODEL_TYPE=llama  # or mistral
TEMPERATURE=0.7
```

**Pros**:
- No external API calls
- Complete privacy
- No usage costs

**Cons**:
- Requires powerful hardware
- Slower inference
- More setup complexity

### Agent Configuration

```env
# Planning Agent
PLANNING_AGENT_ENABLED=true
PLANNING_AGENT_MODEL=gpt-4
PLANNING_AGENT_TEMPERATURE=0.7

# Communication Agent
COMM_AGENT_ENABLED=true
COMM_AGENT_MODEL=gpt-3.5-turbo
COMM_AGENT_TEMPERATURE=0.8

# Analysis Agent
ANALYSIS_AGENT_ENABLED=true
ANALYSIS_AGENT_MODEL=gpt-4
ANALYSIS_AGENT_TEMPERATURE=0.5

# Recommendation Agent
RECOMMEND_AGENT_ENABLED=true
RECOMMEND_AGENT_MODEL=gpt-3.5-turbo
RECOMMEND_AGENT_TEMPERATURE=0.7
```

### Performance Tuning

```env
# Request limits
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30
MAX_RETRIES=3

# Caching
ENABLE_CACHE=true
CACHE_TTL=3600  # seconds

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
```

---

## Deployment

### Docker Deployment

```bash
# Build AI orchestrator image
docker build -t fitnesscrm-ai ./ai-orchestrator

# Run with docker-compose
docker-compose up ai-orchestrator
```

### Standalone Deployment

```bash
# Install as service
sudo cp ai-orchestrator.service /etc/systemd/system/
sudo systemctl enable ai-orchestrator
sudo systemctl start ai-orchestrator

# Check status
sudo systemctl status ai-orchestrator
```

### Production Considerations

1. **API Key Security**
   - Use environment variables
   - Rotate keys regularly
   - Monitor usage

2. **Scaling**
   - Deploy multiple instances
   - Use load balancer
   - Implement caching

3. **Monitoring**
   - Track API usage
   - Monitor response times
   - Log errors

4. **Cost Management**
   - Set usage limits
   - Monitor token consumption
   - Optimize prompts

---

## Usage Examples

### Generate Workout Plan

```python
import requests

response = requests.post(
    'http://localhost:5001/api/ai/workout-plan',
    json={
        'client_id': 1,
        'duration_weeks': 12,
        'goals': ['muscle_gain'],
        'fitness_level': 'beginner'
    }
)

plan = response.json()
print(plan['plan']['name'])
```

### Analyze Client Progress

```python
response = requests.post(
    'http://localhost:5001/api/ai/analyze-progress',
    json={
        'client_id': 1,
        'date_range': {
            'start': '2024-01-01',
            'end': '2024-03-01'
        }
    }
)

analysis = response.json()
print(analysis['analysis']['summary'])
```

### Generate Personalized Message

```python
response = requests.post(
    'http://localhost:5001/api/ai/generate-message',
    json={
        'client_id': 1,
        'message_type': 'celebration',
        'context': 'lost 10 pounds'
    }
)

message = response.json()
print(message['message']['body'])
```

---

## Troubleshooting

### Common Issues

**Issue: "API key not found"**
- Solution: Set `OPENAI_API_KEY` in `.env`
- Verify key is valid
- Check environment variables loaded

**Issue: "Timeout errors"**
- Solution: Increase `REQUEST_TIMEOUT`
- Check network connectivity
- Consider using faster model

**Issue: "Rate limit exceeded"**
- Solution: Reduce `RATE_LIMIT_PER_MINUTE`
- Implement request queuing
- Upgrade OpenAI plan

**Issue: "Poor quality responses"**
- Solution: Adjust `TEMPERATURE` (0.7-0.9)
- Use GPT-4 instead of GPT-3.5
- Improve prompt engineering

---

## Advanced Features

### Custom Prompts

Create custom prompts in `ai-orchestrator/prompts/`:

```python
# custom_workout_prompt.py
def get_workout_prompt(client_data):
    return f"""
    Create a personalized workout plan for:
    - Fitness Level: {client_data['fitness_level']}
    - Goals: {client_data['goals']}
    - Equipment: {client_data['equipment']}
    
    Format as JSON with exercises, sets, reps.
    """
```

### Agent Chaining

Combine multiple agents:

```python
# 1. Analyze progress
analysis = analyze_agent.analyze(client_id)

# 2. Generate recommendations based on analysis
recommendations = recommend_agent.recommend(analysis)

# 3. Create message about recommendations
message = comm_agent.generate_message(recommendations)
```

### Webhooks

Set up webhooks for events:

```env
WEBHOOK_URL=https://your-app.com/webhook
WEBHOOK_EVENTS=plan_created,analysis_complete
```

---

## API Reference

See **AI_AGENT_INTEGRATION_POINTS.md** for complete API documentation.

---

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for secrets
3. **Implement rate limiting** on endpoints
4. **Validate all inputs** before processing
5. **Monitor API usage** and costs
6. **Encrypt sensitive data** in transit and at rest
7. **Audit agent decisions** for accountability

---

## Future Enhancements

- Voice-based interactions
- Image analysis (form checking)
- Multi-language support
- Custom agent creation UI
- Real-time collaboration
- Advanced analytics
- Integration with wearables

---

**Related Documentation**:
- MANUAL.md - Complete FitnessCRM guide
- API_DOCUMENTATION.md - REST API reference
- DEPLOYMENT_GUIDE.md - Deployment instructions
