# FitnessCRM Production Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [SSL/TLS Configuration](#ssltls-configuration)
4. [Docker Deployment](#docker-deployment)
5. [Database Setup](#database-setup)
6. [Redis Configuration](#redis-configuration)
7. [Nginx Configuration](#nginx-configuration)
8. [Monitoring Setup](#monitoring-setup)
9. [Backup Configuration](#backup-configuration)
10. [Security Checklist](#security-checklist)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- Linux server (Ubuntu 20.04+ or similar)
- Minimum 2 CPU cores
- Minimum 4GB RAM (8GB recommended)
- Minimum 20GB disk space (50GB recommended)
- Docker 20.10+
- Docker Compose 2.0+

### Domain Requirements
- A registered domain name
- DNS configured to point to your server
- SSL certificate (Let's Encrypt recommended)

### Required Accounts
- Sentry account for error tracking (optional but recommended)
- SMTP service for email notifications
- Twilio account for SMS (optional)
- Stripe account for payments (optional)

---

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/FitnessCRM.git
cd FitnessCRM
```

### 2. Create Production Environment File

```bash
cp .env.production.template .env.production
```

### 3. Configure Environment Variables

Edit `.env.production` and update all the values:

#### Critical Variables to Change
```bash
# Database
POSTGRES_PASSWORD=<generate-strong-password>

# Redis
REDIS_PASSWORD=<generate-strong-password>

# Application
SECRET_KEY=<generate-long-random-string>

# Domain
DOMAIN=yourdomain.com
API_DOMAIN=api.yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
VITE_API_URL=https://api.yourdomain.com
```

#### Generate Secure Passwords

```bash
# Generate a secure password
openssl rand -base64 32

# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## SSL/TLS Configuration

### Using Let's Encrypt (Recommended)

#### 1. Install Certbot

```bash
sudo apt update
sudo apt install certbot
```

#### 2. Obtain SSL Certificate

```bash
# Stop nginx if running
docker-compose -f docker-compose.prod.yml stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates will be at:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

#### 3. Copy Certificates to Project

```bash
mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
sudo chmod 644 nginx/ssl/cert.pem
sudo chmod 600 nginx/ssl/key.pem
```

#### 4. Enable HTTPS in Nginx Config

Edit `nginx/nginx.conf` and uncomment the HTTPS server block (lines 162-182).

#### 5. Set Up Auto-Renewal

```bash
# Add cron job for certificate renewal
sudo crontab -e

# Add this line:
0 3 * * * certbot renew --quiet --deploy-hook "docker-compose -f /path/to/FitnessCRM/docker-compose.prod.yml restart nginx"
```

---

## Docker Deployment

### 1. Build Production Images

```bash
# Set production environment
export $(cat .env.production | xargs)

# Build images
docker-compose -f docker-compose.prod.yml build --no-cache
```

### 2. Start Services

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 3. Verify Services

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# All services should be "Up" and healthy
```

### 4. Initialize Database

```bash
# Run database initialization
docker-compose -f docker-compose.prod.yml exec backend python init_db.py
```

---

## Database Setup

### 1. Database Initialization

The database is automatically initialized on first startup using the `init_db.sql` script.

### 2. Create Admin User

```bash
# Connect to backend container
docker-compose -f docker-compose.prod.yml exec backend python

# In Python shell:
from models.user import User
from app import db, app

with app.app_context():
    admin = User(
        email='admin@yourdomain.com',
        username='admin',
        role='admin'
    )
    admin.set_password('change-this-password')
    db.session.add(admin)
    db.session.commit()
    print("Admin user created!")
```

### 3. Database Backups

See [Backup Configuration](#backup-configuration) section below.

---

## Redis Configuration

Redis is configured in `docker-compose.prod.yml` with the following settings:

- **Persistence**: AOF (Append-Only File) enabled
- **Password Protected**: Using REDIS_PASSWORD from .env.production

### Verify Redis Connection

```bash
# Connect to Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a <REDIS_PASSWORD>

# Test connection
redis> PING
# Should respond: PONG

# Check memory usage
redis> INFO memory
```

---

## Nginx Configuration

### Configuration Files

- **Main config**: `nginx/nginx.conf`
- **SSL certificates**: `nginx/ssl/`
- **Logs**: `nginx/logs/`

### Rate Limiting

Default rate limits configured:
- API endpoints: 10 requests/second (burst 20)
- Authentication: 5 requests/second (burst 5)
- General pages: 30 requests/second (burst 50)

### Reload Nginx Configuration

```bash
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

---

## Monitoring Setup

### 1. Sentry Integration

#### Configure Sentry

1. Sign up at [sentry.io](https://sentry.io)
2. Create a new project for Flask
3. Copy the DSN
4. Update `.env.production`:

```bash
SENTRY_DSN=https://your-dsn@sentry.io/project-id
```

#### Restart Backend

```bash
docker-compose -f docker-compose.prod.yml restart backend
```

### 2. Health Checks

#### Application Health Endpoint

```bash
curl http://localhost/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "version": "2.3.0"
}
```

---

## Backup Configuration

### 1. Automated Database Backups

Create backup script: `scripts/backup-database.sh`

```bash
#!/bin/bash
set -e

# Configuration
BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="fitnesscrm_backup_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
docker-compose -f docker-compose.prod.yml exec -T db pg_dump \
  -U $POSTGRES_USER \
  -d $POSTGRES_DB \
  | gzip > "$BACKUP_DIR/$BACKUP_FILE"

# Remove old backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_FILE"
```

### 2. Schedule Backups

```bash
# Make script executable
chmod +x scripts/backup-database.sh

# Add to crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/FitnessCRM/scripts/backup-database.sh >> /var/log/fitnesscrm-backup.log 2>&1
```

### 3. Restore from Backup

```bash
# Stop the application
docker-compose -f docker-compose.prod.yml stop backend

# Restore database
gunzip -c /backups/postgres/fitnesscrm_backup_YYYYMMDD_HHMMSS.sql.gz | \
docker-compose -f docker-compose.prod.yml exec -T db psql \
  -U $POSTGRES_USER \
  -d $POSTGRES_DB

# Restart application
docker-compose -f docker-compose.prod.yml start backend
```

---

## Security Checklist

### Pre-Deployment

- [ ] All default passwords changed
- [ ] SECRET_KEY is a strong random value
- [ ] SSL certificate obtained and configured
- [ ] HTTPS redirect enabled in Nginx
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] SSH key-based authentication enabled
- [ ] Root login disabled
- [ ] Regular security updates enabled

### Application Security

- [ ] Environment variables properly set
- [ ] CORS origins configured correctly
- [ ] Rate limiting enabled
- [ ] File upload size limits configured
- [ ] Database ports not exposed to internet
- [ ] Redis password protected
- [ ] Session cookies set to secure and httponly
- [ ] CSRF protection enabled
- [ ] Input validation on all forms
- [ ] SQL injection prevention (using ORM)

---

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Rebuild and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Database Connection Issues

```bash
# Check database status
docker-compose -f docker-compose.prod.yml exec db pg_isready

# Check database logs
docker-compose -f docker-compose.prod.yml logs db
```

---

**Last Updated**: January 2026
**Version**: 2.3.0
