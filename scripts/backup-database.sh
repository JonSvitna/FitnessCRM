#!/bin/bash

##############################################################################
# FitnessCRM Automated Database Backup Script
# 
# This script creates automated backups of the PostgreSQL database and
# optionally uploads them to AWS S3 for off-site storage.
#
# Usage: ./backup-database.sh [--s3] [--retention DAYS]
##############################################################################

set -e  # Exit on error
set -o pipefail  # Exit on pipe failure

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_ONLY=$(date +%Y%m%d)
BACKUP_FILE="fitnesscrm_backup_${TIMESTAMP}.sql.gz"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
UPLOAD_TO_S3=false
S3_BUCKET="${BACKUP_S3_BUCKET:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --s3)
            UPLOAD_TO_S3=true
            shift
            ;;
        --retention)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--s3] [--retention DAYS]"
            echo "  --s3             Upload backup to S3"
            echo "  --retention DAYS Number of days to keep backups (default: 30)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Load environment variables
if [ -f "$PROJECT_DIR/.env.production" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env.production" | xargs)
fi

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

# Create backup directory
log "Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Check if Docker Compose is running
log "Checking Docker services..."
cd "$PROJECT_DIR"
if ! docker-compose -f docker-compose.prod.yml ps db | grep -q "Up"; then
    error "Database container is not running!"
    exit 1
fi

# Perform backup
log "Starting database backup..."
log "Backup file: $BACKUP_FILE"

if docker-compose -f docker-compose.prod.yml exec -T db pg_dump \
    -U "${POSTGRES_USER:-fitnesscrm_user}" \
    -d "${POSTGRES_DB:-fitnesscrm_prod}" \
    --clean \
    --if-exists \
    | gzip > "$BACKUP_DIR/$BACKUP_FILE"; then
    
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    log "Backup completed successfully!"
    log "Backup size: $BACKUP_SIZE"
    log "Backup location: $BACKUP_DIR/$BACKUP_FILE"
else
    error "Backup failed!"
    exit 1
fi

# Verify backup integrity
log "Verifying backup integrity..."
if gunzip -t "$BACKUP_DIR/$BACKUP_FILE" 2>/dev/null; then
    log "Backup integrity verified!"
else
    error "Backup verification failed! File may be corrupted."
    exit 1
fi

# Create a symlink to latest backup
ln -sf "$BACKUP_FILE" "$BACKUP_DIR/latest.sql.gz"
log "Created symlink to latest backup"

# Upload to S3 if requested
if [ "$UPLOAD_TO_S3" = true ]; then
    if [ -z "$S3_BUCKET" ]; then
        warning "S3_BUCKET not configured. Skipping S3 upload."
    else
        log "Uploading backup to S3: s3://$S3_BUCKET/postgres/"
        
        if command -v aws &> /dev/null; then
            if aws s3 cp "$BACKUP_DIR/$BACKUP_FILE" "s3://$S3_BUCKET/postgres/$DATE_ONLY/$BACKUP_FILE"; then
                log "Successfully uploaded to S3!"
            else
                error "Failed to upload to S3"
            fi
        else
            error "AWS CLI not installed. Cannot upload to S3."
        fi
    fi
fi

# Remove old backups
log "Cleaning up old backups (older than $RETENTION_DAYS days)..."
DELETED_COUNT=$(find "$BACKUP_DIR" -name "fitnesscrm_backup_*.sql.gz" -type f -mtime +"$RETENTION_DAYS" 2>/dev/null | wc -l)
find "$BACKUP_DIR" -name "fitnesscrm_backup_*.sql.gz" -type f -mtime +"$RETENTION_DAYS" -delete
log "Removed $DELETED_COUNT old backup(s)"

# List recent backups
log "Recent backups:"
ls -lh "$BACKUP_DIR"/fitnesscrm_backup_*.sql.gz | tail -5 || true

# Summary
log "========================================="
log "Backup Summary"
log "========================================="
log "Backup file: $BACKUP_FILE"
log "Backup size: $BACKUP_SIZE"
log "Location: $BACKUP_DIR"
log "Retention: $RETENTION_DAYS days"
if [ "$UPLOAD_TO_S3" = true ] && [ -n "$S3_BUCKET" ]; then
    log "S3 Upload: Enabled (s3://$S3_BUCKET/postgres/$DATE_ONLY/)"
fi
log "========================================="
log "Backup completed successfully!"

exit 0
