# Database Accounts - Seeded Data

This document contains information about the accounts that have been seeded into the database.

## Summary

The database has been populated with real account data including:
- **1 Admin account**
- **4 Trainer accounts** with User login credentials
- **8 Client accounts** with User login credentials
- **6 Trainer-Client assignments**

## Admin Account

| Email | Password | Role |
|-------|----------|------|
| admin@fitnesscrm.com | admin123 | admin |

## Trainer Accounts

All trainers have the password: `trainer123`

| Name | Email | Specialization | Certification | Experience |
|------|-------|----------------|---------------|------------|
| Mike Johnson | mike.johnson@fitnesscrm.com | Strength Training, Powerlifting | NASM-CPT, CSCS | 8 years |
| Sarah Williams | sarah.williams@fitnesscrm.com | Cardio, HIIT, Weight Loss | ACE-CPT | 5 years |
| David Chen | david.chen@fitnesscrm.com | Yoga, Flexibility, Rehabilitation | RYT-500, NASM-CES | 10 years |
| Jessica Brown | jessica.brown@fitnesscrm.com | CrossFit, Functional Training | CrossFit Level 2 | 6 years |

## Client Accounts

All clients have the password: `client123`

| Name | Email | Age | Goals |
|------|-------|-----|-------|
| Emma Thompson | emma.thompson@example.com | 28 | Weight loss, improved cardiovascular health |
| James Martinez | james.martinez@example.com | 35 | Muscle gain, strength training |
| Lisa Anderson | lisa.anderson@example.com | 42 | Flexibility, stress reduction, back pain management |
| Robert Taylor | robert.taylor@example.com | 31 | Marathon training, endurance |
| Jennifer Lee | jennifer.lee@example.com | 26 | Toning, general fitness |
| Michael Scott | michael.scott@example.com | 45 | Weight management, stress relief |
| Amanda Clark | amanda.clark@example.com | 33 | Athletic performance, competition prep |
| Daniel Kim | daniel.kim@example.com | 29 | Build muscle, improve posture |

## Trainer-Client Assignments

| Trainer | Client | Notes |
|---------|--------|-------|
| Mike Johnson | James Martinez | Focus on compound lifts and progressive overload |
| Sarah Williams | Emma Thompson | Starting with cardio base building, 3x per week |
| Sarah Williams | Robert Taylor | Marathon training plan - 16 week program |
| David Chen | Lisa Anderson | Therapeutic yoga for back pain, 2x per week |
| Sarah Williams | Jennifer Lee | Circuit training and HIIT workouts |
| Jessica Brown | Amanda Clark | CrossFit competition prep, 5x per week |

## How to Seed the Database

To populate a fresh database with this data, run:

```bash
cd backend
source venv/bin/activate
export DATABASE_URL='sqlite:///fitnesscrm.db'  # or your database URL
python seed_accounts.py
```

To clear all data and reseed:

```bash
python seed_accounts.py clear
python seed_accounts.py
```

## ⚠️ Security Warning

**IMPORTANT:** These are default passwords for development/testing only!

- Change all passwords immediately in production environments
- Use the password change functionality in the Settings section of each portal
- Admin can set passwords for trainers/clients via the admin dashboard

## Testing the Accounts

You can log in to test each portal:

1. **Admin Portal** (http://localhost:3000/index.html):
   - Login: admin@fitnesscrm.com / admin123

2. **Trainer Portal** (http://localhost:3000/trainer.html):
   - Login: mike.johnson@fitnesscrm.com / trainer123
   - Or any other trainer email / trainer123

3. **Client Portal** (http://localhost:3000/client.html):
   - Login: emma.thompson@example.com / client123
   - Or any other client email / client123

Each portal now has:
- Logout button in the sidebar footer
- Settings section with password change form
- Account information display
