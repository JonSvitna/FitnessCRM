# Railway Deployment - Step by Step

## Your Current Problem: Backend Won't Boot

### Most Likely Causes:
1. ❌ Root Directory not set correctly (or conflicts with railway.toml)
2. ❌ DATABASE_URL environment variable missing
3. ❌ Worker timeout (fixed in latest config)
4. ❌ Build vs Deploy directory mismatch

---

## Solution 1: Clean Deploy (Recommended)

### Step 1: Delete Current Service
1. Go to Railway Dashboard
2. Find your backend service
3. Click Settings → Danger Zone → "Remove Service"
4. Confirm deletion

### Step 2: Create New Service  
1. Click "New" → "GitHub Repo"
2. Select `FitnessCRM` repository
3. **DO NOT set Root Directory** - leave it empty!
4. Railway will read `railway.toml` automatically

### Step 3: Add PostgreSQL Database
1. Click "New" → "Database" → "Add PostgreSQL"
2. Wait for it to provision (~30 seconds)
3. Railway automatically links it and sets `DATABASE_URL`

### Step 4: Add Environment Variables
1. Click on your backend service
2. Go to "Variables" tab
3. Add these variables:

```env
# Required
FLASK_ENV=production

# Recommended
SECRET_KEY=generate-a-random-secret-key-here

# Required for frontend
CORS_ORIGINS=https://fitness-ekirbp658-jonsvitnas-projects.vercel.app
```

**To generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 5: Deploy
1. Service should auto-deploy after adding variables
2. Watch the deployment logs
3. Look for these success messages:
   - ✅ "pip install" commands succeed
   - ✅ "Database tables created/verified"
   - ✅ "Booting worker with pid"
   - ✅ Service status turns green

### Step 6: Get Your Railway URL
1. In Railway dashboard, click your service
2. Go to "Settings" → "Networking"
3. Click "Generate Domain"
4. Copy the URL (e.g., `https://backend-production-xxxx.up.railway.app`)

### Step 7: Update Vercel Frontend
1. Go to Vercel Dashboard
2. Your project → Settings → Environment Variables
3. Update `VITE_API_URL` to your Railway URL:
   ```
   https://backend-production-xxxx.up.railway.app
   ```
4. Redeploy frontend

---

## Solution 2: Fix Existing Deployment

If you don't want to delete and recreate:

### Check 1: Root Directory Setting
1. Railway Dashboard → Your Service → Settings
2. Find "Root Directory"
3. **Choose ONE:**
   - **Option A:** Leave it EMPTY (recommended) - uses railway.toml
   - **Option B:** Set it to `backend` - uses backend/Procfile

**⚠️ IMPORTANT:** If you have Root Directory set to `backend`, the railway.toml commands with `cd backend` will fail!

### Check 2: Database Connection
1. Verify PostgreSQL service exists in your project
2. Check Variables tab for `DATABASE_URL`
3. Should look like: `postgresql://postgres:password@...`
4. If missing, click "New" → "Database" → "Add PostgreSQL"

### Check 3: Environment Variables
Required variables:
```env
DATABASE_URL=postgresql://...  # Automatic from Postgres
FLASK_ENV=production
SECRET_KEY=your-secret-key
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

### Check 4: Force Rebuild
1. Go to "Deployments" tab
2. Click on failed deployment
3. Click "View Logs" to see error
4. Click ⋮ menu → "Redeploy"

---

## Verifying Success

### 1. Check Railway Logs
```
Build Logs should show:
✅ Successfully installed Flask-3.0.0 ...
✅ Build completed

Deploy Logs should show:
✅ Database tables created/verified
✅ [INFO] Starting gunicorn 21.2.0
✅ [INFO] Listening at: http://0.0.0.0:8000
✅ [INFO] Using worker: sync
✅ [INFO] Booting worker with pid: ...
```

### 2. Test API Directly
```bash
# Replace with your actual Railway URL
export RAILWAY_URL="https://backend-production-xxxx.up.railway.app"

# Health check
curl $RAILWAY_URL/api/health
# Expected: {"status":"healthy","message":"API is running"}

# Root endpoint
curl $RAILWAY_URL/
# Expected: {"message":"Fitness CRM API","version":"1.0.0",...}

# Test CORS (from browser console on your Vercel site)
fetch('https://backend-production-xxxx.up.railway.app/api/health')
  .then(r => r.json())
  .then(console.log)
# Should work without CORS errors
```

### 3. Check Frontend Integration
1. Open your Vercel app
2. Open browser DevTools (F12) → Network tab
3. Try creating a trainer
4. Check Network tab:
   - Request URL should be: `https://backend-production-xxxx.up.railway.app/api/trainers`
   - Status should be: `201 Created` or `200 OK`
   - No CORS errors in console

---

## Common Errors & Fixes

### Error: "Worker timeout"
**Solution:** Already fixed in latest configs
- Increased timeout to 120 seconds
- Added proper logging flags

### Error: "Address already in use"
**Cause:** Port hardcoded instead of using $PORT
**Solution:** Already fixed - using `$PORT` variable

### Error: "ModuleNotFoundError: No module named 'flask'"
**Cause:** Dependencies not installed
**Solution:**
1. Check Root Directory setting
2. Verify `requirements.txt` location
3. Force rebuild

### Error: "Database connection failed"
**Cause:** No DATABASE_URL or wrong format
**Solution:**
1. Add PostgreSQL to project
2. Check DATABASE_URL in variables
3. Our code auto-fixes `postgres://` → `postgresql://`

### Error: "CORS policy" in browser
**Cause:** Backend not allowing frontend origin
**Solution:**
1. Add `CORS_ORIGINS` variable in Railway
2. Set to your Vercel URL
3. Redeploy backend

---

## Configuration Summary

### Files That Control Deployment

**If Root Directory is EMPTY (recommended):**
- Uses: `/railway.toml`
- Commands: `cd backend && ...`
- Start: `cd backend && gunicorn app:app ...`

**If Root Directory = "backend":**
- Uses: `/backend/nixpacks.toml` OR `/backend/Procfile`
- Commands: Run from `backend/` directory
- Start: `gunicorn app:app ...`

**Current Configuration Works With:** Empty Root Directory (uses railway.toml)

---

## Quick Reference

### Your URLs
```
Frontend (Vercel): https://fitness-ekirbp658-jonsvitnas-projects.vercel.app
Backend (Railway):  https://backend-production-xxxx.up.railway.app
```

### Required Environment Variables

**Railway (Backend):**
```env
DATABASE_URL=postgresql://...  # Auto-set by Railway Postgres
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=https://fitness-ekirbp658-jonsvitnas-projects.vercel.app
```

**Vercel (Frontend):**
```env
VITE_API_URL=https://backend-production-xxxx.up.railway.app
```

### Port Configuration
```bash
# Railway automatically sets $PORT
# Our configs use: --bind 0.0.0.0:$PORT
# Don't hardcode port numbers!
```

---

## Need More Help?

### Information to Provide:
1. Railway deployment logs (Build + Deploy)
2. Current Root Directory setting
3. Environment variables (hide sensitive values)
4. Specific error message
5. Service status (crashed/failed/active)

### Where to Find Logs:
1. Railway Dashboard
2. Click your service
3. "Deployments" tab
4. Click latest deployment
5. View "Build Logs" and "Deploy Logs"
