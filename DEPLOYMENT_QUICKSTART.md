# FitnessCRM - Deployment Quick Start Guide 🚀

**Goal**: Get FitnessCRM production-ready in 1 week  
**Audience**: Developers deploying the application  
**Last Updated**: December 2024

---

## 🎯 Overview

This guide provides immediate actionable steps to deploy FitnessCRM to production. For detailed analysis, see `DEPLOYMENT_ASSESSMENT.md`.

---

## 📋 Pre-Deployment Checklist

### Critical (Must Complete)
- [ ] Environment variables configured
- [ ] Database connected and migrations run
- [ ] Email service configured (SMTP)
- [ ] Authentication working end-to-end
- [ ] Security headers added
- [ ] Rate limiting implemented
- [ ] Basic monitoring set up

### Important (Should Complete)
- [ ] Payment processing configured (Stripe)
- [ ] Automated backups enabled
- [ ] SSL/TLS certificate installed
- [ ] Redis caching configured
- [ ] Error tracking active (Sentry)

### Nice to Have
- [ ] SMS notifications configured (Twilio)
- [ ] AI service integrated
- [ ] Wearable devices integrated
- [ ] Advanced monitoring dashboard

---

## Day 1: Environment Setup ⚙️

### Step 1: Create Backend Environment File

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` with these **required** variables:

```env
# Database (Get from Railway)
DATABASE_URL=postgresql://user:password@host:port/database

# Security (Generate strong keys)
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET=another-super-secret-key-for-jwt-tokens

# Server
FLASK_ENV=production
PORT=5000

# CORS (Your frontend URL)
CORS_ORIGINS=https://your-frontend.vercel.app,https://www.yourdomain.com

# Email (Gmail App Password recommended)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

**How to generate secure keys:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**How to get Gmail App Password:**
1. Enable 2-Factor Authentication on Gmail
2. Go to: Google Account → Security → 2-Step Verification → App passwords
3. Generate password for "Mail"
4. Use this password in MAIL_PASSWORD

### Step 2: Create Frontend Environment File

```bash
cd frontend
cp .env.example .env
```

Edit `frontend/.env`:

```env
# Backend API URL (Your Railway deployment)
VITE_API_URL=https://your-backend.up.railway.app

# Environment
VITE_APP_ENV=production
```

### Step 3: Verify Configuration

```bash
# Backend
cd backend
python -c "from app import create_app; app = create_app(); print('✅ Backend config OK')"

# Frontend
cd frontend
npm run build
echo "✅ Frontend config OK"
```

---

## Day 2: Database & Email Setup 💾

### Step 1: Initialize Database

If using Railway PostgreSQL (recommended):

```bash
cd backend
# Set DATABASE_URL from Railway
export DATABASE_URL="postgresql://..."

# Initialize database
python init_db.py

# Seed with sample data (optional)
python init_db.py seed
```

### Step 2: Test Email

Create `test_email.py`:

```python
from utils.email import send_email

result = send_email(
    to="your-test-email@example.com",
    subject="FitnessCRM Test Email",
    html="<h1>Email is working!</h1>"
)

print("✅ Email sent successfully" if result else "❌ Email failed")
```

Run:
```bash
cd backend
python test_email.py
```

### Step 3: Run Database Migrations

```bash
cd backend
# If you have migrations
flask db upgrade

# Or just verify tables exist
python -c "from models.database import db; from app import create_app; app = create_app(); print('✅ Database connected')"
```

---

## Day 3: Payment Setup (Stripe) 💳

### Step 1: Get Stripe Credentials

1. Sign up at https://stripe.com
2. Get **test mode** API keys first
3. Navigate to: Developers → API keys

### Step 2: Configure Stripe

Add to `backend/.env`:

```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Step 3: Set Up Webhook

1. Go to: Developers → Webhooks → Add endpoint
2. URL: `https://your-backend.up.railway.app/api/stripe/webhook`
3. Events: Select all `checkout.session.*` and `payment_intent.*`
4. Copy webhook signing secret to STRIPE_WEBHOOK_SECRET

### Step 4: Test Payment

```bash
cd backend
python -c "import stripe; stripe.api_key='sk_test_...'; print('✅ Stripe configured')"
```

---

## Day 4: Fix Authentication TODOs 🔐

### Files to Fix

1. **frontend/src/client.js** (Lines 336-337)

