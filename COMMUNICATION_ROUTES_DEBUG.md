# Communication Routes 404 Debug Guide

## Issue
All communication tools (Messages, SMS, Campaigns, Automation) are returning 404 Not Found errors.

## Root Cause Analysis

The communication routes are conditionally imported and registered in `backend/app.py`:

```python
# Routes are imported with try/except
sms_bp = None
try:
    from api.sms_routes import sms_bp
except Exception as e:
    print(f"Warning: Failed to import SMS routes: {e}")

# Then conditionally registered
if sms_bp:
    app.register_blueprint(sms_bp)
```

If the import fails, `sms_bp` remains `None` and the routes are never registered, causing 404 errors.

## Possible Causes

1. **Missing Dependencies**: Required packages not installed in production
   - Flask-SocketIO (for messages)
   - Twilio (for SMS)
   - Flask-Mail (for campaigns)

2. **Import Errors**: Syntax errors or missing imports in route files
   - Check `backend/api/message_routes.py`
   - Check `backend/api/sms_routes.py`
   - Check `backend/api/campaign_routes.py`
   - Check `backend/api/automation_routes.py`

3. **Database Models Missing**: Models not created in database
   - MessageThread, Message, MessageAttachment
   - SMSLog, SMSTemplate, SMSSchedule
   - EmailCampaign, EmailTemplate, CampaignRecipient
   - AutomationRule, AutomationLog

## Debugging Steps

### 1. Check Backend Logs
Look for warnings like:
```
Warning: Failed to import SMS routes: ...
Warning: Failed to import Campaign routes: ...
Warning: Failed to import Automation routes: ...
Warning: Failed to import message routes: ...
```

### 2. Check Root Endpoint
Call `GET /` and check the `communication_features` field:
```json
{
  "communication_features": {
    "sms": false,  // Should be true if routes are registered
    "campaigns": false,
    "automation": false,
    "messages": false
  }
}
```

### 3. Verify Dependencies
Check if all packages are installed:
```bash
pip list | grep -i "flask-socketio\|twilio\|flask-mail"
```

### 4. Test Route Imports
Try importing the routes directly:
```python
from api.sms_routes import sms_bp
from api.campaign_routes import campaign_bp
from api.automation_routes import automation_bp
from api.message_routes import message_bp
```

### 5. Check Database Tables
Verify all required tables exist:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
  'message_threads', 'messages', 'message_attachments',
  'sms_logs', 'sms_templates', 'sms_schedules',
  'email_campaigns', 'email_templates', 'campaign_recipients',
  'automation_rules', 'automation_logs'
);
```

## Solutions

### Solution 1: Install Missing Dependencies
```bash
pip install Flask-SocketIO==5.3.6 python-socketio==5.11.0 twilio>=9.1.0 Flask-Mail==0.9.1
```

### Solution 2: Create Missing Database Tables
```python
from models.database import db
db.create_all()
```

### Solution 3: Fix Import Errors
Check each route file for:
- Missing imports
- Syntax errors
- Circular imports
- Missing model definitions

### Solution 4: Check Production Environment
- Verify `requirements.txt` is installed
- Check Railway/Render logs for import errors
- Ensure database migrations have run

## Expected Behavior After Fix

1. Backend logs should show:
   ```
   SMS routes registered
   Campaign routes registered
   Automation routes registered
   Message routes registered
   ```

2. Root endpoint should show:
   ```json
   {
     "communication_features": {
       "sms": true,
       "campaigns": true,
       "automation": true,
       "messages": true
     }
   }
   ```

3. API calls should return 200 instead of 404:
   - `GET /api/sms/templates` → 200 OK
   - `GET /api/campaigns` → 200 OK
   - `GET /api/automation/rules` → 200 OK
   - `GET /api/messages/threads` → 200 OK

## Next Steps

1. Check production logs for import errors
2. Verify all dependencies are installed
3. Check database tables exist
4. Test route imports directly
5. Redeploy if needed

