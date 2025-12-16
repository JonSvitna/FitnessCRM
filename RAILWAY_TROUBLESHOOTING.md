# Railway Backend Boot Troubleshooting Guide

## Common Boot Issues & Solutions

### Issue 1: Application Fails to Start

**Symptoms:**
- Service shows "Crashed" or "Failed" status
- Logs show timeout or connection errors
- Build succeeds but deploy fails

**Solutions:**

#### A. Check Root Directory Configuration

**Option 1: Using railway.toml (Recommended)**
- Place `railway.toml` in the **repository root**
- Railway will automatically use it
- No manual Root Directory needed
- Current config uses: `cd backend && ...` in commands

**Option 2: Manual Root Directory**
- Go to Railway Dashboard → Your Service → Settings
- Find "Root Directory" field (it's a TEXT INPUT, not a dropdown)
- Type: `backend`
- Save and redeploy

**⚠️ Important:** Only use ONE method. If you set Root Directory manually, the `railway.toml` commands with `cd backend` will fail.

#### B. Verify Environment Variables

Required variables in Railway:
```env
# Required
DATABASE_URL=postgresql://...  (automatically added by Railway when you add Postgres)

# Required for production
FLASK_ENV=production

# Optional but recommended
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=https://your-frontend.vercel.app
PORT=8000  (Railway sets this automatically)
```

#### C. Check Database Connection

**Common Issue:** DATABASE_URL not set or incorrect

1. **Add Postgres to your Railway project:**
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway automatically sets `DATABASE_URL` variable

2. **Verify the variable:**
   ```bash
   # Railway automatically converts old format to new format in settings.py
   postgres://...  → postgresql://...
   ```

3. **Test database initialization:**
   - Check deployment logs for "Database tables created/verified"
   - If you see warnings, database connection might be failing

### Issue 2: Gunicorn Timeout

**Symptoms:**
- Logs show "Worker timeout"
- Service starts but crashes after 30s

**Solution:**
- Updated configuration now includes `--timeout 120`
- Also added `--workers 2` for better performance
- Logs now go to stdout/stderr with `--access-logfile -` and `--error-logfile -`

### Issue 3: Module Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'flask'
```

**Cause:** Dependencies not installed properly

**Solution:**
1. Check `requirements.txt` is in the correct location:
   - If Root Directory = "backend": `backend/requirements.txt`
   - If using railway.toml: `backend/requirements.txt`

2. Verify nixpacks is installing deps:
   - Check build logs for "pip install" commands
   - Should see all packages being installed

3. Force rebuild:
   - Railway Dashboard → Deployments → Click menu → "Redeploy"

### Issue 4: Port Binding Issues

**Symptoms:**
- "Address already in use"
- "Failed to bind to 0.0.0.0:8000"

**Solution:**
- Railway automatically sets `$PORT` variable
- Our Procfile uses: `--bind 0.0.0.0:$PORT`
- Make sure you're not hardcoding a port number

## Current Configuration Files

### ✅ railway.toml (root directory)
```toml
[build]
builder = "nixpacks"
watchPatterns = ["backend/**"]

[deploy]
startCommand = "cd backend && gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level info"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**Use when:** Deploying from repository root (recommended)

### ✅ backend/Procfile
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level info --access-logfile - --error-logfile -
```

**Use when:** Root Directory set to "backend" manually

### ✅ backend/nixpacks.toml
```toml
[phases.setup]
nixPkgs = ["python311", "postgresql"]

[phases.install]
cmds = ["pip install --no-cache-dir -r requirements.txt"]

[start]
cmd = "gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level info"
```

**Use when:** Root Directory set to "backend" manually

## Deployment Checklist

### Pre-Deploy
- [ ] Postgres database added to Railway project
- [ ] `DATABASE_URL` automatically set by Railway
- [ ] `FLASK_ENV=production` set in Railway variables
- [ ] Frontend `VITE_API_URL` set to full Railway backend URL
- [ ] `CORS_ORIGINS` includes your Vercel frontend URL

### During Deploy
- [ ] Check build logs for errors
- [ ] Verify pip packages install successfully
- [ ] Check for "Database tables created/verified" message
- [ ] No Python import errors

### Post-Deploy
- [ ] Service shows "Active" status (green)
- [ ] Test health endpoint: `curl https://your-app.railway.app/api/health`
- [ ] Check deployment logs for startup messages
- [ ] Test API from frontend

## Quick Diagnosis Commands

### Test Backend Locally
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL="postgresql://localhost/fitnesscrm"
export FLASK_ENV=development
python app.py
```

### Test Gunicorn Locally
```bash
cd backend
export PORT=8000
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level debug
```

### Check Railway Logs
1. Go to Railway Dashboard
2. Click your service
3. Click "Deployments" tab
4. Click on the latest deployment
5. View "Build Logs" and "Deploy Logs"

### Test Railway API
```bash
# Health check
curl https://your-backend.railway.app/api/health

# Root endpoint
curl https://your-backend.railway.app/

# Trainers endpoint
curl https://your-backend.railway.app/api/trainers
```

## If Nothing Works

### Nuclear Option: Fresh Deploy

1. **In Railway:**
   - Delete the current service (not the project)
   - Create new service from GitHub repo
   - Select your repository
   - **Don't set Root Directory manually**
   - Let railway.toml handle it

2. **Add Database:**
   - Click "New" → "Database" → "Add PostgreSQL"
   - Wait for DATABASE_URL to be set

3. **Set Variables:**
   ```env
   FLASK_ENV=production
   SECRET_KEY=your-secret-key
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```

4. **Deploy:**
   - Should automatically deploy
   - Watch logs carefully

## Understanding the File Structure

```
FitnessCRM/
├── railway.toml              ← Railway reads this FIRST (if at root)
└── backend/
    ├── Procfile              ← Railway reads this if Root Directory="backend"
    ├── nixpacks.toml         ← Nixpacks reads this if Root Directory="backend"
    ├── requirements.txt      ← Python dependencies
    ├── runtime.txt           ← Python version (3.11.0)
    └── app.py                ← Main Flask application
```

**Key Point:** railway.toml at root uses `cd backend` in commands, so it works from repository root.

## Getting Help

If you're still stuck, gather this information:

1. **Railway deployment logs** (both build and deploy)
2. **Environment variables** (hide sensitive values)
3. **Root Directory** setting (if any)
4. **Error messages** from logs
5. **Service status** (crashed, failed, active)

Common log locations in Railway Dashboard:
- Build Logs: Shows pip install, dependency installation
- Deploy Logs: Shows gunicorn startup, database connection
- Service Logs: Shows runtime errors and requests
