# FitnessCRM Deployment Guide 🚀

**Complete guide for deploying FitnessCRM to production**  
**Last Updated**: December 2024

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
4. [Backend Deployment (Railway)](#backend-deployment-railway)
5. [Database Setup](#database-setup)
6. [Environment Configuration](#environment-configuration)
7. [Docker Deployment](#docker-deployment)
8. [Post-Deployment](#post-deployment)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Option 1: Vercel + Railway (Recommended for Quick Deployment)

```bash
# 1. Deploy frontend to Vercel
cd frontend
vercel --prod

# 2. Deploy backend to Railway
railway up

# 3. Configure environment variables (see Environment Configuration section)
```

### Option 2: Docker Compose (Production)

```bash
# 1. Configure environment
cp .env.example .env
nano .env

# 2. Start services
docker-compose -f docker-compose.prod.yml up -d

# 3. Initialize database
docker-compose exec backend python init_db.py
```

---

## Prerequisites

### Required
- GitHub account
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 15+ (or Railway PostgreSQL)

### For Cloud Deployment
- Vercel account (free tier available)
- Railway account (free tier with $5 credit)

### For Docker Deployment
- Docker and Docker Compose installed
- Domain name (optional, for SSL)

---

## Frontend Deployment (Vercel)

### Step 1: Connect Repository

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Select the FitnessCRM repository

### Step 2: Configure Project

- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build` (auto-detected)
- **Output Directory**: `dist` (auto-detected)

### Step 3: Environment Variables

Add to Vercel project settings:

```
VITE_API_URL=https://your-railway-backend.up.railway.app
```

### Step 4: Deploy

1. Click "Deploy"
2. Wait for build to complete
3. Access at `https://your-project.vercel.app`

### Automatic Deployments

- **Production**: Pushes to `main` branch
- **Preview**: Pull requests and other branches

### Troubleshooting Vercel Deployment

**Issue: Build fails with "Module not found"**
- Solution: Verify `package.json` includes all dependencies
- Run `npm install` locally to test

**Issue: Environment variables not working**
- Solution: Redeploy after adding variables (they're only applied on new deployments)

**Issue: 404 on page refresh**
- Solution: Already configured in `vercel.json` with rewrite rules

---

## Backend Deployment (Railway)

### Method 1: Automatic Configuration (Recommended)

This repository includes `railway.toml` in the root for automatic configuration.

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway automatically uses `railway.toml` configuration

### Method 2: Manual Configuration

If automatic configuration doesn't work:

1. Create new Railway project
2. Deploy from GitHub
3. **Set Root Directory** in service settings:
   - Find "Root Directory" field (text input, not dropdown)
   - Type `backend` and press Enter
4. Railway will use `backend/Procfile` and `backend/nixpacks.toml`

### Configuration Files

**`railway.toml`** (repository root):
```toml
[build]
builder = "NIXPACKS"

[build.nixpacks]
nixpkgsVersion = "23.05"

[deploy]
startCommand = "cd backend && gunicorn app:app"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**`backend/nixpacks.toml`**:
```toml
[phases.setup]
nixPkgs = ["python311", "postgresql"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "gunicorn app:app --bind 0.0.0.0:$PORT"
```

### Add PostgreSQL Database

1. In Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway auto-configures `DATABASE_URL` environment variable

### Environment Variables

Set in Railway dashboard:

```
DATABASE_URL=<automatically set by Railway>
SECRET_KEY=<generate secure key>
FLASK_ENV=production
PORT=5000
CORS_ORIGINS=https://your-frontend.vercel.app
```

### Troubleshooting Railway Deployment

**Issue: "Root Directory not found" error**
- **Solution**: Type `backend` in Root Directory field (it's a text input, not dropdown)
- Verify `railway.toml` is in repository root

**Issue: Build fails with Python errors**
- **Solution**: Check `backend/nixpacks.toml` specifies Python 3.11
- Verify `requirements.txt` is in backend directory

**Issue: Database connection fails**
- **Solution**: Ensure PostgreSQL service is running
- Check `DATABASE_URL` is set correctly
- Railway format: `postgresql://user:pass@host:port/dbname`

**Issue: Application crashes on start**
- **Solution**: Check Railway logs for errors
- Verify `Procfile` or start command is correct: `gunicorn app:app`
- Ensure all dependencies in `requirements.txt`

**Issue: Port binding errors**
- **Solution**: Use `$PORT` environment variable (Railway assigns dynamically)
- In code: `app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))`

---

## Database Setup

### Railway PostgreSQL (Automatic)

Railway provisions database automatically:
- `DATABASE_URL` is auto-configured
- No manual setup required

### Manual PostgreSQL Setup

```bash
# Create database
createdb fitnesscrm

# Set DATABASE_URL
export DATABASE_URL=postgresql://user:password@localhost:5432/fitnesscrm

# Initialize database
cd backend
python init_db.py

# Optional: Seed with sample data
python init_db.py seed
```

### Database Migrations

```bash
# Run migrations
cd backend
python init_db.py

# Verify tables created
psql $DATABASE_URL -c "\dt"
```

---

## Environment Configuration

### Backend Environment Variables

Create `backend/.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Security
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
JWT_SECRET=<generate another secure key>

# Flask
FLASK_ENV=production
PORT=5000

# CORS
CORS_ORIGINS=https://your-frontend.vercel.app,https://yourdomain.com

# Email (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=<gmail app password>
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Twilio (Optional)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Stripe (Optional)
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=

# Redis (Optional, for caching)
REDIS_URL=redis://localhost:6379
```

### Frontend Environment Variables

Create `frontend/.env`:

```env
# Backend API URL
VITE_API_URL=https://your-backend.up.railway.app

# Environment
VITE_ENV=production
```

### Generate Secure Keys

```bash
# Generate SECRET_KEY and JWT_SECRET
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Gmail App Password Setup

1. Enable 2-Factor Authentication on Gmail
2. Go to: Google Account → Security → 2-Step Verification → App passwords
3. Generate password for "Mail"
4. Use in `MAIL_PASSWORD`

---

## Docker Deployment

### Production Docker Compose

Create `.env` file:

```env
# Database
POSTGRES_DB=fitnesscrm_prod
POSTGRES_USER=fitnesscrm_user
POSTGRES_PASSWORD=<secure password>

# Redis
REDIS_PASSWORD=<secure password>

# Application
SECRET_KEY=<secure key>
VITE_API_URL=http://your-domain.com

# Optional
SENTRY_DSN=
```

### Start Services

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Initialize Database

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python init_db.py

# Seed sample data (optional)
docker-compose -f docker-compose.prod.yml exec backend python seed_accounts.py
```

### SSL/TLS Setup with Nginx

The production Docker setup includes Nginx reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://frontend:3000;
    }
    
    location /api {
        proxy_pass http://backend:5000;
    }
}
```

For Let's Encrypt SSL:

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Generate certificate
certbot --nginx -d your-domain.com
```

---

## Post-Deployment

### Verification Checklist

- [ ] Frontend accessible at production URL
- [ ] Backend API responding (`/api/health` endpoint)
- [ ] Database connected and tables created
- [ ] Authentication working
- [ ] CORS configured correctly
- [ ] Email sending functional (if configured)
- [ ] All environment variables set

### Test API Endpoints

```bash
# Health check
curl https://your-backend.up.railway.app/api/health

# List trainers (should return JSON)
curl https://your-backend.up.railway.app/api/trainers
```

### Monitoring Setup

**Railway Monitoring**:
- View logs in Railway dashboard
- Set up deployment notifications

**Sentry Error Tracking** (Optional):
```bash
# Install Sentry
pip install sentry-sdk[flask]

# Add to backend/app.py
import sentry_sdk
sentry_sdk.init(dsn="YOUR_SENTRY_DSN")
```

### Backup Strategy

**Database Backups**:
```bash
# Manual backup
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

**Railway Automatic Backups**:
- Enable in PostgreSQL service settings
- Configure backup schedule

---

## Troubleshooting

### Common Issues

**CORS Errors**
- Check `CORS_ORIGINS` includes your frontend URL
- Verify no trailing slashes in URLs
- Check browser console for specific CORS errors

**Database Connection Issues**
- Verify `DATABASE_URL` format
- Check database service is running
- Test connection: `psql $DATABASE_URL`

**Build Failures**
- Review build logs carefully
- Check all dependencies listed in requirements/package files
- Verify Python/Node versions match requirements

**Environment Variable Issues**
- Variables only apply to new deployments
- Redeploy after changing variables
- Check variable names match code expectations

**502/503 Errors**
- Backend service may not be running
- Check Railway logs for startup errors
- Verify gunicorn command is correct

### Getting Help

1. Check application logs first
2. Review relevant troubleshooting section above
3. Check Railway/Vercel status pages
4. Open GitHub issue with:
   - Error messages
   - Deployment platform
   - Steps to reproduce
   - Logs (remove sensitive data)

---

## Additional Resources

- **MANUAL.md** - Comprehensive application documentation
- **API_DOCUMENTATION.md** - Complete API reference
- **TESTING_GUIDE.md** - Testing procedures
- **README.md** - Project overview

---

**Deployment Summary**:
- Frontend: Vercel (automatic deploys from GitHub)
- Backend: Railway (with PostgreSQL database)
- Alternative: Docker Compose for self-hosted deployment
