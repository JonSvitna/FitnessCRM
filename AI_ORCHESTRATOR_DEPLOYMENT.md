# AI Orchestrator Deployment Guide

Complete guide for deploying the AI Orchestrator service to Railway.

## 🎯 Overview

The AI Orchestrator is deployed as a **separate Railway service** that shares the PostgreSQL database with the main FitnessCRM application. This architecture provides:

- **Isolation**: AI processing doesn't impact main app performance
- **Scalability**: Can scale AI service independently
- **Flexibility**: Easy to update AI models and agents
- **Cost Optimization**: Can use different compute resources

## 📋 Prerequisites

- Railway account with existing FitnessCRM project
- OpenAI API key with GPT-4 access
- Access to your FitnessCRM PostgreSQL database

## 🚀 Deployment Steps

### Step 1: Create New Railway Service

1. Go to your Railway dashboard
2. Open your FitnessCRM project
3. Click **"+ New"** → **"GitHub Repo"**
4. Select your FitnessCRM repository
5. Railway will create a new service

### Step 2: Configure Service Settings

1. **Set Service Name**
   - Click on the new service
   - Click settings icon
   - Name: `ai-orchestrator`

2. **Set Root Directory**
   - In Settings → **Root Directory**
   - Enter: `ai-orchestrator`
   - This tells Railway to deploy from the ai-orchestrator folder

3. **Configure Build & Deploy**
   - Railway auto-detects Python from `requirements.txt`
   - Uses `Procfile` for start command
   - No additional configuration needed

### Step 3: Link PostgreSQL Database

1. **Connect to Existing Database**
   - In your AI Orchestrator service settings
   - Go to **Variables** tab
   - Click **"+ Reference Variable"**
   - Select your existing PostgreSQL service
   - Choose `DATABASE_URL`
   - Railway will automatically inject the connection string

### Step 4: Configure Environment Variables

Add these environment variables in the **Variables** tab:

#### Required Variables
```
FLASK_ENV=production
PORT=5001
SECRET_KEY=<generate-a-secure-random-key>
OPENAI_API_KEY=<your-openai-api-key>
```

#### Optional Configuration
```
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
MAIN_APP_URL=<your-main-app-railway-url>
MAIN_APP_API_KEY=<generate-shared-api-key>
ENABLE_SELF_HEALING=true
ENABLE_CODE_MONITORING=true
ENABLE_WORKOUT_OPTIMIZATION=true
ENABLE_PROGRESS_MONITORING=true
ENABLE_SCHEDULING_INTELLIGENCE=true
LOG_LEVEL=INFO
```

#### Generate Secure Keys

Use Python to generate secure keys:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Step 5: Deploy

1. Railway will automatically deploy after configuration
2. Monitor deployment logs in Railway dashboard
3. Wait for "Deployed successfully" message
4. Note your service URL: `https://<your-service>.up.railway.app`

### Step 6: Verify Deployment

Test the deployment:

```bash
# Health check
curl https://<your-ai-orchestrator-url>/api/health

# Expected response:
# {"status": "healthy", "service": "ai-orchestrator", "version": "1.0.0"}

# List agents
curl https://<your-ai-orchestrator-url>/api/agents

# Expected: List of 5 default agents
```

### Step 7: Connect Main App to Orchestrator

1. **Update Main App Environment Variables**
   
   In your main FitnessCRM backend service, add:
   ```
   AI_ORCHESTRATOR_URL=https://<your-ai-orchestrator-url>
   AI_ORCHESTRATOR_KEY=<your-shared-api-key>
   ```

2. **Redeploy Main App**
   - Railway will auto-redeploy with new variables

## 🔧 Configuration Details

### Database Shared Access

The AI Orchestrator shares the PostgreSQL database with your main app:

**Main App Tables:**
- trainers, clients, sessions, workouts, etc.

**AI Orchestrator Tables:**
- ai_agents
- ai_agent_executions
- ai_agent_metrics
- ai_system_health
- ai_code_suggestions

Both services can read/write to the same database safely.

### Port Configuration

- **Main App**: Port 5000 (or Railway assigned)
- **AI Orchestrator**: Port 5001 (or Railway assigned)
- Railway handles external port mapping automatically

### OpenAI Configuration

Recommended models and settings:

| Use Case | Model | Temperature |
|----------|-------|-------------|
| Workout Plans | gpt-4-turbo-preview | 0.7 |
| Progress Analysis | gpt-4-turbo-preview | 0.7 |
| Code Analysis | gpt-4-turbo-preview | 0.3 |
| Error Debugging | gpt-4-turbo-preview | 0.3 |

**Cost Optimization**:
- Use `gpt-3.5-turbo` for development/testing
- Use `gpt-4-turbo-preview` for production
- Set rate limits in OpenAI dashboard

