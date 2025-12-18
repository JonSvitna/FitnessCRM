# PWA Console Errors - Fix Summary

## Issues Identified

1. **401 Unauthorized** for `manifest.json` - File not being served correctly
2. **404 Not Found** for `sw.js` - Service worker file not found
3. **Service Worker registration failed** - Due to missing sw.js file

## Root Cause

The `manifest.json` and `sw.js` files were in the root `frontend/` directory, but Vite only automatically copies files from the `public/` directory to the build output (`dist/`). When deployed to Vercel, these files weren't available at the expected paths.

## Fixes Applied

### 1. Moved PWA Files to Public Directory ✅
- Created `frontend/public/` directory
- Moved `manifest.json` to `frontend/public/manifest.json`
- Moved `sw.js` to `frontend/public/sw.js`

**Why**: Vite automatically copies all files from `public/` to the root of `dist/` during build, making them available at `/manifest.json` and `/sw.js` in production.

### 2. Updated Vercel Configuration ✅
Added proper headers in `vercel.json`:
- **manifest.json**: 
  - Content-Type: `application/manifest+json`
  - Cache-Control: `public, max-age=3600`
- **sw.js**:
  - Content-Type: `application/javascript`
  - Service-Worker-Allowed: `/`
  - Cache-Control: `no-cache`

**Why**: Ensures Vercel serves these files with correct MIME types and caching headers, and allows the service worker to control the entire site.

### 3. Added Manifest Link to Landing Page ✅
- Added `<link rel="manifest" href="/manifest.json">` to `home.html`

**Why**: Ensures PWA manifest is available on all pages.

## Files Modified

1. `frontend/public/manifest.json` (moved from root)
2. `frontend/public/sw.js` (moved from root)
3. `frontend/vercel.json` (added headers)
4. `frontend/home.html` (added manifest link)

## Next Steps

1. **Rebuild and Redeploy**:
   ```bash
   cd frontend
   npm run build
   ```
   Then push to trigger Vercel deployment.

2. **Verify After Deployment**:
   - Check browser console - errors should be gone
   - Verify `/manifest.json` returns 200 (not 401)
   - Verify `/sw.js` returns 200 (not 404)
   - Service worker should register successfully

3. **Test PWA Features**:
   - Service worker should cache assets
   - Offline functionality should work
   - Install prompt should appear (if configured)

## Notes

- The 401 error was likely due to Vercel's routing not finding the file
- The 404 error was because the file wasn't in the build output
- Files in `public/` are copied as-is (no hashing) to maintain consistent paths
- Service worker must be served from root (`/sw.js`) to control the entire site

