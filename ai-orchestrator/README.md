# AI Orchestrator Service

A separate, intelligent AI orchestration service for FitnessCRM that uses OpenAI, LangChain, and LangGraph to manage AI agents for enhanced platform capabilities.

## 🎯 Overview

The AI Orchestrator is a standalone service that:
- Runs as its own Railway instance
- Shares the same PostgreSQL database with the main FitnessCRM app
- Uses OpenAI with LangChain/LangGraph for agent management
- Provides AI-powered features through specialized agents
- Includes self-healing and code monitoring capabilities
- Offers a management GUI for controlling AI agents

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FitnessCRM Main App                  │
│                   (Railway Instance 1)                  │
│                        Port 5000                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Shared PostgreSQL
                     │ Database
                     │
┌────────────────────┴────────────────────────────────────┐
│                 AI Orchestrator Service                 │
│                   (Railway Instance 2)                  │
│                        Port 5001                        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │         LangGraph Agent Orchestrator            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐     │  │
│  │  │ Workout  │  │ Progress │  │Scheduler │     │  │
│  │  │Optimizer │  │ Monitor  │  │   AI     │     │  │
│  │  └──────────┘  └──────────┘  └──────────┘     │  │
│  │  ┌──────────┐  ┌──────────┐                   │  │
│  │  │  Health  │  │   Code   │                   │  │
│  │  │ Checker  │  │ Analyzer │                   │  │
│  │  └──────────┘  └──────────┘                   │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │            OpenAI Integration                   │  │
│  │              (GPT-4 Turbo)                      │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 🤖 AI Agents

### 1. Workout Optimizer Agent
**Purpose**: Analyzes client data and generates personalized workout recommendations

**Capabilities**:
- Considers fitness level, goals, available equipment
- Creates progressive workout plans
- Adapts to client preferences and constraints
- Provides detailed exercise instructions

**Integration Points**:
- Client Portal: Workout suggestions
- Trainer Portal: Auto-generated workout plans
- API: `/api/ai/workout-recommendations`

### 2. Progress Monitor Agent
**Purpose**: Tracks and analyzes client progress with predictive insights

**Capabilities**:
- Analyzes historical fitness data
- Identifies trends and patterns
- Predicts time to reach goals
- Provides motivational insights

**Integration Points**:
- Client Portal: Progress dashboard
- Trainer Portal: Client progress reports
- API: `/api/ai/progress-prediction`

### 3. Scheduling Intelligence Agent
**Purpose**: Optimizes trainer-client scheduling

**Capabilities**:
- Analyzes scheduling patterns
- Considers trainer/client preferences
- Optimizes for attendance and retention
- Suggests ideal time slots

**Integration Points**:
- Trainer Portal: Schedule optimization
- Calendar: Smart scheduling suggestions
- API: `/api/ai/scheduling-suggestions`

### 4. Health Checker Agent
**Purpose**: Monitors system health and identifies issues

**Capabilities**:
- Database connectivity checks
- API health monitoring
- Agent performance tracking
- Automated alerting

**Integration Points**:
- Admin Dashboard: System health display
- Monitoring: Continuous health checks
- API: `/api/health-status`

### 5. Code Analyzer Agent
**Purpose**: Analyzes code quality and suggests improvements

**Capabilities**:
- Bug detection
- Security vulnerability identification
- Performance optimization suggestions
- Code style improvements
- Error analysis and fix suggestions

**Integration Points**:
- Admin Dashboard: Code quality reports
- CI/CD: Automated code reviews
- API: `/api/suggestions`

## 🚀 Deployment

### Railway Deployment

1. **Create New Service**
   ```
   Railway Dashboard → New Project → Deploy from GitHub
   ```

2. **Configure Service**
   - Set Root Directory: `ai-orchestrator`
   - Service Name: `fitnesscrm-ai-orchestrator`

3. **Link Database**
   - Use existing PostgreSQL database from main app
   - Railway will auto-populate `DATABASE_URL`

4. **Environment Variables**
   ```
   FLASK_ENV=production
   SECRET_KEY=<generate-secure-key>
   OPENAI_API_KEY=<your-openai-key>
   OPENAI_MODEL=gpt-4-turbo-preview
   MAIN_APP_URL=<main-app-railway-url>
   MAIN_APP_API_KEY=<shared-api-key>
   ENABLE_SELF_HEALING=true
   ENABLE_CODE_MONITORING=true
   ```