## 📊 Monitoring

### Railway Dashboard

Monitor in Railway:
1. **Metrics** tab: CPU, Memory, Network usage
2. **Logs** tab: Application logs
3. **Deployments** tab: Deployment history

### Application Logs

View logs:
```bash
railway logs -s ai-orchestrator
```

### Health Checks

Set up automated health checks:
```bash
# Add to your monitoring system
curl https://<ai-orchestrator-url>/api/health

# Check system health
curl https://<ai-orchestrator-url>/api/health-status
```

## 🔐 Security Best Practices

### 1. API Key Security
- Generate strong, unique API keys
- Store in Railway environment variables (encrypted)
- Rotate keys regularly
- Use different keys for dev/prod

### 2. Database Access
- Use read-only credentials where possible
- Enable SSL/TLS for database connections
- Monitor query patterns for anomalies

### 3. OpenAI Key Protection
- Never commit API keys to Git
- Set spending limits in OpenAI dashboard
- Monitor usage for unusual patterns
- Enable alerts for high usage

### 4. Network Security
- Use HTTPS for all API calls
- Implement rate limiting
- Add IP allowlisting if needed
- Enable CORS only for trusted origins

## 🐛 Troubleshooting

### Issue: Service Won't Start

**Check:**
1. Root directory is set to `ai-orchestrator`
2. All required environment variables are set
3. DATABASE_URL is properly formatted
4. OpenAI API key is valid

**View logs:**
```bash
railway logs -s ai-orchestrator --tail 100
```

### Issue: Database Connection Failed

**Solutions:**
1. Verify DATABASE_URL variable is set
2. Check if database service is running
3. Ensure network connectivity between services
4. Review database logs for errors

**Test connection:**
```bash
railway shell -s ai-orchestrator
python -c "from app import app; app.app_context().push(); from models import db; db.session.execute(db.text('SELECT 1'))"
```

### Issue: OpenAI API Errors

**Common causes:**
1. Invalid API key
2. Insufficient credits/quota
3. Rate limiting
4. Model not available

**Check OpenAI status:**
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Issue: High Memory Usage

**Solutions:**
1. Reduce number of workers in Procfile
2. Implement request queuing
3. Add rate limiting
4. Scale up Railway plan if needed

## 📈 Scaling

### Vertical Scaling
Upgrade Railway plan for more resources:
- Starter: 512 MB RAM, 1 vCPU
- Developer: 8 GB RAM, 8 vCPU
- Team: 32 GB RAM, 32 vCPU

### Horizontal Scaling
Add multiple service replicas:
1. Railway settings → Replicas
2. Set replica count (requires Team plan)
3. Railway handles load balancing

### Cost Optimization
- Use cheaper models for non-critical tasks
- Implement caching for repeated queries
- Set OpenAI rate limits
- Use Railway's auto-sleep for dev environments

## 🔄 Updates and Maintenance

### Updating Code
1. Push changes to GitHub
2. Railway auto-deploys from main branch
3. Monitor deployment logs
4. Test with health check

### Updating Dependencies
1. Update `requirements.txt`
2. Push to GitHub
3. Railway rebuilds and redeploys

### Database Migrations
```bash
# Create migration
railway shell -s ai-orchestrator
flask db migrate -m "Add new table"
flask db upgrade
```

### Rollback Deployment
1. Railway Dashboard → Deployments
2. Find previous successful deployment
3. Click "Redeploy"

## 📞 Support

- Railway Status: https://status.railway.app/
- Railway Docs: https://docs.railway.app/
- OpenAI Status: https://status.openai.com/
- FitnessCRM Issues: https://github.com/JonSvitna/FitnessCRM/issues

## ✅ Deployment Checklist

- [ ] Railway service created
- [ ] Root directory set to `ai-orchestrator`
- [ ] Database linked and DATABASE_URL set
- [ ] OpenAI API key configured
- [ ] All required environment variables set
- [ ] Service deployed successfully
- [ ] Health check returns 200
- [ ] Default agents created
- [ ] Main app connected to orchestrator
- [ ] Monitoring configured
- [ ] Documentation updated
- [ ] Team notified of new service URL

## 🎉 Next Steps

After successful deployment:

1. **Test AI Features**: Try each agent through the API
2. **Monitor Performance**: Set up alerts for errors/performance
3. **Optimize Costs**: Monitor OpenAI usage and adjust
4. **Add Custom Agents**: Create domain-specific agents
5. **Build GUI**: Develop agent management interface
6. **Enable Self-Healing**: Configure automated monitoring
7. **Document APIs**: Create API documentation for team

---

**Deployment Date**: _____________

**Deployed By**: _____________

**Service URL**: _____________

**Notes**: _____________
