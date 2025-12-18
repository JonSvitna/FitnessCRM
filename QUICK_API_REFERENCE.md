# Quick API Reference - Communication Routes

## Base URL
- **Development**: `http://localhost:5000`
- **Production**: Set via `VITE_API_URL` environment variable

## Quick Test Commands

### Check if Routes are Registered
```bash
curl http://localhost:5000/ | jq '.communication_features'
```

### Messages API

```bash
# Get threads
GET /api/messages/threads?user_type=trainer&user_id=1

# Create thread
POST /api/messages/threads
Body: {"participant_type": "trainer", "participant_id": 1, "other_participant_type": "client", "other_participant_id": 2}

# Send message
POST /api/messages/threads/{thread_id}/messages
Body: {"sender_type": "trainer", "sender_id": 1, "content": "Hello"}

# Unread count
GET /api/messages/unread-count?user_type=trainer&user_id=1
```

### SMS API

```bash
# Send SMS
POST /api/sms/send
Body: {"to_number": "+1234567890", "message": "Hello", "client_id": 1}

# Get templates
GET /api/sms/templates

# Create template
POST /api/sms/templates
Body: {"name": "Reminder", "category": "reminder", "message": "Reminder text"}

# Get logs
GET /api/sms/logs

# Get analytics
GET /api/sms/analytics
```

### Campaigns API

```bash
# Get campaigns
GET /api/campaigns

# Create campaign
POST /api/campaigns
Body: {"name": "Newsletter", "subject": "Subject", "html_body": "<p>Body</p>", "segment_type": "all"}

# Send campaign
POST /api/campaigns/{id}/send

# Get templates
GET /api/campaigns/templates

# Create template
POST /api/campaigns/templates
Body: {"name": "Template", "subject": "Subject", "html_body": "<p>Body</p>"}

# Get analytics
GET /api/campaigns/{id}/analytics
```

### Automation API

```bash
# Get rules
GET /api/automation/rules

# Create rule
POST /api/automation/rules
Body: {"name": "Rule", "rule_type": "session_reminder", "trigger_event": "session_scheduled", "action_type": "email", "enabled": true}

# Execute rule
POST /api/automation/rules/{id}/execute

# Toggle rule
POST /api/automation/rules/{id}/toggle

# Get logs
GET /api/automation/logs

# Get analytics
GET /api/automation/analytics

# Process triggers (background worker)
POST /api/automation/process-triggers
```

## Frontend Usage

```javascript
import { smsAPI, campaignAPI, automationAPI, messageAPI } from './api.js';

// SMS
await smsAPI.send({ to_number: '+1234567890', message: 'Hello' });
await smsAPI.getTemplates();

// Campaigns
await campaignAPI.getCampaigns();
await campaignAPI.createCampaign({ name: 'Campaign', subject: 'Subject', html_body: '<p>Body</p>' });

// Automation
await automationAPI.getRules();
await automationAPI.createRule({ name: 'Rule', rule_type: 'session_reminder', ... });

// Messages
await messageAPI.getThreads({ user_type: 'trainer', user_id: 1 });
await messageAPI.createThread({ participant_type: 'trainer', participant_id: 1, ... });
```

## Browser Console Test

```javascript
const API_URL = 'http://localhost:5000'; // Change to your backend URL

// Test all routes
async function testAll() {
  const routes = {
    sms: '/api/sms/templates',
    campaigns: '/api/campaigns',
    automation: '/api/automation/rules',
    messages: '/api/messages/threads'
  };
  
  for (const [name, route] of Object.entries(routes)) {
    try {
      const res = await fetch(`${API_URL}${route}`);
      console.log(`${name}:`, res.status, res.status === 200 ? '✅' : '❌');
    } catch (e) {
      console.error(`${name}:`, '❌ Error', e.message);
    }
  }
}

testAll();
```

