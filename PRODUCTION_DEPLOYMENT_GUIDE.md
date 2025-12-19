# Production Deployment Guide - Phase 9

**Version**: v2.3.0  
**Last Updated**: December 2024

## Overview

This guide walks you through deploying FitnessCRM to production using the Phase 9 production configuration.

---

## Prerequisites

Before starting production deployment:

- [ ] Docker and Docker Compose installed
- [ ] Domain name configured (optional for initial testing)
- [ ] SSL certificates ready (or will use Let's Encrypt)
- [ ] Production database accessible
- [ ] Redis server available (or will use containerized version)
- [ ] Environment variables prepared

---

## Quick Start (5 Minutes)

### 1. Clone Repository

```bash
git clone https://github.com/JonSvitna/FitnessCRM.git
cd FitnessCRM
git checkout phase9/production-optimization
```

### 2. Configure Environment

```bash
# Copy production environment templates
cp backend/.env.production backend/.env
cp frontend/.env.production frontend/.env

# Edit with your production values
nano backend/.env
nano frontend/.env
```

### 3. Configure Secrets

Create a `.env` file in the project root for Docker Compose:

```bash
cat > .env << 'EOF'
# Database
POSTGRES_DB=fitnesscrm_prod
POSTGRES_USER=fitnesscrm_user
POSTGRES_PASSWORD=YOUR_SECURE_PASSWORD_HERE

# Redis
REDIS_PASSWORD=YOUR_SECURE_REDIS_PASSWORD

# Application
SECRET_KEY=YOUR_SUPER_SECURE_SECRET_KEY_HERE
VITE_API_URL=http://your-domain.com

# Optional: Monitoring
SENTRY_DSN=

# Optional: Email
MAIL_SERVER=
MAIL_USERNAME=
MAIL_PASSWORD=
EOF
```

### 4. Build and Start Services

```bash
# Build all services
docker-compose -f docker-compose.prod.yml build

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 5. Initialize Database

```bash
# Run database migrations
docker-compose -f docker-compose.prod.yml exec backend python init_db.py

# Optional: Seed with sample data
docker-compose -f docker-compose.prod.yml exec backend python seed_accounts.py
```

### 6. Verify Deployment

```bash
# Check health endpoint
curl http://localhost/api/health

# Check all services
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## Detailed Setup

### Environment Configuration

#### Backend (.env)

Required variables:
```bash
FLASK_ENV=production
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://:password@host:6379/0
```

Optional variables:
```bash
# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=app-specific-password

# Monitoring
SENTRY_DSN=https://your-key@sentry.io/project-id
LOG_LEVEL=INFO

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### Frontend (.env)

```bash
VITE_API_URL=https://api.yourdomain.com
VITE_APP_ENV=production
VITE_ENABLE_ANALYTICS=true
```

### SSL Certificate Setup

#### Option 1: Let's Encrypt (Production)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Stop nginx temporarily
docker-compose -f docker-compose.prod.yml stop nginx

# Generate certificate
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your-email@example.com \
  --agree-tos

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
sudo chmod 600 nginx/ssl/key.pem

# Update nginx.conf to enable HTTPS
# Uncomment HTTPS server block
nano nginx/nginx.conf

# Restart nginx
docker-compose -f docker-compose.prod.yml start nginx
```

#### Option 2: Self-Signed (Development/Testing)

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Org/CN=localhost"

chmod 600 nginx/ssl/key.pem
```

### Database Setup

#### Using Docker PostgreSQL (Included)

```bash
# Start database
docker-compose -f docker-compose.prod.yml up -d db

# Wait for database to be ready
docker-compose -f docker-compose.prod.yml exec db pg_isready

# Initialize database
docker-compose -f docker-compose.prod.yml exec backend python init_db.py
```

#### Using External PostgreSQL (Railway, AWS RDS, etc.)

```bash
# Update DATABASE_URL in backend/.env
DATABASE_URL=postgresql://user:pass@external-host:5432/dbname

# Initialize database from your machine or a container
cd backend
python init_db.py
```

### Redis Setup

#### Using Docker Redis (Included)

```bash
# Start Redis
docker-compose -f docker-compose.prod.yml up -d redis

# Test connection
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a YOUR_PASSWORD ping
```

#### Using External Redis (Redis Cloud, AWS ElastiCache, etc.)

```bash
# Update REDIS_URL in backend/.env
REDIS_URL=redis://:password@external-redis:6379/0
```

---

## Production Checklist

### Pre-Deployment
- [ ] All environment variables configured
- [ ] Secrets are strong and secure
- [ ] Database accessible and initialized
- [ ] Redis cache accessible
- [ ] SSL certificates generated
- [ ] Domain DNS configured
- [ ] Firewall rules configured

### Security
- [ ] Change all default passwords
- [ ] SECRET_KEY is random and secure
- [ ] Database credentials are strong
- [ ] Redis password is set
- [ ] SSL/TLS enabled
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] CORS configured properly

### Performance
- [ ] Redis caching enabled
- [ ] Gzip compression enabled
- [ ] Static file caching configured
- [ ] Database connection pooling set
- [ ] Worker processes optimized

### Monitoring
- [ ] Health check endpoint working
- [ ] Logs being written
- [ ] Monitoring service configured (if using)
- [ ] Backup system configured
- [ ] Uptime monitoring set up

### Testing
- [ ] All services healthy
- [ ] API endpoints responding
- [ ] Frontend loading correctly
- [ ] Database queries working
- [ ] Redis cache working
- [ ] SSL certificate valid
- [ ] Rate limiting functional

---

## Service Management

### Starting Services

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Start specific service
docker-compose -f docker-compose.prod.yml up -d backend
```

### Stopping Services

```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Stop without removing volumes
docker-compose -f docker-compose.prod.yml stop
```

### Restarting Services

```bash
# Restart all
docker-compose -f docker-compose.prod.yml restart

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend
```

### Viewing Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Checking Status

```bash
# Service status
docker-compose -f docker-compose.prod.yml ps

# Resource usage
docker stats

# Health checks
curl http://localhost/api/health
```

---

## Updating Application

### Zero-Downtime Deployment

```bash
# Pull latest changes
git pull origin main

# Rebuild images
docker-compose -f docker-compose.prod.yml build

# Rolling restart (one service at a time)
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend
docker-compose -f docker-compose.prod.yml up -d --no-deps --build frontend

# Verify deployment
curl http://localhost/api/health
```

### Database Migrations

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python migrate.py

# Or with backup first
docker-compose -f docker-compose.prod.yml exec db pg_dump -U fitnesscrm_user fitnesscrm_prod > backup.sql
docker-compose -f docker-compose.prod.yml exec backend python migrate.py
```

---

## Backup & Recovery

### Manual Backup

```bash
# Database backup
docker-compose -f docker-compose.prod.yml exec db \
  pg_dump -U fitnesscrm_user fitnesscrm_prod | gzip > backup-$(date +%Y%m%d-%H%M%S).sql.gz

# Redis backup
docker-compose -f docker-compose.prod.yml exec redis redis-cli BGSAVE
docker cp $(docker-compose -f docker-compose.prod.yml ps -q redis):/data/dump.rdb ./redis-backup.rdb
```

### Automated Backups

See `scripts/backup.sh` (to be created in Phase 9) for automated backup script.

### Restore from Backup

```bash
# Stop application
docker-compose -f docker-compose.prod.yml stop backend

# Restore database
gunzip -c backup-20241219-120000.sql.gz | \
  docker-compose -f docker-compose.prod.yml exec -T db \
  psql -U fitnesscrm_user fitnesscrm_prod

# Restart application
docker-compose -f docker-compose.prod.yml start backend
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs service-name

# Check configuration
docker-compose -f docker-compose.prod.yml config

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --force-recreate service-name
```

### Database Connection Issues

```bash
# Test database connectivity
docker-compose -f docker-compose.prod.yml exec db pg_isready

# Check database logs
docker-compose -f docker-compose.prod.yml logs db

# Connect to database
docker-compose -f docker-compose.prod.yml exec db psql -U fitnesscrm_user -d fitnesscrm_prod
```

### Redis Connection Issues

```bash
# Test Redis connectivity
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a YOUR_PASSWORD ping

# Check Redis logs
docker-compose -f docker-compose.prod.yml logs redis

# Monitor Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a YOUR_PASSWORD monitor
```

### 502 Bad Gateway

```bash
# Check backend is running
docker-compose -f docker-compose.prod.yml ps backend

# Check backend logs
docker-compose -f docker-compose.prod.yml logs backend

# Test backend directly
curl http://localhost:5000/api/health

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Limit container resources (edit docker-compose.prod.yml)
# Add under service:
#   deploy:
#     resources:
#       limits:
#         memory: 1G
```

---

## Monitoring

### Health Checks

```bash
# API health
curl http://localhost/api/health

# Database health
docker-compose -f docker-compose.prod.yml exec db pg_isready

# Redis health
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a YOUR_PASSWORD ping
```

### Performance Monitoring

```bash
# Container stats
docker stats

# Database connections
docker-compose -f docker-compose.prod.yml exec db \
  psql -U fitnesscrm_user -d fitnesscrm_prod \
  -c "SELECT count(*) FROM pg_stat_activity;"

# Redis info
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a YOUR_PASSWORD info
```

### Log Analysis

```bash
# Error logs
docker-compose -f docker-compose.prod.yml logs | grep ERROR

# Access logs (nginx)
docker-compose -f docker-compose.prod.yml logs nginx | grep GET

# Slow queries (database)
docker-compose -f docker-compose.prod.yml exec db \
  psql -U fitnesscrm_user -d fitnesscrm_prod \
  -c "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

---

## Scaling

### Horizontal Scaling (Multiple Instances)

```bash
# Scale backend to 3 instances
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Nginx will load balance across all instances
```

### Vertical Scaling (More Resources)

Edit `docker-compose.prod.yml` to increase resources:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## Security Best Practices

### Change Default Credentials
- Update all passwords in `.env`
- Use strong, random passwords (min 32 characters)
- Never commit `.env` file

### Enable HTTPS
- Use Let's Encrypt for SSL
- Enable HTTPS redirect in nginx
- Configure HSTS header

### Regular Updates
- Keep Docker images updated
- Update dependencies regularly
- Apply security patches promptly

### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### Backup Strategy
- Daily automated backups
- Off-site backup storage
- Test restore procedures regularly

---

## Performance Optimization

### Database Optimization
- Create indexes on frequently queried columns
- Use connection pooling
- Regular VACUUM and ANALYZE

### Caching Strategy
- Enable Redis caching
- Cache frequently accessed data
- Set appropriate TTL values

### Frontend Optimization
- Enable gzip compression
- Use CDN for static assets
- Implement browser caching

---

## Support & Resources

### Documentation
- [Phase 9 Guide](PHASE9_PRODUCTION_OPTIMIZATION.md)
- [Quick Start](PHASE9_QUICKSTART.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Nginx Configuration](nginx/README.md)

### Monitoring Services
- [Sentry](https://sentry.io) - Error tracking
- [UptimeRobot](https://uptimerobot.com) - Uptime monitoring
- [New Relic](https://newrelic.com) - APM

### Community
- GitHub Issues
- Documentation Wiki
- Support Email

---

## Next Steps

After successful deployment:

1. **Configure Monitoring**: Set up Sentry, UptimeRobot, etc.
2. **Set Up Backups**: Automate daily backups
3. **Load Testing**: Test with expected traffic
4. **Documentation**: Document your specific setup
5. **Team Training**: Train team on operations

---

**Congratulations! Your FitnessCRM is now running in production! 🚀**

For questions or issues, refer to [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or create a GitHub issue.
