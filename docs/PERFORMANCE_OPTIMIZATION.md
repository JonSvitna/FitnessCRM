# FitnessCRM Performance Optimization Guide

## Table of Contents
1. [Database Performance](#database-performance)
2. [Redis Caching](#redis-caching)
3. [API Optimization](#api-optimization)
4. [Frontend Optimization](#frontend-optimization)
5. [Nginx Optimization](#nginx-optimization)
6. [Monitoring Performance](#monitoring-performance)

---

## Database Performance

### 1. Add Database Indexes

Create a migration file to add indexes for frequently queried fields:

```sql
-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email);
CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status);
CREATE INDEX IF NOT EXISTS idx_trainers_email ON trainers(email);
CREATE INDEX IF NOT EXISTS idx_sessions_trainer_id ON sessions(trainer_id);
CREATE INDEX IF NOT EXISTS idx_sessions_client_id ON sessions(client_id);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(session_date);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_payments_client_id ON payments(client_id);
CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_assignments_trainer_id ON assignments(trainer_id);
CREATE INDEX IF NOT EXISTS idx_assignments_client_id ON assignments(client_id);
CREATE INDEX IF NOT EXISTS idx_assignments_status ON assignments(status);
CREATE INDEX IF NOT EXISTS idx_workout_plans_trainer_id ON workout_plans(trainer_id);
CREATE INDEX IF NOT EXISTS idx_progress_records_client_id ON progress_records(client_id);
CREATE INDEX IF NOT EXISTS idx_progress_records_date ON progress_records(date);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_activity_logs_timestamp ON activity_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_activity_logs_entity_type ON activity_logs(entity_type);
```

### 2. Optimize Connection Pooling

Update `backend/config/database.py`:

```python
from sqlalchemy.pool import QueuePool

# Optimal connection pool settings
SQLALCHEMY_ENGINE_OPTIONS = {
    'poolclass': QueuePool,
    'pool_size': 10,              # Base pool size
    'pool_pre_ping': True,        # Test connections before use
    'pool_recycle': 3600,         # Recycle connections after 1 hour
    'max_overflow': 20,           # Maximum extra connections
    'pool_timeout': 30,           # Timeout for getting connection
}
```

### 3. Enable Query Logging (Development Only)

```python
# In development only
SQLALCHEMY_ECHO = False  # Set to True to log all queries
SQLALCHEMY_TRACK_MODIFICATIONS = False  # Always False for performance
```

### 4. Optimize PostgreSQL Configuration

Add to `docker-compose.prod.yml` under `db` service:

```yaml
command: >
  postgres
  -c shared_buffers=256MB
  -c effective_cache_size=1GB
  -c maintenance_work_mem=64MB
  -c checkpoint_completion_target=0.9
  -c wal_buffers=16MB
  -c default_statistics_target=100
  -c random_page_cost=1.1
  -c effective_io_concurrency=200
  -c work_mem=4MB
  -c min_wal_size=1GB
  -c max_wal_size=4GB
  -c max_connections=100
```

---

## Redis Caching

### 1. Implement Flask-Caching

Install dependencies (already in `backend/Dockerfile.prod`):
```bash
pip install flask-caching redis
```

### 2. Configure Flask-Caching

Create `backend/config/cache.py`:

```python
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    'CACHE_DEFAULT_TIMEOUT': 300,  # 5 minutes
    'CACHE_KEY_PREFIX': 'fitnesscrm:'
})
```

### 3. Add Caching to Routes

Example implementation in `backend/api/routes.py`:

```python
from config.cache import cache

@app.route('/api/trainers', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_trainers():
    # This response will be cached for 5 minutes
    trainers = Trainer.query.all()
    return jsonify([t.to_dict() for t in trainers])

@app.route('/api/clients', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_clients():
    # Cache includes query parameters (pagination, filters)
    clients = Client.query.all()
    return jsonify([c.to_dict() for c in clients])
```

### 4. Cache Invalidation

```python
# Invalidate cache when data changes
@app.route('/api/trainers', methods=['POST'])
def create_trainer():
    # Create trainer logic...
    cache.delete_memoized(get_trainers)  # Clear cache
    return jsonify(trainer.to_dict()), 201
```

### 5. Cache Dashboard Statistics

```python
@app.route('/api/dashboard/stats')
@cache.cached(timeout=60, key_prefix='dashboard_stats')
def get_dashboard_stats():
    stats = {
        'total_trainers': Trainer.query.count(),
        'total_clients': Client.query.count(),
        'active_sessions': Session.query.filter_by(status='scheduled').count(),
        # ... other stats
    }
    return jsonify(stats)
```

---

## API Optimization

### 1. Enable Response Compression

Update `backend/app.py`:

```python
from flask_compress import Compress

app = Flask(__name__)
Compress(app)  # Enable gzip compression
```

### 2. Implement Pagination Helper

Create `backend/utils/pagination.py`:

```python
def paginate_query(query, page=1, per_page=20, max_per_page=100):
    """Optimized pagination helper"""
    per_page = min(per_page, max_per_page)
    
    # Use count() efficiently
    total = query.count()
    
    # Calculate pagination
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'has_prev': page > 1,
        'has_next': page * per_page < total
    }
```

### 3. Optimize Serialization

Use `marshmallow` for efficient serialization:

```python
from marshmallow import Schema, fields

class TrainerSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    email = fields.Str()
    # Only include necessary fields
    
    class Meta:
        ordered = True

trainer_schema = TrainerSchema()
trainers_schema = TrainerSchema(many=True)

# Usage
trainers = Trainer.query.all()
result = trainers_schema.dump(trainers)  # Fast serialization
```

### 4. Database Query Optimization

```python
# Bad: N+1 queries
clients = Client.query.all()
for client in clients:
    trainer = client.trainer  # Separate query for each

# Good: Eager loading
clients = Client.query.options(
    db.joinedload(Client.trainer),
    db.joinedload(Client.sessions)
).all()
```

---

## Frontend Optimization

### 1. Enable Code Splitting

Update `frontend/vite.config.js`:

```javascript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom'],
          'charts': ['chart.js'],
          'utils': ['axios', 'lodash']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  }
})
```

### 2. Implement Lazy Loading

```javascript
// Lazy load heavy components
const Analytics = lazy(() => import('./components/Analytics'));
const WorkoutBuilder = lazy(() => import('./components/WorkoutBuilder'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Route path="/analytics" component={Analytics} />
      <Route path="/workouts" component={WorkoutBuilder} />
    </Suspense>
  );
}
```

### 3. Optimize Images

```javascript
// Use WebP format with fallback
<picture>
  <source srcSet="image.webp" type="image/webp" />
  <img src="image.jpg" alt="Description" loading="lazy" />
</picture>
```

### 4. Implement Request Debouncing

```javascript
import { debounce } from 'lodash';

const searchClients = debounce((query) => {
  fetch(`/api/clients?search=${query}`)
    .then(res => res.json())
    .then(data => setResults(data));
}, 300);
```

---

## Nginx Optimization

### 1. Enable Browser Caching

Update `nginx/nginx.conf`:

```nginx
# Static assets with long cache
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    proxy_pass http://frontend;
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
}

# HTML files with short cache
location ~* \.html$ {
    proxy_pass http://frontend;
    expires 1h;
    add_header Cache-Control "public, must-revalidate";
}
```

### 2. Enable HTTP/2

```nginx
server {
    listen 443 ssl http2;  # Enable HTTP/2
    # ... rest of config
}
```

### 3. Optimize Buffer Sizes

```nginx
http {
    # Optimize buffer sizes
    client_body_buffer_size 128k;
    client_max_body_size 10m;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 8k;
    output_buffers 1 32k;
    postpone_output 1460;
}
```

---

## Monitoring Performance

### 1. Add Performance Metrics Endpoint

Create `backend/api/metrics_routes.py`:

```python
from flask import Blueprint, jsonify
import psutil
import time

metrics_bp = Blueprint('metrics', __name__)

@metrics_bp.route('/api/metrics/performance', methods=['GET'])
def get_performance_metrics():
    """Get system performance metrics"""
    return jsonify({
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'active_connections': get_active_db_connections(),
        'cache_hit_rate': get_cache_hit_rate(),
        'timestamp': time.time()
    })

@metrics_bp.route('/api/metrics/slow-queries', methods=['GET'])
def get_slow_queries():
    """Get slow database queries"""
    # Query pg_stat_statements for slow queries
    slow_queries = db.session.execute("""
        SELECT query, mean_exec_time, calls
        FROM pg_stat_statements
        ORDER BY mean_exec_time DESC
        LIMIT 10
    """)
    return jsonify([dict(q) for q in slow_queries])
```

### 2. Frontend Performance Monitoring

```javascript
// Add performance tracking
window.addEventListener('load', () => {
  const perfData = window.performance.timing;
  const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
  
  // Send to analytics
  fetch('/api/analytics/performance', {
    method: 'POST',
    body: JSON.stringify({
      page_load_time: pageLoadTime,
      dom_ready_time: perfData.domContentLoadedEventEnd - perfData.navigationStart,
      url: window.location.pathname
    })
  });
});
```

### 3. Database Query Monitoring

Enable `pg_stat_statements` in PostgreSQL:

```sql
-- In PostgreSQL
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- View slow queries
SELECT 
  query,
  mean_exec_time,
  calls,
  total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

---

## Performance Benchmarks

### Target Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time | < 200ms | Average response time |
| Page Load Time | < 2s | First Contentful Paint |
| Time to Interactive | < 3s | Interactive state |
| Database Query Time | < 100ms | Average query execution |
| Cache Hit Rate | > 80% | Redis cache hits |
| Error Rate | < 0.1% | 4xx/5xx errors |

### Load Testing

Use `locust` or `k6` for load testing:

```python
# locustfile.py
from locust import HttpUser, task, between

class FitnessCRMUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_dashboard(self):
        self.client.get("/api/dashboard/stats")
    
    @task(2)
    def view_clients(self):
        self.client.get("/api/clients")
    
    @task(1)
    def create_session(self):
        self.client.post("/api/sessions", json={
            "trainer_id": 1,
            "client_id": 1,
            "date": "2026-01-10"
        })
```

Run load test:
```bash
locust -f locustfile.py --host=http://localhost
```

---

## Continuous Optimization

### 1. Regular Performance Audits

- Run Lighthouse audits monthly
- Monitor slow query logs weekly
- Review Sentry performance data
- Check cache hit rates daily

### 2. Database Maintenance

```bash
# Weekly vacuum and analyze
docker-compose -f docker-compose.prod.yml exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "VACUUM ANALYZE;"

# Check table bloat
docker-compose -f docker-compose.prod.yml exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema') ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

### 3. CDN Integration (Optional)

For static assets, consider using a CDN:
- Cloudflare (free tier available)
- AWS CloudFront
- Fastly

---

**Last Updated**: January 2026