```javascript
// Before (hardcoded):
document.getElementById('total-workouts').textContent = '0'; // TODO: Implement workout tracking
document.getElementById('streak-days').textContent = '0'; // TODO: Implement streak tracking

// After:
async function loadClientStats() {
    const response = await api.get(`/api/clients/${currentUser.id}/stats`);
    document.getElementById('total-workouts').textContent = response.data.total_workouts || '0';
    document.getElementById('streak-days').textContent = response.data.streak_days || '0';
}
loadClientStats();
```

2. **frontend/src/trainer.js** (Lines 191-192)

```javascript
// Before:
document.getElementById('sessions-this-week').textContent = '0'; // TODO: Implement sessions
document.getElementById('new-messages').textContent = '0'; // TODO: Implement messages

// After:
async function loadTrainerStats() {
    const response = await api.get(`/api/trainers/${currentUser.id}/stats`);
    document.getElementById('sessions-this-week').textContent = response.data.sessions_this_week || '0';
    document.getElementById('new-messages').textContent = response.data.unread_messages || '0';
}
loadTrainerStats();
```

3. **frontend/src/messages.js** (Line 12)

```javascript
// Before:
let currentUser = { type: 'trainer', id: 1 }; // TODO: Get from auth/session

// After:
// Get from authentication
let currentUser = null;
async function initAuth() {
    const response = await api.get('/api/auth/me');
    currentUser = response.data;
}
initAuth();
```

4. **frontend/src/main.js** (Multiple locations)

Search and replace:
```javascript
// Find all instances of:
created_by: 1 // TODO: Get from auth
assigned_by: 1, // TODO: Get from auth

// Replace with:
created_by: currentUser.id
assigned_by: currentUser.id
```

### Add Backend Stats Endpoints

Create `backend/api/stats_routes.py`:

```python
from flask import Blueprint, jsonify
from models.database import db, Client, Trainer, Session, WorkoutPlan, Message

stats_bp = Blueprint('stats', __name__, url_prefix='/api')

@stats_bp.route('/clients/<int:client_id>/stats', methods=['GET'])
def get_client_stats(client_id):
    """Get client statistics"""
    # Total workouts completed
    total_workouts = WorkoutPlan.query.filter_by(
        client_id=client_id,
        status='completed'
    ).count()
    
    # Streak days (simplified - implement proper logic)
    streak_days = 0  # TODO: Implement streak calculation
    
    return jsonify({
        'total_workouts': total_workouts,
        'streak_days': streak_days
    })

@stats_bp.route('/trainers/<int:trainer_id>/stats', methods=['GET'])
def get_trainer_stats(trainer_id):
    """Get trainer statistics"""
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Sessions this week
    sessions_this_week = Session.query.filter(
        Session.trainer_id == trainer_id,
        Session.session_date >= week_ago
    ).count()
    
    # Unread messages
    unread_messages = Message.query.filter(
        Message.receiver_id == trainer_id,
        Message.read == False
    ).count() if hasattr(Message, 'read') else 0
    
    return jsonify({
        'sessions_this_week': sessions_this_week,
        'unread_messages': unread_messages
    })
```

Register in `backend/app.py`:
```python
from api.stats_routes import stats_bp
app.register_blueprint(stats_bp)
```

---

## Day 5: Security Hardening 🔒

### Step 1: Add Security Headers

Edit `backend/app.py` to add after CORS setup:

```python
from flask import Flask, jsonify
from flask_cors import CORS

def create_app(config_name=None):
    app = Flask(__name__)
    
    # ... existing setup ...
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Prevent MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # HTTPS only (if in production)
        if app.config.get('FLASK_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://*.railway.app;"
        )
        
        return response
    
    return app
```

### Step 2: Add Rate Limiting

Install Flask-Limiter:
```bash
cd backend
pip install Flask-Limiter
pip freeze > requirements.txt
```

Add to `backend/app.py`:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def create_app(config_name=None):
    app = Flask(__name__)
    
    # ... existing setup ...
    
    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"  # Use Redis in production: "redis://localhost:6379"
    )
    
    # Apply stricter limits to auth endpoints
    from api.auth_routes import auth_bp
    
    @limiter.limit("5 per minute")
    @auth_bp.route('/login', methods=['POST'])
    def login():
        pass  # existing login logic
    
    return app
```

### Step 3: Verify Security

Test security headers:
```bash
curl -I https://your-backend.up.railway.app/api/health
# Should see X-Frame-Options, X-Content-Type-Options, etc.
```

---

## Day 6-7: Monitoring & Deployment 📊

### Step 1: Set Up Sentry (Error Tracking)

1. Sign up at https://sentry.io (free tier available)
2. Create new project
3. Get DSN

Add to `backend/.env`:
```env
SENTRY_DSN=https://...@sentry.io/...
```

Install and configure:
```bash
cd backend
pip install sentry-sdk[flask]
```

Add to `backend/app.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import os

