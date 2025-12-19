# Database Migration Guide

## Fix for "column sessions.end_time does not exist" Error

If you encounter the error:
```
(psycopg2.errors.UndefinedColumn) column sessions.end_time does not exist
```

This means your database schema is missing the `end_time` column that was added to the `Session` model.

### Running the Migration

#### Option 1: Using the Migration Script (Recommended for Existing Databases)

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Run the migration script**:
   ```bash
   python migrate_add_end_time.py
   ```

   The script will:
   - Check if the `end_time` column already exists
   - Add the column if it doesn't exist
   - Populate `end_time` values for existing sessions based on `session_date + duration`

3. **Verify the migration**:
   ```bash
   # Connect to your database and check the sessions table
   psql $DATABASE_URL -c "SELECT column_name FROM information_schema.columns WHERE table_name='sessions';"
   ```

#### Option 2: For New Database Installations

If you're setting up a fresh database, simply run:
```bash
python init_db.py
```

This will create all tables with the correct schema, including the `end_time` column.

#### Option 3: Manual SQL (Advanced Users)

If you prefer to run the SQL manually:

```sql
-- Add the column
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS end_time TIMESTAMP;

-- Populate values for existing sessions
UPDATE sessions 
SET end_time = session_date + (duration || ' minutes')::INTERVAL
WHERE end_time IS NULL AND session_date IS NOT NULL AND duration IS NOT NULL;
```

### What This Migration Does

The `end_time` column stores the calculated end time of each session based on:
- `session_date` - The start date/time of the session
- `duration` - The duration in minutes

Previously, `end_time` was calculated on-the-fly in the application code. Adding it as a database column improves query performance, especially for:
- Checking for scheduling conflicts
- Filtering sessions by time range
- Calendar exports

### Deployment Considerations

#### Railway/Production Deployment

1. **Before deploying the code changes**, run the migration script on your production database:
   ```bash
   # From your local machine with Railway CLI installed and authenticated
   # Navigate to the backend directory first
   cd backend
   railway run python migrate_add_end_time.py
   ```

2. **Or set the DATABASE_URL and run locally**:
   ```bash
   # Get your DATABASE_URL from Railway dashboard
   export DATABASE_URL="your-railway-database-url"
   cd backend
   python migrate_add_end_time.py
   ```

#### Docker Deployments

Add the migration to your deployment script or run it as an init container:
```dockerfile
RUN python backend/migrate_add_end_time.py
```

### Troubleshooting

**Error: "relation 'sessions' does not exist"**
- Your database hasn't been initialized yet
- Run `python init_db.py` first

**Error: "column end_time already exists"**
- The migration has already been applied
- No action needed

**Permission denied errors**
- Ensure your database user has ALTER TABLE permissions
- Contact your database administrator if needed

### Rollback (Not Recommended)

If you need to remove the column:
```sql
ALTER TABLE sessions DROP COLUMN IF EXISTS end_time;
```

**Note**: After rollback, the application will fail with the original error until the column is re-added.
