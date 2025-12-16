# Deployment Guide 🚀

This guide covers deploying the Fitness CRM application with frontend on Vercel and backend on Railway.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Railway Configuration Files](#railway-configuration-files)
- [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
- [Backend Deployment (Railway)](#backend-deployment-railway)
- [Database Setup (Railway PostgreSQL)](#database-setup-railway-postgresql)
- [Environment Variables](#environment-variables)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- GitHub account
- Vercel account (free tier available)
- Railway account (free tier available with $5 credit)
- Your code pushed to a GitHub repository

## Railway Configuration Files

This repository includes Railway configuration files to simplify deployment:

### `railway.toml` (Repository Root)
Located at the root of the repository, this file configures the backend service deployment:
- Specifies Nixpacks as the builder
- Points to the backend directory for build and deployment
- Defines the start command and restart policy

### `backend/nixpacks.toml`
Located in the backend directory, this file configures the Python environment:
- Specifies Python 3.11 and PostgreSQL packages
- Defines installation commands for dependencies
- Sets the gunicorn start command

**How Railway Uses These Files**:
1. When you deploy from the repository root, Railway reads `railway.toml`
2. The configuration automatically points to the backend directory
3. Nixpacks uses `backend/nixpacks.toml` to set up the Python environment
4. **No manual Root Directory configuration needed** with `railway.toml`

**Alternative Manual Configuration**:
If you prefer to set the Root Directory manually or if automatic configuration doesn't work:
- Find the "Root Directory" field in Railway's service settings
- This is a **text input field**, not a dropdown menu
- Type `backend` and press Enter
- Railway will then use `backend/Procfile` and `backend/nixpacks.toml`

**Common Question**: "Why don't I see backend/frontend as dropdown options?"
- Railway's Root Directory field accepts any text path
- It doesn't pre-populate with directory names
- You must manually type the directory name (e.g., `backend`)

## Frontend Deployment (Vercel)

### Step 1: Connect Repository

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Select the repository containing FitnessCRM

### Step 2: Configure Project

1. **Framework Preset**: Vite
2. **Root Directory**: `frontend`
3. **Build Command**: `npm run build` (auto-detected)
4. **Output Directory**: `dist` (auto-detected)

### Step 3: Environment Variables

Add the following environment variable:

```
VITE_API_URL=https://your-railway-backend.up.railway.app
```

**Note**: You'll need to deploy the backend first to get this URL, or update it after backend deployment.

### Step 4: Deploy

1. Click "Deploy"
2. Wait for the build to complete
3. Your frontend will be available at `https://your-project.vercel.app`

### Automatic Deployments

Vercel automatically deploys:
- **Production**: Pushes to `main` branch
- **Preview**: Pull requests and other branches

## Backend Deployment (Railway)

### Step 1: Create New Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

### Step 2: Configure Service

You have TWO options for configuring the backend service:

#### Option A: Automatic Configuration (Recommended)

The repository includes a `railway.toml` file at the root that automatically configures the backend deployment. **No manual configuration needed!**

- Railway will automatically detect and use `railway.toml`
- Builds and runs from the `backend/` directory automatically
- Start command is pre-configured

Simply proceed to Step 3 after creating the project.

#### Option B: Manual Root Directory Configuration

If Option A doesn't work or you prefer manual configuration:

1. **Root Directory**: 
   - In Railway's service settings, find the "Root Directory" field
   - **IMPORTANT**: This is a text input field, not a dropdown menu
   - Type: `backend` (exactly as shown)
   - Press Enter or click away to save
   
   **Why you don't see dropdown options**: Railway's Root Directory field accepts any path as text. The directories "backend" and "frontend" aren't shown as pre-populated options - you must type the directory name yourself.

2. **Start Command**: `gunicorn app:app`
   - Auto-detected from `Procfile` in the backend directory
   - Can be left empty to use the default

3. **Builder**: Nixpacks (auto-detected)
   - Uses `backend/nixpacks.toml` for build configuration

### Step 3: Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will provision a PostgreSQL instance
4. Database credentials are automatically injected as environment variables

### Step 4: Environment Variables

Railway automatically sets:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Service port

You need to add:

```
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this-in-production
```

**Generate a secure SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 5: Deploy

1. Click "Deploy"
2. Railway will build and deploy your backend
3. Your API will be available at `https://your-project.up.railway.app`

### Step 6: Generate Domain

1. Go to your backend service settings
2. Under "Networking", click "Generate Domain"
3. Copy this URL for your frontend environment variable

## Database Setup (Railway PostgreSQL)

Railway handles database setup automatically:

### Automatic Configuration

- PostgreSQL 15 instance is provisioned
- Connection URL is set in `DATABASE_URL`
- Tables are created automatically on first run (via SQLAlchemy)

### Manual Database Access

If you need to access the database directly:

1. Go to your PostgreSQL service in Railway
2. Click "Connect"
3. Use provided credentials with any PostgreSQL client

### Connection String Format

```
postgresql://username:password@hostname:port/database
```

### Running Migrations

The app automatically creates tables on startup using SQLAlchemy's `db.create_all()`.

For production, consider using a migration tool like Alembic:

```bash
# In backend directory
pip install alembic
alembic init migrations
# Configure and run migrations
```

## Environment Variables

### Frontend (.env)

```bash
# Required
VITE_API_URL=https://your-railway-backend.up.railway.app

# Optional (for local development)
VITE_API_URL=http://localhost:5000
```

### Backend (.env)

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# Optional
PORT=5000
```

## Post-Deployment

### 1. Update Frontend Environment

After deploying the backend:

1. Copy your Railway backend URL
2. Go to Vercel project settings
3. Update `VITE_API_URL` environment variable
4. Redeploy frontend (automatic or manual)

### 2. Test the Application

1. Visit your Vercel frontend URL
2. Try creating a trainer
3. Try creating a client
4. Test the assignment system
5. Check the dashboard updates

### 3. Verify API Health

```bash
curl https://your-railway-backend.up.railway.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### 4. Monitor Logs

**Vercel**:
- Go to project → "Deployments" → Select deployment → "Functions" tab

**Railway**:
- Go to service → "Deployments" → Select deployment → View logs

## Troubleshooting

### Frontend Issues

**Build Fails**:
- Check Node.js version (should be 18+)
- Verify all dependencies are in package.json
- Check build logs for specific errors

**API Connection Fails**:
- Verify `VITE_API_URL` is set correctly
- Check CORS settings in backend
- Verify backend is running

### Backend Issues

**Database Connection Error**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**:
- Check `DATABASE_URL` format
- Ensure PostgreSQL service is running
- Verify network connectivity

**Port Already in Use**:
```
OSError: [Errno 98] Address already in use
```

**Solution**:
- Railway sets `PORT` automatically
- Don't hardcode port in production

**Module Not Found**:
```
ModuleNotFoundError: No module named 'flask'
```

**Solution**:
- Verify requirements.txt is in correct location
- Check Railway build logs
- Ensure all dependencies are listed

### Database Issues

**Tables Not Created**:

**Solution**:
```python
# Verify in app.py:
with app.app_context():
    db.create_all()
```

**Connection Pool Exhausted**:

**Solution**:
- Upgrade Railway PostgreSQL plan
- Optimize database queries
- Add connection pooling

### CORS Issues

**CORS Error in Browser**:
```
Access to fetch at 'xxx' from origin 'yyy' has been blocked by CORS policy
```

**Solution**:
- Verify Flask-CORS is installed
- Check CORS configuration in app.py:
```python
from flask_cors import CORS
CORS(app)
```

## Custom Domain (Optional)

### Vercel Custom Domain

1. Go to project settings → "Domains"
2. Add your custom domain
3. Configure DNS records as instructed

### Railway Custom Domain

1. Go to service settings → "Networking"
2. Add custom domain
3. Configure DNS records (CNAME or A record)

## Monitoring & Maintenance

### Set Up Monitoring

**Vercel Analytics**:
- Enable in project settings
- Track page views and performance

**Railway Metrics**:
- Monitor CPU, memory, and network usage
- Set up alerts for downtime

### Regular Maintenance

- Monitor error logs weekly
- Update dependencies monthly
- Backup database regularly
- Review and optimize slow queries

## Scaling

### Horizontal Scaling

**Frontend** (Vercel):
- Automatic CDN distribution
- Edge network deployment
- No configuration needed

**Backend** (Railway):
- Upgrade to Pro plan for horizontal scaling
- Add multiple service replicas
- Configure load balancing

### Database Scaling

- Upgrade PostgreSQL plan for more resources
- Add read replicas for read-heavy workloads
- Implement connection pooling (PgBouncer)

## Security Checklist

- [ ] Change all default secrets
- [ ] Use strong `SECRET_KEY`
- [ ] Enable HTTPS (automatic on Vercel and Railway)
- [ ] Implement rate limiting
- [ ] Add input validation
- [ ] Enable database backups
- [ ] Set up monitoring and alerts
- [ ] Review and update dependencies
- [ ] Implement authentication (future phase)

## Cost Estimates

### Free Tier Limits

**Vercel Free Tier**:
- Bandwidth: 100 GB/month
- Build time: 6000 minutes/month
- Suitable for: Development and small production apps

**Railway Free Tier**:
- $5 monthly credit
- Includes one PostgreSQL database
- Suitable for: Development and MVP

### Upgrade Recommendations

**Vercel Pro** ($20/month):
- When you exceed free tier limits
- Need custom analytics
- Want advanced features

**Railway Pro** ($20/month):
- When you need more than $5/month usage
- Want horizontal scaling
- Need priority support

## Backup & Recovery

### Database Backups

**Automated** (Railway Pro):
- Daily automatic backups
- Point-in-time recovery

**Manual**:
```bash
# Export database
pg_dump $DATABASE_URL > backup.sql

# Import database
psql $DATABASE_URL < backup.sql
```

### Code Backups

- Use Git and GitHub
- Tag releases
- Document changes in CHANGELOG.md

## Support

- **Vercel**: [vercel.com/support](https://vercel.com/support)
- **Railway**: [railway.app/help](https://railway.app/help)
- **Project Issues**: GitHub Issues

---

**Last Updated**: December 2024
