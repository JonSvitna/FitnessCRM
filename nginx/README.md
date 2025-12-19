# Nginx Configuration

This directory contains the Nginx reverse proxy configuration for FitnessCRM production deployment.

## Directory Structure

```
nginx/
├── nginx.conf          # Main Nginx configuration
├── ssl/                # SSL certificates (add your certificates here)
│   ├── cert.pem       # SSL certificate (not included in repo)
│   └── key.pem        # SSL private key (not included in repo)
└── logs/              # Nginx logs (mapped from container)
```

## SSL Certificate Setup

### Option 1: Let's Encrypt (Recommended for Production)

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./ssl/key.pem
sudo chmod 600 ./ssl/key.pem
```

### Option 2: Self-Signed Certificate (Development/Testing)

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ./ssl/key.pem \
  -out ./ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Set proper permissions
chmod 600 ./ssl/key.pem
chmod 644 ./ssl/cert.pem
```

### Enable HTTPS

After setting up SSL certificates, uncomment the HTTPS server block in `nginx.conf`:

1. Uncomment the `server` block starting with `listen 443 ssl http2`
2. Update `server_name` with your actual domain
3. Uncomment the HTTP to HTTPS redirect: `return 301 https://$server_name$request_uri;`
4. Restart nginx: `docker-compose -f docker-compose.prod.yml restart nginx`

## Configuration Features

### Security Headers
- X-Frame-Options: Prevents clickjacking
- X-Content-Type-Options: Prevents MIME sniffing
- X-XSS-Protection: Enables XSS filtering
- Referrer-Policy: Controls referrer information
- Permissions-Policy: Restricts browser features

### Rate Limiting
- API endpoints: 10 requests/second (burst 20)
- Authentication: 5 requests/second (burst 5)
- General pages: 30 requests/second (burst 50)
- Connection limit: 10 concurrent connections per IP

### Performance Optimizations
- Gzip compression for text-based content
- Connection keep-alive
- Upstream keepalive connections
- Static file caching (1 year)
- Efficient buffering settings

### Load Balancing
- Backend upstream with health checks
- Frontend upstream with health checks
- Automatic failover on upstream failures

## Testing Configuration

Test the nginx configuration:

```bash
# Test configuration syntax
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Reload configuration (without downtime)
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

# View logs
docker-compose -f docker-compose.prod.yml logs -f nginx
```

## Monitoring

View real-time logs:

```bash
# Access logs
tail -f logs/access.log

# Error logs
tail -f logs/error.log

# Both
tail -f logs/access.log logs/error.log
```

## Common Issues

### 502 Bad Gateway
- Backend service not running
- Check: `docker-compose -f docker-compose.prod.yml ps backend`
- Solution: `docker-compose -f docker-compose.prod.yml restart backend`

### 413 Request Entity Too Large
- File upload exceeds `client_max_body_size`
- Edit `nginx.conf` and increase the value
- Reload: `docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload`

### SSL Certificate Errors
- Check certificate paths in configuration
- Verify file permissions: `ls -l ssl/`
- Ensure certificates are valid: `openssl x509 -in ssl/cert.pem -text -noout`

## Customization

### Adjusting Rate Limits

Edit the `limit_req_zone` directives in `nginx.conf`:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=20r/s;  # Increase to 20 req/s
```

### Adding Custom Headers

Add to the `server` block:

```nginx
add_header Custom-Header "value" always;
```

### Enabling CORS (if needed)

Add to API location block:

```nginx
add_header Access-Control-Allow-Origin "*" always;
add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
```

## Production Checklist

- [ ] SSL certificates installed
- [ ] HTTPS enabled and tested
- [ ] HTTP to HTTPS redirect enabled
- [ ] Domain name updated in configuration
- [ ] Rate limits adjusted for expected traffic
- [ ] Logs directory has proper permissions
- [ ] Health checks working
- [ ] Security headers verified
- [ ] Load testing completed

## Resources

- [Nginx Documentation](https://nginx.org/en/docs/)
- [SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
