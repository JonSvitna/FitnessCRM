# AI Orchestrator - Quick Start Guide

One-page reference for deploying and using the AI Orchestrator.

## 🚀 5-Minute Deployment

### 1. Create Railway Service (2 min)
```bash
1. Railway Dashboard → Your Project → "+ New"
2. Select "GitHub Repo" → Choose FitnessCRM
3. Service Name: "ai-orchestrator"
4. Settings → Root Directory: "ai-orchestrator"
```

### 2. Configure Environment (2 min)
Add these variables in Railway → Variables:
```bash
FLASK_ENV=production
OPENAI_API_KEY=sk-...your-key...
OPENAI_MODEL=gpt-4-turbo-preview
MAIN_APP_URL=https://your-main-app.up.railway.app
DATABASE_URL=  # Auto-linked from existing database
```

### 3. Deploy & Verify (1 min)
```bash
# Railway deploys automatically
# Wait for "Deployed successfully"

# Test it:
curl https://your-orchestrator.up.railway.app/api/health
```

## 🔗 Connect Main App

Add to main backend service variables:
```bash
AI_ORCHESTRATOR_URL=https://your-orchestrator.up.railway.app
AI_ORCHESTRATOR_KEY=optional-shared-key
```

## 🎯 Quick Tests

### Test Health Check
```bash
curl -X POST https://your-orchestrator.up.railway.app/api/execute \
  -H "Content-Type: application/json" \
  -d '{"task_type": "health_check", "input_data": {}}'
```

### Test Workout Generation
```bash
curl -X POST https://your-orchestrator.up.railway.app/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "workout_optimization",
    "input_data": {
      "client_id": 1,
      "goals": ["strength"],
      "fitness_level": "intermediate"
    }
  }'
```

### Access GUI
Open in browser:
```
https://your-orchestrator.up.railway.app/gui
```

## 📊 Integration Examples

### Frontend - Add Workout Widget
```javascript
// client.js
async function loadAIWorkouts() {
  const response = await fetch(
    `${API_URL}/api/ai/workout-recommendations`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        client_id: clientId,
        goals: ['strength', 'cardio'],
        fitness_level: 'intermediate'
      })
    }
  );
  const data = await response.json();
  displayWorkouts(data.recommendations);
}
```

### Backend - Add Auto-Fix
```python
# error_handler.py
from utils.ai_service import analyze_error

@app.errorhandler(Exception)
def handle_error(e):
    analysis = analyze_error({
        'error': str(e),
        'stack_trace': traceback.format_exc()
    })
    # Log analysis for review
    logger.info(f"AI Analysis: {analysis}")
```

## 🎛️ Agent Management

### Via GUI
```
https://your-orchestrator.up.railway.app/gui
- View all agents
- Enable/disable agents
- See execution history
- Review code suggestions
```

### Via API
```bash
# List agents
curl https://your-orchestrator.up.railway.app/api/agents

# Create agent
curl -X POST https://your-orchestrator.up.railway.app/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Custom Agent",
    "type": "custom",
    "description": "Does something cool"
  }'

# Update agent
curl -X PUT https://your-orchestrator.up.railway.app/api/agents/1 \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

## 🔧 Common Issues

### Issue: Service won't start
**Solution**: Check Railway logs
```bash
railway logs -s ai-orchestrator --tail 100
```

### Issue: OpenAI errors
**Solution**: Verify API key
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Issue: Database connection failed
**Solution**: Verify DATABASE_URL is linked
```bash
# In Railway → ai-orchestrator → Variables
# Should see DATABASE_URL with value from Postgres service
```

### Issue: Main app can't reach orchestrator
**Solution**: Check URL and network
```bash
curl https://your-orchestrator.up.railway.app/api/health
# Should return: {"status": "healthy", ...}
```

## 📈 Monitor Performance

### View Metrics
```bash
# Agent executions
curl https://your-orchestrator.up.railway.app/api/executions?per_page=20

# System health
curl https://your-orchestrator.up.railway.app/api/health-status

# Performance metrics
curl https://your-orchestrator.up.railway.app/api/metrics
```

### OpenAI Usage
Check in OpenAI dashboard:
```
https://platform.openai.com/usage
```

## 💰 Cost Optimization

### Development
- Use `gpt-3.5-turbo` (set in OPENAI_MODEL)
- Estimated: $5-10/month

### Production
- Use `gpt-4-turbo-preview`
- Implement caching
- Set rate limits
- Estimated: $50-200/month

### Railway
- Start with Developer plan ($20/month)
- Scale up if needed

## 🔐 Security Checklist

- [ ] OpenAI API key secured in Railway variables
- [ ] FLASK_ENV=production (not development)
- [ ] Shared API key between services (optional)
- [ ] Database uses SSL/TLS
- [ ] CORS configured appropriately
- [ ] Rate limiting enabled
- [ ] Monitoring and alerts set up

## 📚 Full Documentation

For detailed information:
- **Deployment**: AI_ORCHESTRATOR_DEPLOYMENT.md
- **Architecture**: ai-orchestrator/README.md
- **Integration**: AI_AGENT_INTEGRATION_POINTS.md
- **Self-Healing**: SELF_HEALING_GUIDE.md
- **Summary**: AI_ORCHESTRATOR_SUMMARY.md

## 🆘 Get Help

- Check logs: `railway logs -s ai-orchestrator`
- Review documentation in repo
- Test each component individually
- Verify environment variables
- Check Railway service status

## ✅ Post-Deployment Checklist

After deployment:
- [ ] Health check returns 200
- [ ] GUI loads at /gui
- [ ] All 5 agents created
- [ ] Test one agent execution
- [ ] Main app can call orchestrator
- [ ] Database tables created
- [ ] Monitor for 24 hours
- [ ] Check OpenAI usage
- [ ] Review execution logs
- [ ] Plan frontend integration

---

**Deployment Time**: ~5 minutes
**Configuration Time**: ~10 minutes
**Testing Time**: ~15 minutes
**Total**: ~30 minutes to production! 🚀
