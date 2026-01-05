#!/bin/bash

##############################################################################
# FitnessCRM System Health Check Script
# 
# This script performs comprehensive health checks on all FitnessCRM
# components and services.
#
# Usage: ./health-check.sh [--verbose] [--json]
##############################################################################

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VERBOSE=false
JSON_OUTPUT=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--verbose] [--json]"
            echo "  --verbose, -v    Show detailed output"
            echo "  --json           Output results in JSON format"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Initialize results
declare -A CHECKS
OVERALL_STATUS="healthy"

# Log functions
log() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
    fi
}

success() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${GREEN}✓${NC} $1"
    fi
}

failure() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${RED}✗${NC} $1"
    fi
    OVERALL_STATUS="unhealthy"
}

warning() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${YELLOW}⚠${NC} $1"
    fi
}

# Change to project directory
cd "$PROJECT_DIR"

# Header
if [ "$JSON_OUTPUT" = false ]; then
    echo "========================================="
    echo "FitnessCRM System Health Check"
    echo "========================================="
    echo ""
fi

# Check 1: Docker Daemon
log "Checking Docker daemon..."
if docker info &>/dev/null; then
    success "Docker daemon is running"
    CHECKS["docker"]="ok"
else
    failure "Docker daemon is not running"
    CHECKS["docker"]="fail"
fi

# Check 2: Docker Compose
log "Checking Docker Compose..."
if command -v docker-compose &>/dev/null; then
    COMPOSE_VERSION=$(docker-compose version --short)
    success "Docker Compose is installed (version: $COMPOSE_VERSION)"
    CHECKS["docker_compose"]="ok"
else
    failure "Docker Compose is not installed"
    CHECKS["docker_compose"]="fail"
fi

# Check 3: Database Container
log "Checking database container..."
if docker-compose -f docker-compose.prod.yml ps db | grep -q "Up"; then
    DB_STATUS=$(docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U "${POSTGRES_USER:-fitnesscrm_user}" 2>&1)
    if echo "$DB_STATUS" | grep -q "accepting connections"; then
        success "Database container is running and accepting connections"
        CHECKS["database"]="ok"
        
        # Check database size
        if [ "$VERBOSE" = true ]; then
            DB_SIZE=$(docker-compose -f docker-compose.prod.yml exec -T db psql -U "${POSTGRES_USER:-fitnesscrm_user}" -d "${POSTGRES_DB:-fitnesscrm_prod}" -t -c "SELECT pg_size_pretty(pg_database_size('${POSTGRES_DB:-fitnesscrm_prod}'));" 2>/dev/null | xargs)
            log "  Database size: $DB_SIZE"
        fi
    else
        failure "Database is not accepting connections"
        CHECKS["database"]="fail"
    fi
else
    failure "Database container is not running"
    CHECKS["database"]="fail"
fi

# Check 4: Redis Container
log "Checking Redis container..."
if docker-compose -f docker-compose.prod.yml ps redis | grep -q "Up"; then
    if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli -a "${REDIS_PASSWORD:-changeme}" ping 2>/dev/null | grep -q "PONG"; then
        success "Redis container is running and responding"
        CHECKS["redis"]="ok"
        
        # Check Redis memory usage
        if [ "$VERBOSE" = true ]; then
            REDIS_MEMORY=$(docker-compose -f docker-compose.prod.yml exec -T redis redis-cli -a "${REDIS_PASSWORD:-changeme}" INFO memory 2>/dev/null | grep "used_memory_human:" | cut -d: -f2 | tr -d '\r')
            log "  Redis memory usage: $REDIS_MEMORY"
        fi
    else
        failure "Redis is not responding"
        CHECKS["redis"]="fail"
    fi
else
    failure "Redis container is not running"
    CHECKS["redis"]="fail"
fi

