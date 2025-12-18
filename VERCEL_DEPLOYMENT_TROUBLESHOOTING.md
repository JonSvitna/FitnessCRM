# Vercel Deployment Troubleshooting Guide

## Issue: Changes Not Appearing in Vercel

If you've pushed changes to git but don't see them in Vercel, follow these steps:

## Step 1: Check Vercel Deployment Status

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/dashboard
   - Find your FitnessCRM project

2. **Check Latest Deployment**
   - Go to "Deployments" tab
   - Check the latest deployment status
   - Look for:
     - ✅ Success (green) - Deployment completed
     - ⏳ Building - Still in progress
     - ❌ Error (red) - Build failed

## Step 2: Verify Git Integration

1. **Check if Vercel is connected to GitHub**
   - Go to: Settings → Git
   - Verify repository is connected
   - Check if "Production Branch" is set to `main`

2. **Check if auto-deploy is enabled**
   - Settings → Git → Production Branch
   - Should be: `main` with "Automatic Deployments" enabled

## Step 3: Manual Redeploy

If automatic deployment didn't trigger:

### Option A: Redeploy from Vercel Dashboard

1. Go to "Deployments" tab
2. Click on the latest deployment
3. Click "Redeploy" button (three dots menu)
4. Select "Redeploy" option
5. Wait for build to complete

### Option B: Trigger via Git Push

```bash
# Make a small change to trigger deployment
echo "# Trigger deployment" >> README.md
git add README.md
git commit -m "Trigger Vercel deployment"
git push origin main
```

## Step 4: Check Build Logs

If deployment failed:

1. Click on the failed deployment
2. View "Build Logs"
3. Look for errors such as:
   - Missing dependencies
   - Build command failures
   - Environment variable issues

## Step 5: Verify Build Configuration

Check that Vercel settings match:

**Settings → General → Build & Development Settings:**

- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

## Step 6: Check Environment Variables

1. Go to: Settings → Environment Variables
2. Verify `VITE_API_URL` is set correctly:
   ```
   VITE_API_URL=https://your-backend.up.railway.app
   ```
3. Make sure it's set for **Production** environment
4. After updating, **redeploy** the project

## Step 7: Clear Cache and Redeploy

If changes still don't appear:

1. **Clear Vercel Cache**
   - Go to: Settings → General
   - Scroll to "Clear Build Cache"
   - Click "Clear Build Cache"
   - Redeploy

2. **Hard Refresh Browser**
   - Press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
   - Or clear browser cache

## Step 8: Verify Files Are Built

Check that new files are included in build:

1. **Check Build Output**
   - In deployment logs, look for:
     ```
     ✓ built in Xs
     dist/index.html
     dist/assets/...
     ```

2. **Verify New Files**
   - Check if new JS files are in `dist/assets/`
   - Example: `dist/assets/dark-mode-xxxx.js`

## Common Issues

### Issue: Build Succeeds but Changes Don't Appear

**Solution**: 
- Clear browser cache
- Hard refresh (Ctrl+Shift+R)
- Check if service worker is caching old version
- Disable service worker in DevTools → Application → Service Workers

### Issue: Build Fails with Module Not Found

**Solution**:
- Check `package.json` has all dependencies
- Run `npm install` locally to verify
- Check if new imports are correct

### Issue: Environment Variables Not Working

**Solution**:
- Verify variable name starts with `VITE_`
- Redeploy after adding/changing variables
- Check variable is set for correct environment (Production/Preview)

### Issue: API Calls Failing

**Solution**:
- Verify `VITE_API_URL` is set correctly
- Check backend is running and accessible
- Check CORS settings on backend
- Verify API endpoints exist

## Quick Fix Checklist

- [ ] Latest commit pushed to `main` branch
- [ ] Vercel deployment shows "Building" or "Ready"
- [ ] Build logs show no errors
- [ ] Environment variables are set correctly
- [ ] Browser cache cleared
- [ ] Service worker disabled/updated
- [ ] Hard refresh attempted

## Force Redeploy Command

If nothing else works, trigger a redeploy:

```bash
# Add empty commit to trigger deployment
git commit --allow-empty -m "Trigger Vercel redeploy"
git push origin main
```

## Still Not Working?

1. **Check Vercel Status**: https://www.vercel-status.com/
2. **Review Build Logs**: Look for specific error messages
3. **Test Locally**: Run `npm run build` locally to catch errors
4. **Check Dependencies**: Verify all packages are in `package.json`

## Testing Locally Before Deploy

```bash
cd frontend
npm install
npm run build
npm run preview
```

This will build and preview locally, helping identify issues before deploying.

