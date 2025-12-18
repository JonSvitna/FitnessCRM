# Trainer Login Troubleshooting Guide

## Issue: Unable to Login to Trainer Account

### Common Causes

1. **Trainer was created before password management was added**
   - Trainers created before the password system was implemented don't have User accounts
   - The login system only checks the `users` table, not the `trainers` table

2. **No User account exists for the trainer**
   - Each trainer needs a corresponding User account with the same email
   - The User account stores the password and role

### Solution

#### Option 1: Set Password via Admin Dashboard (Recommended)

1. Log in as admin
2. Go to "Trainers" section
3. Find the trainer who can't log in
4. Click the "Change Password" button (key icon) next to the trainer
5. Enter a new password (minimum 6 characters)
6. This will automatically create a User account if one doesn't exist
7. The trainer can now log in with their email and the password you set

#### Option 2: Create User Account via Script

Run the utility script to create User accounts for all trainers without them:

```bash
cd backend
python utils/create_trainer_user.py
```

This will create User accounts with default passwords.

**NOTE**: When running `python init_db.py seed`, User accounts are automatically created for all seeded trainers and clients with development default passwords. These passwords should be changed immediately in production environments using the password change endpoints.

#### Option 3: Check if User Account Exists

Use the diagnostic endpoint to check:

```bash
curl http://localhost:5000/api/trainers/<trainer_id>/check-user \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

This will show:
- Whether the trainer has a User account
- The user's role
- Whether the account is active

### Verification Steps

1. **Check if trainer exists:**
   ```bash
   curl http://localhost:5000/api/trainers
   ```

2. **Check if User account exists:**
   ```bash
   curl http://localhost:5000/api/trainers/<trainer_id>/check-user
   ```

3. **Try logging in:**
   - Go to `/login.html`
   - Enter trainer's email
   - Enter the password you set
   - Should redirect to `/trainer.html`

### For New Trainers

When creating a new trainer:
- **Always include a password** in the "Add Trainer" form
- The system will automatically create both:
  - Trainer record in `trainers` table
  - User account in `users` table with role `'trainer'`

### Debugging Login Issues

If login still fails after setting password:

1. **Check browser console** for errors
2. **Check backend logs** for authentication errors
3. **Verify email matches exactly** (case-sensitive)
4. **Check if User account is active:**
   ```sql
   SELECT * FROM users WHERE email = 'trainer@example.com';
   ```
5. **Verify password hash was created:**
   ```sql
   SELECT email, role, active FROM users WHERE email = 'trainer@example.com';
   ```

### Common Error Messages

- **"Invalid credentials"**: Email/password mismatch or User account doesn't exist
- **"Account is disabled"**: User account exists but `active = false`
- **"User account not found"**: No User account exists for this email

### Quick Fix Script

If you have many trainers without User accounts, you can run:

```python
# backend/utils/create_trainer_user.py
python utils/create_trainer_user.py
```

This will create User accounts for all trainers/clients missing them.