# Check 5: Backend Container
log "Checking backend container..."
if docker-compose -f docker-compose.prod.yml ps backend | grep -q "Up"; then
    # Check health endpoint
    HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/health 2>/dev/null || echo "000")
    if [ "$HEALTH_RESPONSE" = "200" ]; then
        success "Backend container is running and healthy"
        CHECKS["backend"]="ok"
        
        # Get version info
        if [ "$VERBOSE" = true ]; then
            VERSION=$(curl -s http://localhost:5000/api/health 2>/dev/null | grep -o '"version":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
            log "  Backend version: $VERSION"
        fi
    else
        failure "Backend is not responding (HTTP $HEALTH_RESPONSE)"
        CHECKS["backend"]="fail"
    fi
else
    failure "Backend container is not running"
    CHECKS["backend"]="fail"
fi

# Check 6: Frontend Container
log "Checking frontend container..."
if docker-compose -f docker-compose.prod.yml ps frontend | grep -q "Up"; then
    FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
    if [ "$FRONTEND_RESPONSE" = "200" ]; then
        success "Frontend container is running and serving content"
        CHECKS["frontend"]="ok"
    else
        failure "Frontend is not responding (HTTP $FRONTEND_RESPONSE)"
        CHECKS["frontend"]="fail"
    fi
else
    failure "Frontend container is not running"
    CHECKS["frontend"]="fail"
fi

# Check 7: Nginx Container
log "Checking Nginx container..."
if docker-compose -f docker-compose.prod.yml ps nginx | grep -q "Up"; then
    NGINX_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null || echo "000")
    if [ "$NGINX_RESPONSE" = "200" ] || [ "$NGINX_RESPONSE" = "301" ] || [ "$NGINX_RESPONSE" = "302" ]; then
        success "Nginx container is running and routing traffic"
        CHECKS["nginx"]="ok"
    else
        failure "Nginx is not responding properly (HTTP $NGINX_RESPONSE)"
        CHECKS["nginx"]="fail"
    fi
else
    failure "Nginx container is not running"
    CHECKS["nginx"]="fail"
fi

# Check 8: Disk Space
log "Checking disk space..."
DISK_USAGE=$(df -h "$PROJECT_DIR" | awk 'NR==2 {print $5}' | tr -d '%')
if [ "$DISK_USAGE" -lt 80 ]; then
    success "Disk space is adequate ($DISK_USAGE% used)"
    CHECKS["disk"]="ok"
elif [ "$DISK_USAGE" -lt 90 ]; then
    warning "Disk space is getting low ($DISK_USAGE% used)"
    CHECKS["disk"]="warning"
else
    failure "Disk space is critically low ($DISK_USAGE% used)"
    CHECKS["disk"]="fail"
fi

# Check 9: Memory Usage
log "Checking memory usage..."
if command -v free &>/dev/null; then
    MEMORY_USAGE=$(free | awk 'NR==2 {printf "%.0f", $3*100/$2}')
    if [ "$MEMORY_USAGE" -lt 80 ]; then
        success "Memory usage is normal ($MEMORY_USAGE% used)"
        CHECKS["memory"]="ok"
    elif [ "$MEMORY_USAGE" -lt 90 ]; then
        warning "Memory usage is high ($MEMORY_USAGE% used)"
        CHECKS["memory"]="warning"
    else
        failure "Memory usage is critically high ($MEMORY_USAGE% used)"
        CHECKS["memory"]="fail"
    fi
fi

# Check 10: Docker Volumes
log "Checking Docker volumes..."
POSTGRES_VOLUME=$(docker volume ls | grep "postgres_data_prod" || echo "")
REDIS_VOLUME=$(docker volume ls | grep "redis_data_prod" || echo "")
if [ -n "$POSTGRES_VOLUME" ] && [ -n "$REDIS_VOLUME" ]; then
    success "Required Docker volumes exist"
    CHECKS["volumes"]="ok"
else
    failure "Some Docker volumes are missing"
    CHECKS["volumes"]="fail"
fi

# Output results
if [ "$JSON_OUTPUT" = true ]; then
    # JSON output
    echo "{"
    echo "  \"timestamp\": \"$(date -Iseconds)\","
    echo "  \"overall_status\": \"$OVERALL_STATUS\","
    echo "  \"checks\": {"
    FIRST=true
    for key in "${!CHECKS[@]}"; do
        if [ "$FIRST" = false ]; then
            echo ","
        fi
        echo -n "    \"$key\": \"${CHECKS[$key]}\""
        FIRST=false
    done
    echo ""
    echo "  }"
    echo "}"
else
    # Human-readable summary
    echo ""
    echo "========================================="
    echo "Health Check Summary"
    echo "========================================="
    echo "Overall Status: $OVERALL_STATUS"
    echo ""
    echo "Component Status:"
    for key in "${!CHECKS[@]}"; do
        status="${CHECKS[$key]}"
        if [ "$status" = "ok" ]; then
            echo -e "  ${GREEN}✓${NC} $key"
        elif [ "$status" = "warning" ]; then
            echo -e "  ${YELLOW}⚠${NC} $key"
        else
            echo -e "  ${RED}✗${NC} $key"
        fi
    done
    echo "========================================="
fi

# Exit code based on overall status
if [ "$OVERALL_STATUS" = "healthy" ]; then
    exit 0
else
    exit 1
fi
