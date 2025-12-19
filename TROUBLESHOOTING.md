# FitnessCRM Troubleshooting Guide 🔧

This guide provides solutions to common issues encountered when developing, testing, or deploying the FitnessCRM application.

## Table of Contents

1. [Backend Issues](#backend-issues)
2. [Frontend Issues](#frontend-issues)
3. [Database Issues](#database-issues)
4. [API Integration Issues](#api-integration-issues)
5. [Deployment Issues](#deployment-issues)
6. [Performance Issues](#performance-issues)
7. [Security Issues](#security-issues)
8. [External Service Issues](#external-service-issues)

---

## Backend Issues

### Issue: Flask Application Won't Start

**Symptoms**:
- Error: "Address already in use"
- Flask fails to bind to port
- Application crashes on startup

**Solutions**:

1. **Check if port is already in use**:
   ```bash
   # Find process using port 5000
   lsof -i :5000
   
   # Kill the process
   kill -9 <PID>
   ```

2. **Try a different port**:
   ```bash
   export PORT=5001
   python app.py
   ```

3. **Check for Python errors**:
   ```bash
   python -c "from app import create_app; app = create_app(); print('OK')"
   ```

---

### Issue: Import Errors in Backend

**Symptoms**:
- ModuleNotFoundError
- ImportError
- "No module named X"

**Solutions**:

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Check Python path**:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

3. **Use virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

---

### Issue: Database Connection Failed

**Symptoms**:
- SQLAlchemy connection errors
- "Connection refused"
- "Could not connect to server"

**Solutions**:

1. **Check DATABASE_URL**:
   ```bash
   echo $DATABASE_URL
   # Should be: postgresql://user:pass@host:port/dbname
   ```

2. **Test database connection**:
   ```bash
   psql $DATABASE_URL
   ```

3. **Check PostgreSQL is running**:
   ```bash
   # On macOS
   brew services list | grep postgresql
   
   # On Linux
   systemctl status postgresql
   
   # Test connectivity
   pg_isready
   ```

4. **Check firewall settings**:
   ```bash
   # Ensure port 5432 is open
   sudo ufw status
   ```

5. **Verify credentials**:
   - Check username and password
   - Ensure database exists: `psql -l`
   - Create database if needed: `createdb fitnesscrm`

---

### Issue: CORS Errors

**Symptoms**:
- "Access-Control-Allow-Origin" error in browser
- API requests blocked by CORS policy
- Preflight requests failing

**Solutions**:

1. **Check CORS configuration** in `backend/app.py`:
   ```python
   CORS(app, resources={
       r"/api/*": {
           "origins": ["http://localhost:3000", "https://your-domain.com"],
           "methods": ["GET", "POST", "PUT", "DELETE"],
           "allow_headers": ["Content-Type", "Authorization"]
       }
   })
   ```

2. **Update allowed origins**:
   ```python
   # For development
   CORS(app, origins="*")
   
   # For production (more secure)
   CORS(app, origins=["https://your-production-domain.com"])
   ```

3. **Check request headers**:
   - Ensure `Content-Type: application/json` is set
   - Check authorization headers if using auth

---

## Frontend Issues

### Issue: Frontend Won't Build

**Symptoms**:
- Vite build errors
- "Command not found"
- Module not found

**Solutions**:

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Clear cache and reinstall**:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Check Node version**:
   ```bash
   node --version  # Should be 18+
   nvm use 18  # If using nvm
   ```

4. **Check for syntax errors**:
   ```bash
   npm run build
   # Look for specific error messages
   ```

---

### Issue: API Requests Failing

**Symptoms**:
- 404 Not Found errors
- Network request failed
- CORS errors

**Solutions**:

1. **Check API URL configuration**:
   ```bash
   # Check .env file
   cat frontend/.env
   # Should have: VITE_API_URL=http://localhost:5000
   ```

2. **Verify backend is running**:
   ```bash
   curl http://localhost:5000/api/health
   ```

3. **Check network tab in browser**:
   - Open DevTools (F12)
   - Go to Network tab
   - Look at failed requests
   - Check request URL and headers

4. **Test with curl**:
   ```bash
   curl -v http://localhost:5000/api/trainers
   ```

---

### Issue: Environment Variables Not Loading

**Symptoms**:
- API URL is undefined
- Configuration values missing
- App behaves differently in production

**Solutions**:

1. **Check .env file exists**:
   ```bash
   ls -la frontend/.env
   ```

2. **Verify variable naming** (must start with `VITE_`):
   ```bash
   # Correct
   VITE_API_URL=http://localhost:5000
   
   # Wrong (won't be exposed to client)
   API_URL=http://localhost:5000
   ```

3. **Restart dev server**:
   ```bash
   # Changes to .env require restart
   npm run dev
   ```

4. **Check variable in code**:
   ```javascript
   console.log('API URL:', import.meta.env.VITE_API_URL);
   ```

---

## Database Issues

### Issue: Tables Not Created

**Symptoms**:
- "Table does not exist" errors
- Query fails with relation error
- Empty database

**Solutions**:

1. **Initialize database**:
   ```bash
   cd backend
   python init_db.py
   ```

2. **Check tables exist**:
   ```bash
   psql $DATABASE_URL -c "\dt"
   ```

3. **Recreate tables**:
   ```python
   from app import create_app
   from models.database import db
   
   app = create_app()
   with app.app_context():
       db.drop_all()  # Caution: deletes all data
       db.create_all()
   ```

---

### Issue: Migration Errors

**Symptoms**:
- Schema mismatch errors
- Column doesn't exist
- Data type conflicts

**Solutions**:

1. **Check model definitions**:
   ```bash
   # Review model changes
   git diff backend/models/database.py
   ```

2. **Drop and recreate** (development only):
   ```bash
   python init_db.py  # Will recreate all tables
   ```

3. **Manual migration**:
   ```sql
   -- Add missing column
   ALTER TABLE trainers ADD COLUMN new_field VARCHAR(255);
   
   -- Modify column type
   ALTER TABLE clients ALTER COLUMN age TYPE INTEGER;
   ```

---

### Issue: Slow Queries

**Symptoms**:
- API endpoints timing out
- Long page load times
- Database high CPU usage

**Solutions**:

1. **Check query performance**:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM trainers WHERE specialization = 'Yoga';
   ```

2. **Add indexes**:
   ```sql
   CREATE INDEX idx_trainers_specialization ON trainers(specialization);
   CREATE INDEX idx_clients_status ON clients(status);
   CREATE INDEX idx_sessions_date ON sessions(session_date);
   ```

3. **Optimize queries**:
   ```python
   # Instead of N+1 queries
   trainers = Trainer.query.all()
   for trainer in trainers:
       clients = trainer.clients  # N queries
   
   # Use eager loading
   trainers = Trainer.query.options(
       db.joinedload(Trainer.clients)
   ).all()  # 1 query
   ```

---

## API Integration Issues

### Issue: Email Not Sending

**Symptoms**:
- Email notifications not received
- Flask-Mail errors
- SMTP authentication failed

**Solutions**:

1. **Check email configuration**:
   ```bash
   # Required environment variables
   echo $MAIL_SERVER
   echo $MAIL_PORT
   echo $MAIL_USERNAME
   echo $MAIL_PASSWORD
   ```

2. **Test SMTP connection**:
   ```python
   import smtplib
   
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('user@gmail.com', 'password')
   server.quit()
   ```

3. **Check SendGrid configuration**:
   ```bash
   # For SendGrid
   export MAIL_SERVER=smtp.sendgrid.net
   export MAIL_PORT=587
   export MAIL_USERNAME=apikey
   export MAIL_PASSWORD=your-sendgrid-api-key
   ```

4. **Test email sending**:
   ```bash
   curl -X POST http://localhost:5000/api/test-email \
     -H "Content-Type: application/json" \
     -d '{"to": "test@example.com"}'
   ```

---

### Issue: SMS Not Sending

**Symptoms**:
- SMS notifications not delivered
- Twilio errors
- Invalid phone number format

**Solutions**:

1. **Check Twilio credentials**:
   ```bash
   echo $TWILIO_ACCOUNT_SID
   echo $TWILIO_AUTH_TOKEN
   echo $TWILIO_PHONE_NUMBER
   ```

2. **Verify phone number format**:
   ```python
   # Correct format
   phone = "+1234567890"  # E.164 format with country code
   
   # Wrong format
   phone = "123-456-7890"
   ```

3. **Test Twilio API**:
   ```bash
   curl -X POST https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json \
     --data-urlencode "From=$TWILIO_PHONE_NUMBER" \
     --data-urlencode "To=+1234567890" \
     --data-urlencode "Body=Test message" \
     -u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN
   ```

---

### Issue: Payment Processing Failed

**Symptoms**:
- Stripe errors
- Payment declined
- Webhook not received

**Solutions**:

1. **Check Stripe configuration**:
   ```bash
   echo $STRIPE_SECRET_KEY
   echo $STRIPE_PUBLISHABLE_KEY
   echo $STRIPE_WEBHOOK_SECRET
   ```

2. **Use test mode**:
   ```python
   # Test card numbers
   # Success: 4242 4242 4242 4242
   # Declined: 4000 0000 0000 0002
   ```

3. **Test webhook locally**:
   ```bash
   # Install Stripe CLI
   stripe listen --forward-to localhost:5000/api/webhooks/stripe
   ```

---

## Deployment Issues

### Issue: Vercel Deployment Failed

**Symptoms**:
- Build fails on Vercel
- Environment variables not set
- Routes return 404

**Solutions**:

1. **Check build command**:
   ```json
   // vercel.json
   {
     "buildCommand": "npm run build",
     "outputDirectory": "dist"
   }
   ```

2. **Set environment variables** in Vercel dashboard:
   - `VITE_API_URL` = your Railway backend URL

3. **Check build logs**:
   - Go to Vercel dashboard
   - Click on deployment
   - View build logs for errors

---

### Issue: Railway Deployment Failed

**Symptoms**:
- Build fails
- Application won't start
- Database connection failed

**Solutions**:

1. **Check Procfile**:
   ```
   web: gunicorn app:app
   ```

2. **Verify root directory** in Railway settings:
   - Set "Root Directory" to `backend`
   - Or use `railway.toml`:
     ```toml
     [build]
     builder = "nixpacks"
     buildCommand = "pip install -r requirements.txt"
     
     [deploy]
     startCommand = "gunicorn app:app"
     
     [deploy.env]
     ROOT = "backend"
     ```

3. **Check environment variables**:
   - `DATABASE_URL` (auto-configured)
   - `SECRET_KEY`
   - `FLASK_ENV=production`

4. **View logs**:
   ```bash
   railway logs
   ```

---

## Performance Issues

### Issue: Slow Page Load Times

**Solutions**:

1. **Enable caching**:
   ```python
   from flask_caching import Cache
   
   cache = Cache(app, config={
       'CACHE_TYPE': 'simple',
       'CACHE_DEFAULT_TIMEOUT': 300
   })
   
   @app.route('/api/trainers')
   @cache.cached(timeout=60)
   def get_trainers():
       return Trainer.query.all()
   ```

2. **Add pagination**:
   ```python
   page = request.args.get('page', 1, type=int)
   per_page = request.args.get('per_page', 20, type=int)
   trainers = Trainer.query.paginate(page=page, per_page=per_page)
   ```

3. **Optimize database queries** (see Database Issues above)

4. **Use CDN for static assets**

---

## Security Issues

### Issue: Unauthorized Access

**Solutions**:

1. **Implement authentication**:
   ```python
   from utils.auth import require_auth
   
   @app.route('/api/trainers')
   @require_auth
   def get_trainers():
       return Trainer.query.all()
   ```

2. **Add rate limiting**:
   ```python
   from flask_limiter import Limiter
   
   limiter = Limiter(app, key_func=lambda: request.remote_addr)
   
   @app.route('/api/login')
   @limiter.limit("5 per minute")
   def login():
       pass
   ```

3. **Validate input**:
   ```python
   from werkzeug.security import escape
   
   email = escape(request.json.get('email', ''))
   ```

---

## External Service Issues

### Issue: WebSocket Connection Failed

**Symptoms**:
- Real-time features not working
- Socket.IO errors
- Messages not delivered

**Solutions**:

1. **Check Socket.IO server**:
   ```python
   # Ensure socketio is initialized
   from flask_socketio import SocketIO
   socketio = SocketIO(app, cors_allowed_origins="*")
   ```

2. **Verify client connection**:
   ```javascript
   const socket = io('http://localhost:5000', {
     transports: ['websocket', 'polling']
   });
   
   socket.on('connect', () => {
     console.log('Connected!');
   });
   ```

3. **Check CORS for WebSocket**:
   ```python
   socketio = SocketIO(app, cors_allowed_origins=[
       "http://localhost:3000",
       "https://your-domain.com"
   ])
   ```

---

## Debug Mode

### Enable Debug Mode

**Backend**:
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

**Frontend**:
```bash
npm run dev
# DevTools already enabled
```

### Enable SQL Query Logging

```python
app.config['SQLALCHEMY_ECHO'] = True
```

### Enable Detailed Error Pages

```python
app.config['DEBUG'] = True
```

---

## Getting Help

If you're still experiencing issues:

1. **Check documentation**:
   - [README.md](README.md)
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
   - [DEPLOYMENT.md](DEPLOYMENT.md)

2. **Run health check**:
   ```bash
   python scripts/health_check.py
   ```

3. **Check logs**:
   ```bash
   # Backend logs
   tail -f backend.log
   
   # Railway logs
   railway logs
   
   # Vercel logs (in dashboard)
   ```

4. **Open an issue** on GitHub with:
   - Detailed error message
   - Steps to reproduce
   - Your environment (OS, Python/Node version)
   - Relevant logs

---

**Last Updated**: December 2024
