# FitnessCRM Operations Manual

## Quick Reference

### Essential Commands

```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up -d

# Stop all services
docker-compose -f docker-compose.prod.yml down

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend

# Health check
./scripts/health-check.sh

# Database backup
./scripts/backup-database.sh --s3

# Database restore
./scripts/restore-database.sh --latest
```

### Emergency Contacts

- **On-Call Engineer**: your-oncall@domain.com
- **Database Admin**: dba@domain.com
- **Security Team**: security@domain.com

---

## Daily Operations

### Morning Checklist

1. **Run Health Check**
   ```bash
   ./scripts/health-check.sh
   ```

2. **Check Application Logs**
   ```bash
   docker-compose -f docker-compose.prod.yml logs --tail=100 backend
   ```

3. **Verify Backups**
   ```bash
   ls -lh /backups/postgres/ | tail -5
   ```

4. **Monitor Resource Usage**
   ```bash
   docker stats
   ```

### Weekly Tasks

1. **Review Error Logs** (Monday)
   - Check Sentry for new errors
   - Review application error logs
   - Create tickets for recurring issues

2. **Database Maintenance** (Wednesday)
   ```bash
   # Vacuum and analyze
   docker-compose -f docker-compose.prod.yml exec db \
     psql -U $POSTGRES_USER -d $POSTGRES_DB -c "VACUUM ANALYZE;"
   
   # Check table sizes
   docker-compose -f docker-compose.prod.yml exec db \
     psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
     "SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
      FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema') 
      ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"
   ```

3. **Performance Review** (Friday)
   - Review API response times
   - Check cache hit rates
   - Monitor database slow queries

### Monthly Tasks

1. **Security Updates**
   ```bash
   # Update Docker images
   docker-compose -f docker-compose.prod.yml pull
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Backup Verification**
   - Test backup restoration in staging
   - Verify backup integrity
   - Confirm S3 uploads

3. **Performance Audit**
   - Run Lighthouse audit
   - Review performance metrics
   - Identify optimization opportunities

---

## Deployment Procedures

### Standard Deployment

1. **Pre-Deployment**
   ```bash
   # Backup database
   ./scripts/backup-database.sh
   
   # Run health check
   ./scripts/health-check.sh
   ```

2. **Deploy**
   ```bash
   # Pull latest code
   git pull origin main
   
   # Rebuild and restart
   docker-compose -f docker-compose.prod.yml build
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Post-Deployment**
   ```bash
   # Verify services
   ./scripts/health-check.sh
   
   # Check logs
   docker-compose -f docker-compose.prod.yml logs --tail=50
   
   # Test critical endpoints
   curl http://localhost/api/health
   ```

### Rollback Procedure

1. **Identify Previous Version**
   ```bash
   git log --oneline -5
   ```

2. **Rollback Code**
   ```bash
   git checkout <previous-commit-hash>
   ```

3. **Rebuild and Deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml build
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Restore Database (if needed)**
   ```bash
   ./scripts/restore-database.sh /backups/postgres/backup_before_deployment.sql.gz
   ```

---

## Monitoring

### Key Metrics

| Metric | Threshold | Action |
|--------|-----------|--------|
| CPU Usage | > 80% | Investigate high-load processes |
| Memory Usage | > 85% | Check for memory leaks |
| Disk Usage | > 85% | Clean up logs, old backups |
| API Response Time | > 500ms | Check slow queries |
| Error Rate | > 1% | Review error logs |
| Database Connections | > 80 | Investigate connection leaks |

### Monitoring Commands

```bash
# Check system resources
docker stats

# Check database connections
docker-compose -f docker-compose.prod.yml exec db \
  psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
  "SELECT count(*) FROM pg_stat_activity;"

# Check Redis memory
docker-compose -f docker-compose.prod.yml exec redis \
  redis-cli -a $REDIS_PASSWORD INFO memory

# View slow queries
docker-compose -f docker-compose.prod.yml exec db \
  psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
  "SELECT query, mean_exec_time FROM pg_stat_statements 
   ORDER BY mean_exec_time DESC LIMIT 10;"
```

---

## Troubleshooting

### Common Issues

#### 1. Service Won't Start

**Symptoms**: Container fails to start or crashes immediately

**Diagnosis**:
```bash
docker-compose -f docker-compose.prod.yml logs <service>
```

**Solutions**:
- Check environment variables
- Verify database connectivity
- Review configuration files
- Check disk space

#### 2. High CPU Usage

**Diagnosis**:
```bash
docker stats
top -p $(docker inspect --format '{{.State.Pid}}' fitnesscrm_backend_prod)
```

**Solutions**:
- Check for infinite loops in code
- Review recent deployments
- Optimize database queries
- Scale horizontally

#### 3. Database Connection Errors