if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.1,  # 10% of transactions
        environment=os.getenv('FLASK_ENV', 'development')
    )
```

### Step 2: Set Up Uptime Monitoring

Use **UptimeRobot** (free tier):
1. Sign up at https://uptimerobot.com
2. Add monitor: HTTPS, `https://your-backend.up.railway.app/api/health`
3. Set check interval: 5 minutes
4. Add alert contacts (email, SMS)

### Step 3: Configure Automated Backups

**Railway PostgreSQL** (already has automated backups):
- Backups run automatically
- Access via Railway dashboard
- Consider additional backup to S3 for critical data

### Step 4: Deploy to Production

**Backend (Railway)**:
```bash
# Make sure railway.toml exists (already in repo)
# Push to main branch triggers automatic deployment
git push origin main

# Or deploy manually
railway up
```

**Frontend (Vercel)**:
```bash
cd frontend
# Set environment variable in Vercel dashboard:
# VITE_API_URL = https://your-backend.up.railway.app

# Deploy
vercel --prod
```

### Step 5: Post-Deployment Smoke Tests

```bash
# Test health endpoint
curl https://your-backend.up.railway.app/api/health

# Test frontend loads
curl -I https://your-frontend.vercel.app

# Test authentication
curl -X POST https://your-backend.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Test database
curl https://your-backend.up.railway.app/api/trainers

# Test email (check logs)
# Test payment (use Stripe test cards)
```

---

## 🎉 Success Criteria

After completing this guide, you should have:

✅ **Functional Application**
- [ ] Backend accessible at Railway URL
- [ ] Frontend accessible at Vercel URL
- [ ] Database connected and migrated
- [ ] Authentication working
- [ ] API endpoints responding

✅ **Services Configured**
- [ ] Email sending successfully
- [ ] Payments processing (test mode)
- [ ] Error tracking active (Sentry)
- [ ] Uptime monitoring configured

✅ **Security Measures**
- [ ] HTTPS enforced
- [ ] Security headers present
- [ ] Rate limiting active
- [ ] Strong secrets configured
- [ ] CORS properly configured

✅ **Monitoring**
- [ ] Error tracking (Sentry)
- [ ] Uptime monitoring (UptimeRobot)
- [ ] Health check endpoint
- [ ] Logs accessible

---

## 🚨 Troubleshooting

### Backend Won't Start

```bash
# Check logs
railway logs

# Common issues:
# 1. Missing environment variables
# 2. Database connection failed
# 3. Python dependencies not installed

# Verify environment
railway vars
```

### Database Connection Failed

```bash
# Verify DATABASE_URL
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL

# Check Railway PostgreSQL service is running
railway status
```

### Email Not Sending

```bash
# Check SMTP settings
# Gmail requires App Password, not regular password
# Verify MAIL_USE_TLS=true

# Test with Python
python -c "from utils.email import send_email; print(send_email('test@example.com', 'Test', 'Test'))"
```

### Frontend Can't Connect to Backend

```bash
# Check CORS_ORIGINS in backend/.env includes your frontend URL
# Check VITE_API_URL in frontend/.env points to backend

# Test CORS
curl -H "Origin: https://your-frontend.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS https://your-backend.up.railway.app/api/health
```

---

## 📚 Next Steps

After completing deployment:

1. **Week 2**: Production hardening (see NEW_ROADMAP.md Phase 9.2)
   - Redis caching
   - Advanced monitoring
   - Performance optimization
   
2. **Week 3-4**: Implement Fitbit integration (see WEARABLE_INTEGRATIONS_ROADMAP.md)

3. **Week 5+**: Continue with roadmap phases

---

## 📞 Support

- **Documentation**: See `DEPLOYMENT_ASSESSMENT.md` for detailed analysis
- **Integrations**: See `WEARABLE_INTEGRATIONS_ROADMAP.md` for device integrations
- **Full Roadmap**: See `NEW_ROADMAP.md` for 12-week plan
- **Issues**: Open GitHub issue for bugs or questions

---

**Quick Reference Card** 📋

```bash
# Start development
docker-compose up

# Backend tests
cd backend && pytest

# Frontend build
cd frontend && npm run build

# Deploy backend
railway up

# Deploy frontend
cd frontend && vercel --prod

# Check health
curl https://your-backend.up.railway.app/api/health
```

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Estimated Time**: 5-7 days for complete setup
