# Authentication Setup Guide

## Default Admin User

A default admin user is automatically created on first startup:

**Email**: `admin@fitnesscrm.com`  
**Password**: `admin123` (or value from `DEFAULT_ADMIN_PASSWORD` environment variable)  
**Role**: `admin`

⚠️ **IMPORTANT**: Change this password immediately after first login!

## Creating Additional Users

### Via API

```bash
# Register a new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "role": "user"
  }'
```

### Via Script

Run the create_default_user script:

```bash
cd backend
python utils/create_default_user.py
```

## Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@fitnesscrm.com",
    "password": "admin123"
  }'
```

Response:
```json
{
  "user": {
    "id": 1,
    "email": "admin@fitnesscrm.com",
    "role": "admin",
    "active": true
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Using the Token

Include the token in API requests:

```bash
curl http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Roles

- **admin**: Full access, can view audit logs
- **trainer**: Trainer-specific access
- **user**: Standard user access

## Security Notes

1. **Change default password** immediately
2. Set `DEFAULT_ADMIN_PASSWORD` environment variable for custom default password
3. Use strong passwords in production
4. JWT tokens expire after 24 hours
5. Store tokens securely (not in localStorage for sensitive apps)

## Environment Variables

```bash
# JWT Secret (required for auth)
JWT_SECRET=your-secret-key-here

# Optional: Custom default admin password
DEFAULT_ADMIN_PASSWORD=your-secure-password

# Optional: Skip default user creation
SKIP_DEFAULT_USER=true
```

