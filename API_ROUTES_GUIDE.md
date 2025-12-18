# API Routes Calling Guide

This guide shows how to call the Fitness CRM API routes, especially the communication routes.

## Base URL

**Development**: `http://localhost:5000`  
**Production**: `https://your-backend-url.railway.app` (or your deployed backend URL)

## Authentication

Currently, the API doesn't require authentication. In production, you should add authentication.

## Communication Routes

### 1. Messages API (`/api/messages`)

#### Get Message Threads
```bash
# Using curl
curl -X GET "http://localhost:5000/api/messages/threads?user_type=trainer&user_id=1"

# Using fetch (JavaScript)
fetch('http://localhost:5000/api/messages/threads?user_type=trainer&user_id=1')
  .then(response => response.json())
  .then(data => console.log(data));
```

#### Create Message Thread
```bash
curl -X POST "http://localhost:5000/api/messages/threads" \
  -H "Content-Type: application/json" \
  -d '{
    "participant_type": "trainer",
    "participant_id": 1,
    "other_participant_type": "client",
    "other_participant_id": 2,
    "subject": "Training Plan Discussion"
  }'
```

#### Send Message
```bash
curl -X POST "http://localhost:5000/api/messages/threads/1/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "sender_type": "trainer",
    "sender_id": 1,
    "content": "Hello! Here is your training plan."
  }'
```

#### Get Unread Count
```bash
curl -X GET "http://localhost:5000/api/messages/unread-count?user_type=trainer&user_id=1"
```

---

### 2. SMS API (`/api/sms`)

#### Send SMS
```bash
curl -X POST "http://localhost:5000/api/sms/send" \
  -H "Content-Type: application/json" \
  -d '{
    "to_number": "+1234567890",
    "message": "Your training session is tomorrow at 10 AM",
    "client_id": 1
  }'
```

#### Get SMS Templates
```bash
curl -X GET "http://localhost:5000/api/sms/templates"
```

#### Create SMS Template
```bash
curl -X POST "http://localhost:5000/api/sms/templates" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Session Reminder",
    "category": "reminder",
    "message": "Reminder: Your training session is tomorrow at {time}"
  }'
```

#### Get SMS Logs
```bash
curl -X GET "http://localhost:5000/api/sms/logs?page=1&per_page=50"
```

#### Get SMS Analytics
```bash
curl -X GET "http://localhost:5000/api/sms/analytics"
```

---

### 3. Email Campaigns API (`/api/campaigns`)

#### Get Campaigns
```bash
curl -X GET "http://localhost:5000/api/campaigns?page=1&per_page=50"
```

#### Create Campaign
```bash
curl -X POST "http://localhost:5000/api/campaigns" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monthly Newsletter",
    "description": "Monthly fitness tips",
    "subject": "Your Monthly Fitness Newsletter",
    "html_body": "<h1>Welcome!</h1><p>This is your monthly newsletter.</p>",
    "text_body": "Welcome! This is your monthly newsletter.",
    "segment_type": "all",
    "send_immediately": false
  }'
```

#### Send Campaign
```bash
curl -X POST "http://localhost:5000/api/campaigns/1/send"
```

#### Get Email Templates
```bash
curl -X GET "http://localhost:5000/api/campaigns/templates"
```

#### Create Email Template
```bash
curl -X POST "http://localhost:5000/api/campaigns/templates" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Welcome Email",
    "category": "welcome",
    "subject": "Welcome to FitnessCRM!",
    "html_body": "<h1>Welcome!</h1><p>Thank you for joining.</p>",
    "text_body": "Welcome! Thank you for joining."
  }'
```

#### Get Campaign Analytics
```bash
curl -X GET "http://localhost:5000/api/campaigns/1/analytics"
```

---

### 4. Automation API (`/api/automation`)

#### Get Automation Rules
```bash
curl -X GET "http://localhost:5000/api/automation/rules"
```

#### Create Automation Rule
```bash
curl -X POST "http://localhost:5000/api/automation/rules" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Session Reminder 24h",
    "description": "Send reminder 24 hours before session",
    "rule_type": "session_reminder",
    "trigger_event": "session_scheduled",
    "trigger_conditions": {"hours_before": 24},
    "action_type": "email",
    "target_audience": "clients",
    "enabled": true
  }'
```

#### Execute Rule Manually
```bash
curl -X POST "http://localhost:5000/api/automation/rules/1/execute"
```

#### Toggle Rule (Enable/Disable)
```bash
curl -X POST "http://localhost:5000/api/automation/rules/1/toggle"
```

#### Get Automation Logs
```bash
curl -X GET "http://localhost:5000/api/automation/logs?page=1&per_page=50"
```

#### Get Automation Analytics
```bash
curl -X GET "http://localhost:5000/api/automation/analytics"
```

#### Process Time-Based Triggers (Background Worker)
```bash
curl -X POST "http://localhost:5000/api/automation/process-triggers"
```

---

## Testing Routes from Frontend