5. **Deploy**
   - Railway will automatically detect Python and use Procfile
   - Service will be available at: `https://fitnesscrm-ai-orchestrator.up.railway.app`

### Local Development

1. **Setup Environment**
   ```bash
   cd ai-orchestrator
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run Service**
   ```bash
   python app.py
   # Service available at http://localhost:5001
   ```

## 📡 API Endpoints

### Agent Management
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
- `GET /api/agents/:id` - Get agent details
- `PUT /api/agents/:id` - Update agent
- `DELETE /api/agents/:id` - Delete agent

### Execution
- `POST /api/execute` - Execute agent or workflow
- `GET /api/executions` - List executions
- `GET /api/executions/:id` - Get execution details

### Monitoring
- `GET /api/health` - Service health check
- `GET /api/health-status` - System health status
- `GET /api/metrics` - Agent performance metrics

### Code Quality
- `GET /api/suggestions` - List code suggestions
- `PUT /api/suggestions/:id` - Update suggestion status

## 🔧 Integration with Main App

### 1. Update Main App's AI Routes

Edit `/backend/utils/ai_service.py`:

```python
import os
import requests

AI_ORCHESTRATOR_URL = os.getenv('AI_ORCHESTRATOR_URL', 'http://localhost:5001')
AI_ORCHESTRATOR_KEY = os.getenv('AI_ORCHESTRATOR_KEY')

def get_workout_recommendations(client_id, goals, fitness_level):
    """Call AI orchestrator for workout recommendations"""
    try:
        response = requests.post(
            f"{AI_ORCHESTRATOR_URL}/api/execute",
            json={
                'task_type': 'workout_optimization',
                'input_data': {
                    'client_id': client_id,
                    'goals': goals,
                    'fitness_level': fitness_level
                }
            },
            headers={'Authorization': f'Bearer {AI_ORCHESTRATOR_KEY}'},
            timeout=30
        )
        return response.json()
    except Exception as e:
        logger.error(f"AI orchestrator call failed: {str(e)}")
        return None
```

### 2. Add Environment Variables to Main App

```
AI_ORCHESTRATOR_URL=https://fitnesscrm-ai-orchestrator.up.railway.app
AI_ORCHESTRATOR_KEY=<shared-api-key>
```

## 🎨 Agent Management GUI

The GUI provides:
- Agent status monitoring
- Agent configuration management
- Execution logs viewer
- Performance metrics dashboard
- Code suggestion review interface
- System health monitoring

Access at: `http://localhost:5001/gui` (coming soon)

## 🔐 Security

- API key authentication between services
- Shared database with proper access controls
- Environment variable encryption in Railway
- Rate limiting on AI API calls
- Audit logging for all agent executions

## 📊 Monitoring

- Prometheus metrics endpoint: `/metrics`
- Agent execution tracking
- Performance metrics
- Error rate monitoring
- Cost tracking for OpenAI usage

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=agents --cov=api --cov-report=html
```

## 📝 Usage Examples

### Execute Workout Optimization

```bash
curl -X POST http://localhost:5001/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "workout_optimization",
    "input_data": {
      "client_id": 1,
      "goals": ["weight_loss", "strength"],
      "fitness_level": "intermediate",
      "available_equipment": ["dumbbells", "bench"],
      "time_per_session": 45,
      "sessions_per_week": 3
    }
  }'
```

### Check System Health

```bash
curl http://localhost:5001/api/health-status
```

### List Code Suggestions

```bash
curl http://localhost:5001/api/suggestions?status=pending
```

## 🛠️ Development

### Adding a New Agent

1. Create agent class in `agents/my_agent.py`
2. Inherit from `BaseAgent`
3. Implement `execute()` method
4. Add agent type to orchestrator
5. Update default agents in `app.py`

### Adding New API Endpoints

1. Add route to `api/routes.py`
2. Follow existing patterns
3. Add appropriate error handling
4. Update API documentation

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Railway Deployment Guide](https://docs.railway.app/)

## 🤝 Contributing

See main repository CONTRIBUTING.md

## 📄 License

Same as main FitnessCRM application
