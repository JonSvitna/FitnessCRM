# FitnessCRM Backend

This directory contains the Flask backend API for FitnessCRM.

## Railway Deployment

When deploying to Railway:

1. Create a new service from your GitHub repository
2. In Railway's service settings, find the **"Root Directory"** field
3. Type `backend` in the Root Directory field (this is a text input, not a dropdown)
4. Railway will then use the configuration from:
   - `../railway.toml` (repository root)
   - `nixpacks.toml` (this directory)
   - `Procfile` (this directory)
   - `requirements.txt` (this directory)

### Why "backend" is not shown as an option

Railway's Root Directory field is a manual text input. You need to type the directory name yourself. This is by design to support any arbitrary directory structure.

## Files

- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `Procfile` - Railway start command
- `runtime.txt` - Python version
- `nixpacks.toml` - Nixpacks build configuration
- `models/` - Database models
- `api/` - API routes
- `config/` - Configuration files
- `utils/` - Utility functions

## Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run the application
python app.py
```

## Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask secret key
- `FLASK_ENV` - Set to "production" for deployment

Optional:
- `PORT` - Server port (default: 5000)