**Symptoms**: "Cannot connect to database" errors

**Diagnosis**:
```bash
# Check database status
docker-compose -f docker-compose.prod.yml exec db pg_isready

# Check connections
docker-compose -f docker-compose.prod.yml exec db \
  psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
  "SELECT * FROM pg_stat_activity;"
```

**Solutions**:
- Verify DATABASE_URL
- Check connection pool settings
- Restart database container
- Check for connection leaks

#### 4. Out of Memory

**Symptoms**: Services crashing with OOM errors

**Diagnosis**:
```bash
dmesg | grep -i "out of memory"
docker stats
```

**Solutions**:
- Increase container memory limits
- Optimize application memory usage
- Add swap space
- Scale horizontally

#### 5. Slow Performance

**Diagnosis**:
```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost/api/health

# Check database
docker-compose -f docker-compose.prod.yml exec db \
  psql -U $POSTGRES_USER -d $POSTGRES_DB -c \
  "SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

**Solutions**:
- Add database indexes
- Enable caching
- Optimize queries
- Review Nginx configuration

---

## Maintenance Windows

### Planned Maintenance

**Schedule**: First Sunday of each month, 2:00 AM - 4:00 AM EST

**Procedure**:

1. **Notify Users** (48 hours in advance)
   - Email notification
   - In-app banner
   - Status page update

2. **Pre-Maintenance**
   ```bash
   # Full backup
   ./scripts/backup-database.sh --s3
   
   # Health check
   ./scripts/health-check.sh
   ```

3. **Maintenance**
   - Apply security updates
   - Database optimization
   - Clean up old data
   - Update SSL certificates

4. **Post-Maintenance**
   ```bash
   # Verify all services
   ./scripts/health-check.sh
   
   # Test critical functions
   # Update status page
   ```

---

## Backup & Recovery

### Backup Strategy

- **Frequency**: Daily at 2:00 AM EST
- **Retention**: 30 days local, 90 days S3
- **Type**: Full database dump

### Recovery Time Objectives

- **RTO** (Recovery Time Objective): 1 hour
- **RPO** (Recovery Point Objective): 24 hours (daily backups)

### Recovery Procedure

1. **Stop Application**
   ```bash
   docker-compose -f docker-compose.prod.yml stop backend
   ```

2. **Restore Database**
   ```bash
   ./scripts/restore-database.sh --latest
   ```

3. **Verify Restoration**
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python -c \
     "from app import db; print('Clients:', db.session.query(Client).count())"
   ```

4. **Start Application**
   ```bash
   docker-compose -f docker-compose.prod.yml start backend
   ```

---

## Security Operations

### Security Monitoring

Daily checks:
- Review failed login attempts
- Check for suspicious activity
- Monitor error rates
- Review audit logs

```bash
# Check failed logins
docker-compose -f docker-compose.prod.yml exec backend python -c \
  "from models.activity_log import ActivityLog; \
   print(ActivityLog.query.filter_by(action='login_failure').limit(10).all())"
```

### Incident Response

1. **Detection**: Automated alerts, user reports
2. **Assessment**: Determine severity and scope
3. **Containment**: Isolate affected systems
4. **Eradication**: Remove threat
5. **Recovery**: Restore normal operations
6. **Lessons Learned**: Post-incident review

---

## Performance Optimization

### Regular Optimization Tasks

1. **Database**
   - VACUUM ANALYZE weekly
   - Review and add indexes
   - Archive old data

2. **Cache**
   - Monitor hit rates
   - Adjust TTLs
   - Clear stale data

3. **Logs**
   - Rotate logs daily
   - Archive old logs
   - Clean up disk space

---

## Documentation

### Key Documents

- [Production Deployment Guide](PRODUCTION_DEPLOYMENT.md)
- [Performance Optimization Guide](PERFORMANCE_OPTIMIZATION.md)
- [Security Hardening Guide](SECURITY_HARDENING.md)
- [API Documentation](../API_DOCUMENTATION.md)
- [Troubleshooting Guide](../TROUBLESHOOTING.md)

### Keeping Documentation Updated

- Update after each deployment
- Document all incidents
- Record configuration changes
- Maintain runbooks

---

## On-Call Procedures

### On-Call Rotation

- **Duration**: 1 week
- **Handoff**: Friday 5:00 PM EST
- **Response Time**: 30 minutes for critical, 4 hours for non-critical

### Alert Severity

- **P0 (Critical)**: Service down, data loss
- **P1 (High)**: Severe degradation, security breach
- **P2 (Medium)**: Partial degradation, high error rates
- **P3 (Low)**: Minor issues, performance degradation

### Escalation Path

1. On-call engineer
2. Engineering manager
3. CTO
4. CEO (for critical incidents only)

---

**Last Updated**: January 2026
**Version**: 2.3.0
