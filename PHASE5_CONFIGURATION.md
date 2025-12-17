# Phase 5: Communication Tools - Configuration Guide

This guide will help you configure all Phase 5 communication features to connect properly with the backend.

## Overview

Phase 5 includes four main communication features:
1. **M5.1: In-App Messaging** - Real-time chat with WebSocket support
2. **M5.2: SMS Integration** - SMS sending via Twilio
3. **M5.3: Email Campaigns** - Email campaigns with templates
4. **M5.4: Automated Reminders** - Automated email/SMS reminders

## Prerequisites

### Backend Dependencies
Ensure these packages are installed:
```bash
pip install Flask-SocketIO python-socketio twilio Flask-Mail
```

### Environment Variables
Create a `.env` file in the backend directory with the following variables:

```env
# Email Configuration (for M5.3 and M5.4)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# SocketIO Configuration (for M5.1)
# No additional env vars needed, but ensure Flask-SocketIO is installed
```

## M5.1: In-App Messaging Configuration

### Backend Setup
1. **SocketIO is already initialized** in `backend/app.py`
2. **Message routes are registered** automatically if Flask-SocketIO is installed
3. **Frontend connects** via Socket.IO client in `frontend/src/messages.js`

### Configuration Steps
1. Ensure Flask-SocketIO is installed:
   ```bash
   pip install Flask-SocketIO==5.3.6 python-socketio==5.11.0
   ```

2. The frontend automatically connects to the backend SocketIO server
3. Test by opening `/messages.html` and sending a message

### Troubleshooting
- If messages don't send: Check browser console for SocketIO connection errors
- If real-time updates don't work: Verify SocketIO is initialized in `app.py`
- Check backend logs for SocketIO connection errors

## M5.2: SMS Integration Configuration

### Backend Setup
SMS functionality uses Twilio and requires configuration in the Settings database.

### Configuration Steps

#### 1. Get Twilio Credentials
1. Sign up for a Twilio account at https://www.twilio.com
2. Get your Account SID and Auth Token from the Twilio Console
3. Get a Twilio phone number (or use a trial number)

#### 2. Configure in Database
You can configure Twilio via the Settings API endpoint:

```bash
# Update Twilio settings
curl -X PUT http://localhost:5000/api/settings \
  -H "Content-Type: application/json" \
  -d '{
    "twilio_enabled": true,
    "twilio_account_sid": "your_account_sid",
    "twilio_auth_token": "your_auth_token",
    "twilio_phone_number": "+1234567890"
  }'
```

Or use the Settings page in the frontend at `/index.html#settings-section`

#### 3. Test SMS Configuration
Use the test endpoint:
```bash
curl -X POST http://localhost:5000/api/settings/test-twilio \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890",
    "message": "Test message"
  }'
```

### Troubleshooting
- **"Twilio is not configured"**: Ensure settings are saved in the database
- **"Twilio library not installed"**: Run `pip install twilio>=9.1.0`
- **Phone number format errors**: Use E.164 format (+1234567890)
- **Trial account limitations**: Twilio trial accounts can only send to verified numbers

## M5.3: Email Campaigns Configuration

### Backend Setup
Email campaigns use Flask-Mail and require SMTP configuration.

### Configuration Steps

#### 1. Gmail Setup (Recommended)
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
   - Use this password in `MAIL_PASSWORD`

#### 2. Other SMTP Providers
Update `.env` with your SMTP settings:
```env
MAIL_SERVER=smtp.your-provider.com
MAIL_PORT=587  # or 465 for SSL
MAIL_USE_TLS=true  # or false for SSL
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=your-email@domain.com
```

#### 3. Test Email Configuration
The email utility will log warnings if not configured. Check backend logs when sending campaigns.

### Troubleshooting
- **Emails not sending**: Check `MAIL_USERNAME` and `MAIL_PASSWORD` in `.env`
- **Gmail errors**: Use App Password, not regular password
- **SMTP errors**: Verify `MAIL_SERVER` and `MAIL_PORT` are correct
- **Check logs**: Backend logs will show email send errors

## M5.4: Automated Reminders Configuration

### Backend Setup
Automation rules use both email and SMS, so configure both M5.2 and M5.3 first.

### Configuration Steps
1. **Configure Email** (see M5.3 above)
2. **Configure SMS** (see M5.2 above)
3. **Create Automation Rules** via `/automation.html` frontend

### How It Works
- Automation rules are stored in the database
- Rules execute based on triggers (session_created, payment_due, etc.)
- Actions can be email, SMS, or both
- Execution logs are stored in `automation_logs` table

### Manual Execution
You can manually trigger rules via API:
```bash
curl -X POST http://localhost:5000/api/automation/rules/{rule_id}/execute
```

## Frontend-Backend Connection

### API Base URL
The frontend connects to the backend via the API base URL configured in `frontend/src/api.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
```

### SocketIO Connection
Messages use Socket.IO and connect automatically:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
socket = io(API_BASE_URL);
```

### CORS Configuration
The backend is configured to allow all origins. For production, update CORS in `backend/app.py`.

## Verification Checklist

- [ ] Flask-SocketIO installed and working
- [ ] Email environment variables set in `.env`
- [ ] Twilio credentials configured in Settings database
- [ ] Frontend can connect to backend API
- [ ] SocketIO connection established (check browser console)
- [ ] Test SMS sends successfully
- [ ] Test email sends successfully
- [ ] Automation rules can be created and executed

## Testing Each Feature

### Test M5.1 (Messaging)
1. Open `/messages.html`
2. Create a new thread
3. Send a message
4. Verify real-time delivery

### Test M5.2 (SMS)
1. Open `/sms.html`
2. Send a test SMS
3. Check SMS logs tab
4. Verify SMS received

### Test M5.3 (Email Campaigns)
1. Open `/campaigns.html`
2. Create a campaign
3. Send to test email
4. Verify email received

### Test M5.4 (Automation)
1. Open `/automation.html`
2. Create an automation rule
3. Manually execute it
4. Check execution logs

## Production Considerations

1. **Email**: Use a professional SMTP service (SendGrid, Mailgun, AWS SES)
2. **SMS**: Upgrade from Twilio trial to paid account
3. **SocketIO**: Configure proper CORS for production domain
4. **Security**: Store credentials securely (use environment variables, not code)
5. **Rate Limiting**: Implement rate limiting for SMS and email sending
6. **Monitoring**: Set up logging and monitoring for all communication features

## Support

If you encounter issues:
1. Check backend logs for errors
2. Check browser console for frontend errors
3. Verify all dependencies are installed
4. Verify environment variables are set correctly
5. Test API endpoints directly with curl/Postman