### Using the API Client (frontend/src/api.js)

The frontend already has API functions set up:

```javascript
import { smsAPI, campaignAPI, automationAPI, messageAPI } from './api.js';

// SMS
const response = await smsAPI.send({
  to_number: '+1234567890',
  message: 'Hello!'
});

// Campaigns
const campaigns = await campaignAPI.getCampaigns({ page: 1 });

// Automation
const rules = await automationAPI.getRules();

// Messages
const threads = await messageAPI.getThreads({ user_type: 'trainer', user_id: 1 });
```

### Using Fetch Directly

```javascript
// Get SMS templates
fetch('http://localhost:5000/api/sms/templates')
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log('Templates:', data.templates);
  })
  .catch(error => {
    console.error('Error:', error);
  });

// Send SMS
fetch('http://localhost:5000/api/sms/send', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    to_number: '+1234567890',
    message: 'Test message'
  })
})
  .then(response => response.json())
  .then(data => console.log('Result:', data));
```

---

## Testing with Browser Console

Open browser console (F12) and run:

```javascript
// Test if routes are available
async function testRoutes() {
  const baseUrl = 'http://localhost:5000'; // Change to your backend URL
  
  // Test SMS
  try {
    const sms = await fetch(`${baseUrl}/api/sms/templates`);
    console.log('SMS Status:', sms.status, await sms.json());
  } catch (e) {
    console.error('SMS Error:', e);
  }
  
  // Test Campaigns
  try {
    const campaigns = await fetch(`${baseUrl}/api/campaigns`);
    console.log('Campaigns Status:', campaigns.status, await campaigns.json());
  } catch (e) {
    console.error('Campaigns Error:', e);
  }
  
  // Test Automation
  try {
    const automation = await fetch(`${baseUrl}/api/automation/rules`);
    console.log('Automation Status:', automation.status, await automation.json());
  } catch (e) {
    console.error('Automation Error:', e);
  }
  
  // Test Messages
  try {
    const messages = await fetch(`${baseUrl}/api/messages/threads`);
    console.log('Messages Status:', messages.status, await messages.json());
  } catch (e) {
    console.error('Messages Error:', e);
  }
}

testRoutes();
```

---

## Testing with Postman/Insomnia

### Postman Collection Example

1. **Create a new Collection**: "Fitness CRM API"

2. **Add Environment Variables**:
   - `base_url`: `http://localhost:5000` (or your production URL)

3. **Example Requests**:

**Get SMS Templates**
- Method: `GET`
- URL: `{{base_url}}/api/sms/templates`
- Headers: None needed

**Send SMS**
- Method: `POST`
- URL: `{{base_url}}/api/sms/send`
- Headers: `Content-Type: application/json`
- Body (JSON):
```json
{
  "to_number": "+1234567890",
  "message": "Test message",
  "client_id": 1
}
```

**Create Campaign**
- Method: `POST`
- URL: `{{base_url}}/api/campaigns`
- Headers: `Content-Type: application/json`
- Body (JSON):
```json
{
  "name": "Test Campaign",
  "subject": "Test Subject",
  "html_body": "<p>Test body</p>",
  "segment_type": "all",
  "send_immediately": false
}
```

---

## Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **404 Not Found**: Route not found (check if blueprint is registered)
- **500 Internal Server Error**: Server error (check backend logs)

---

## Troubleshooting

### 404 Not Found

1. **Check if route is registered**:
   ```bash
   curl http://localhost:5000/
   ```
   Look for `communication_features` in response

2. **Check backend logs** for:
   - `"SMS routes registered"` or `"SMS routes not available"`
   - Import errors

3. **Verify base URL** is correct

### CORS Errors

If calling from browser, ensure:
- Backend CORS is configured (already done in `app.py`)
- Using correct origin

### Connection Refused

- Backend server not running
- Wrong port (default: 5000)
- Firewall blocking connection

---

## Quick Test Script

Save as `test_routes.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:5000"

echo "Testing Communication Routes..."
echo ""

echo "1. Testing SMS Templates..."
curl -s "$BASE_URL/api/sms/templates" | jq '.' || echo "Failed"
echo ""

echo "2. Testing Campaigns..."
curl -s "$BASE_URL/api/campaigns" | jq '.' || echo "Failed"
echo ""

echo "3. Testing Automation Rules..."
curl -s "$BASE_URL/api/automation/rules" | jq '.' || echo "Failed"
echo ""

echo "4. Testing Message Threads..."
curl -s "$BASE_URL/api/messages/threads" | jq '.' || echo "Failed"
echo ""

echo "5. Testing Root Endpoint (check communication_features)..."
curl -s "$BASE_URL/" | jq '.communication_features' || echo "Failed"
```

Run with: `bash test_routes.sh`

---

## Next Steps

1. Test routes using curl or browser console
2. Check response status codes
3. If 404, check backend logs for import errors
4. Verify `communication_features` in root endpoint
5. Fix any missing dependencies or import errors

