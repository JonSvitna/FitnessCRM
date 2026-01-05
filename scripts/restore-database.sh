#!/bin/bash

##############################################################################
# FitnessCRM Database Restore Script
# 
# This script restores the PostgreSQL database from a backup file.
#
# Usage: ./restore-database.sh <backup_file>
#        ./restore-database.sh --latest
##############################################################################

set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Log function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Check arguments
if [ $# -eq 0 ]; then
    error "No backup file specified!"
    echo "Usage: $0 <backup_file>"
    echo "       $0 --latest"
    exit 1
fi

# Load environment variables
if [ -f "$PROJECT_DIR/.env.production" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env.production" | xargs)
fi

# Determine backup file
if [ "$1" = "--latest" ]; then
    BACKUP_FILE="$BACKUP_DIR/latest.sql.gz"
    if [ ! -f "$BACKUP_FILE" ]; then
        error "Latest backup not found at: $BACKUP_FILE"
        exit 1
    fi
    log "Using latest backup: $BACKUP_FILE"
else
    BACKUP_FILE="$1"
    if [ ! -f "$BACKUP_FILE" ]; then
        error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
fi

# Verify backup integrity
log "Verifying backup integrity..."
if ! gunzip -t "$BACKUP_FILE" 2>/dev/null; then
    error "Backup file is corrupted or invalid!"
    exit 1
fi
log "Backup integrity verified!"

# Get backup info
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log "Backup size: $BACKUP_SIZE"

# Warning and confirmation
warning "========================================="
warning "WARNING: This will replace the current database!"
warning "Database: ${POSTGRES_DB:-fitnesscrm_prod}"
warning "Backup file: $BACKUP_FILE"
warning "========================================="
read -p "Are you sure you want to continue? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    log "Restore cancelled by user."
    exit 0
fi

# Change to project directory
cd "$PROJECT_DIR"

# Check if Docker Compose is running
log "Checking Docker services..."
if ! docker-compose -f docker-compose.prod.yml ps db | grep -q "Up"; then
    error "Database container is not running!"
    exit 1
fi

# Stop backend to prevent connections
log "Stopping backend service..."
docker-compose -f docker-compose.prod.yml stop backend

# Wait for active connections to close
log "Waiting for active database connections to close..."
sleep 5

# Terminate remaining connections
log "Terminating remaining database connections..."
docker-compose -f docker-compose.prod.yml exec -T db psql \
    -U "${POSTGRES_USER:-fitnesscrm_user}" \
    -d postgres \
    -c "SELECT pg_terminate_backend(pg_stat_activity.pid) 
        FROM pg_stat_activity 
        WHERE pg_stat_activity.datname = '${POSTGRES_DB:-fitnesscrm_prod}' 
        AND pid <> pg_backend_pid();" || true

# Perform restore
log "Starting database restore..."
log "This may take several minutes depending on database size..."

if gunzip -c "$BACKUP_FILE" | docker-compose -f docker-compose.prod.yml exec -T db psql \
    -U "${POSTGRES_USER:-fitnesscrm_user}" \
    -d "${POSTGRES_DB:-fitnesscrm_prod}"; then
    
    log "Database restored successfully!"
else
    error "Database restore failed!"
    error "Please check the logs for details."
    exit 1
fi

# Restart backend
log "Restarting backend service..."
docker-compose -f docker-compose.prod.yml start backend

# Wait for backend to be healthy
log "Waiting for backend to be healthy..."
sleep 10

# Verify restore
log "Verifying database connection..."
if docker-compose -f docker-compose.prod.yml exec -T backend python -c "from app import db; db.engine.execute('SELECT 1')" &>/dev/null; then
    log "Database connection verified!"
else
    warning "Could not verify database connection. Please check manually."
fi

# Summary
log "========================================="
log "Restore Summary"
log "========================================="
log "Backup file: $BACKUP_FILE"
log "Database: ${POSTGRES_DB:-fitnesscrm_prod}"
log "Status: Completed"
log "========================================="
log "Database restore completed successfully!"
log ""
log "Next steps:"
log "1. Verify application functionality"
log "2. Check logs: docker-compose -f docker-compose.prod.yml logs"
log "3. Test critical features"

exit 0
