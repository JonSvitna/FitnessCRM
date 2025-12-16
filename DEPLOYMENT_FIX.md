# 🔧 Deployment Configuration Fix

## Current Issue
Your frontend on Vercel is making API requests to malformed URLs:
```
❌ https://fitness-ekirbp658-jonsvitnas-projects.vercel.app/backend-production-2078.up.railway.app/api/...
```

Should be:
```
✅ https://backend-production-2078.up.railway.app/api/...
```

## Root Cause
The `VITE_API_URL` environment variable in Vercel is set to a relative path instead of a full URL.

---

## Fix Steps

### 1. Fix Vercel Frontend Configuration

1. **Go to Vercel Dashboard**
   - Navigate to your project: https://vercel.com/jonsvitnas-projects/fitness-ekirbp658
   
2. **Update Environment Variable**
   - Go to: Settings → Environment Variables
   - Find or add: `VITE_API_URL`
   - Set value to: `https://backend-production-2078.up.railway.app`
   - ⚠️ **Important**: 
     - Use the FULL URL (including `https://`)
     - NO trailing slash
     - Only the backend domain, not a path
   
3. **Redeploy**
   - Go to: Deployments tab
   - Click on the latest deployment
   - Click "Redeploy" button
   - Or push a new commit to trigger automatic deployment

### 2. Add CORS Configuration to Railway Backend

1. **Go to Railway Dashboard**
   - Navigate to your backend service
   
2. **Add Environment Variable**
   - Go to: Variables tab
   - Add new variable:
     ```
     Name:  CORS_ORIGINS
     Value: https://fitness-ekirbp658-jonsvitnas-projects.vercel.app,http://localhost:5173
     ```
   - ⚠️ **Important**: Use your actual Vercel domain (from the screenshot)
   
3. **Restart Service**
   - Railway will automatically restart after adding the variable
   - Or manually restart from the deployment tab

---

## Verification Checklist

After redeploying both services:

### ✅ Check Frontend
1. Open browser DevTools (F12)
2. Go to Network tab
3. Visit your Vercel URL
4. API requests should go to: `https://backend-production-2078.up.railway.app/api/...`

### ✅ Check Backend
1. Test API directly:
   ```bash
   curl https://backend-production-2078.up.railway.app/api/health
   ```
   Should return:
   ```json
   {
     "status": "healthy",
     "message": "API is running"
   }
   ```

### ✅ Check CORS
1. Visit Vercel frontend
2. Try creating a trainer or client
3. Should see success messages, not CORS errors

---

## Quick Reference

### Current URLs (from screenshot)
- **Vercel Frontend**: `https://fitness-ekirbp658-jonsvitnas-projects.vercel.app`
- **Railway Backend**: `https://backend-production-2078.up.railway.app`

### Environment Variables Summary

**Vercel** (frontend):
```env
VITE_API_URL=https://backend-production-2078.up.railway.app
```

**Railway** (backend):
```env
CORS_ORIGINS=https://fitness-ekirbp658-jonsvitnas-projects.vercel.app,http://localhost:5173
DATABASE_URL=<auto-set-by-railway>
SECRET_KEY=<your-secret-key>
FLASK_ENV=production
```

---

## Common Mistakes to Avoid

❌ **Don't use relative paths for VITE_API_URL**:
```
backend-production-2078.up.railway.app          # Missing https://
/backend-production-2078.up.railway.app/        # Wrong format
```

✅ **Use full URL**:
```
https://backend-production-2078.up.railway.app
```

❌ **Don't add trailing slashes**:
```
https://backend-production-2078.up.railway.app/  # Extra slash
```

✅ **No trailing slash**:
```
https://backend-production-2078.up.railway.app
```

---

## If Issues Persist

1. **Clear browser cache** and hard refresh (Ctrl+Shift+R)
2. **Check Railway logs** for backend errors
3. **Check Vercel logs** for build/runtime errors
4. **Verify environment variables** are saved correctly
5. **Ensure services are running** (green status in Railway/Vercel)

---

## Additional Resources

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Full deployment guide
- [RAILWAY_SETUP.md](./RAILWAY_SETUP.md) - Railway-specific setup
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - API endpoints reference
