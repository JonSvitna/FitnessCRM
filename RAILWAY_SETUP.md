# Railway Setup Guide

This guide specifically addresses the "Root Directory" configuration question for Railway deployment.

## Quick Answer

**Question**: "I don't see backend or frontend option within the Railway root directory options"

**Answer**: Railway's "Root Directory" field is a **text input**, not a dropdown menu. You need to manually type `backend` in the field.

## Two Ways to Deploy

### Method 1: Automatic Configuration (Recommended)

With the included `railway.toml` file:

1. Create a new project in Railway
2. Connect your GitHub repository
3. **That's it!** Railway automatically reads `railway.toml` and configures everything

No manual Root Directory configuration needed.

### Method 2: Manual Root Directory Configuration

If you prefer manual configuration or Method 1 doesn't work:

1. Create a new project in Railway
2. Connect your GitHub repository
3. Go to service Settings → "Root Directory"
4. Click on the empty text field
5. Type: `backend`
6. Press Enter or click away to save

## Understanding Railway's Root Directory Field

### What It Looks Like

```
┌─────────────────────────────────┐
│ Root Directory                  │
├─────────────────────────────────┤
│ [                       ]       │ ← This is a TEXT INPUT field
│                                 │    Not a dropdown!
│ Type the directory path here    │
└─────────────────────────────────┘
```

### Common Misconception

❌ **Wrong**: "Railway should show me a dropdown with backend/frontend options"
✅ **Correct**: "Railway provides a text field where I type the directory name"

### Why It's a Text Field

Railway supports any directory structure. You might have:
- `backend/`
- `api/`
- `server/`
- `services/api/`
- `apps/main/`

Rather than try to guess which directories contain deployable code, Railway lets you specify the exact path as text.

## Repository Structure

```
FitnessCRM/
├── railway.toml          ← Railway configuration (automatic)
├── frontend/             ← Frontend code (deploy to Vercel)
│   ├── package.json
│   └── ...
└── backend/              ← Backend code (deploy to Railway)
    ├── Procfile
    ├── requirements.txt
    ├── nixpacks.toml
    ├── app.py
    └── ...
```

## Configuration Files

### `railway.toml` (Root)

Tells Railway:
- Use Nixpacks builder
- Build from `backend/` directory
- Run `gunicorn app:app` to start the server

### `backend/nixpacks.toml`

Tells Nixpacks:
- Use Python 3.11
- Install dependencies with pip
- Start with gunicorn

### `backend/Procfile`

Alternative to railway.toml, tells Railway:
- Start command: `gunicorn app:app`

## Troubleshooting

### "I typed 'backend' but it's not working"

Check:
1. Did you press Enter after typing?
2. Is the spelling correct? (case-sensitive)
3. Try clicking "Deploy" again

### "Railway says it can't find requirements.txt"

This means Root Directory isn't set correctly:
1. Go to Settings
2. Find "Root Directory" field
3. Clear it and type `backend` again
4. Save and redeploy

### "Should I use railway.toml or set Root Directory?"

**Best practice**: Use both!
- `railway.toml` provides automatic configuration
- Manually set Root Directory as backup if automatic config doesn't work

### "Can I deploy frontend to Railway too?"

You can, but:
- Frontend is designed for Vercel (optimized for static sites)
- Backend is designed for Railway (optimized for Python apps)
- Deploying both separately is the recommended architecture

## Step-by-Step with Screenshots

### Step 1: Create Project
- Go to railway.app
- Click "New Project"
- Select "Deploy from GitHub repo"

### Step 2: Select Repository
- Choose `FitnessCRM` repository
- Railway will start analyzing it

### Step 3: Configuration (if needed)
If Railway doesn't auto-detect the configuration:
1. Click on the service
2. Go to "Settings" tab
3. Scroll to "Root Directory"
4. Click the empty text field
5. Type: `backend`
6. Press Enter

### Step 4: Add Database
1. Click "New" in your project
2. Select "Database" → "PostgreSQL"
3. Railway provisions database and sets DATABASE_URL

### Step 5: Set Environment Variables
1. Go to service "Variables" tab
2. Add:
   - `FLASK_ENV=production`
   - `SECRET_KEY=your-secret-key-here`

### Step 6: Deploy
1. Railway automatically deploys
2. Once complete, click "Generate Domain" in Settings
3. Use this URL as VITE_API_URL in your Vercel frontend

## Need More Help?

- Full deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- Railway docs: [docs.railway.app](https://docs.railway.app)
- Open an issue on GitHub
