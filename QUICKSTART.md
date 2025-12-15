# Quick Start Guide 🚀

Get Fitness CRM up and running in 5 minutes!

## Prerequisites

Ensure you have these installed:
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 15+

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/JonSvitna/FitnessCRM.git
cd FitnessCRM
```

### 2. Set Up the Database

```bash
# Create PostgreSQL database
createdb fitnesscrm

# Or using psql
psql -U postgres
CREATE DATABASE fitnesscrm;
\q
```

### 3. Set Up Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your database credentials
# DATABASE_URL=postgresql://username:password@localhost:5432/fitnesscrm

# Initialize database with sample data
python init_db.py seed

# Start the backend server
python app.py
```

Backend will be running at `http://localhost:5000`

### 4. Set Up Frontend (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Edit .env with backend URL
# VITE_API_URL=http://localhost:5000

# Start the development server
npm run dev
```

Frontend will be running at `http://localhost:3000`

### 5. Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

You should see the Fitness CRM dashboard!

## Default Sample Data

After running `python init_db.py seed`, you'll have:

**3 Trainers**:
- Mike Johnson (Strength Training)
- Sarah Williams (Cardio, HIIT)
- David Chen (Yoga, Flexibility)

**5 Clients**:
- Emma Thompson
- James Martinez
- Lisa Anderson
- Robert Taylor
- Jennifer Lee

**5 Assignments**:
- Various trainer-client pairings

## Quick Commands

### Backend

```bash
# Start backend
cd backend
source venv/bin/activate
python app.py

# Reset database
python init_db.py reset

# Clear database
python init_db.py clear

# Initialize without sample data
python init_db.py
```

### Frontend

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Testing the Application

### 1. View Dashboard
- Navigate to the Dashboard tab
- See statistics for trainers, clients, and assignments

### 2. Add a Trainer
- Click on "Trainers" tab
- Fill out the form on the left
- Click "Add Trainer"
- See the trainer appear in the list

### 3. Add a Client
- Click on "Clients" tab
- Fill out the form on the left
- Click "Add Client"
- See the client appear in the list

### 4. Create Assignment
- Click on "Management" tab
- Select a trainer from the dropdown
- Select a client from the dropdown
- Add optional notes
- Click "Create Assignment"
- See the assignment in the list

## Common Issues

### Backend won't start

**Issue**: Database connection error
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**: 
- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in `.env`
- Ensure database exists: `psql -l | grep fitnesscrm`

### Frontend can't connect to backend

**Issue**: API calls failing
```
Network Error
```

**Solution**:
- Verify backend is running on port 5000
- Check VITE_API_URL in `.env`
- Check browser console for CORS errors

### Port already in use

**Issue**: 
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solution**:
- Kill the process using the port: `lsof -ti:3000 | xargs kill`
- Or use a different port: `npm run dev -- --port 3001`

## Next Steps

Once you have the app running locally:

1. **Explore Features**: Try all CRUD operations
2. **Read Documentation**: Check out API_DOCUMENTATION.md
3. **Deploy**: Follow DEPLOYMENT.md to deploy to production
4. **Contribute**: See CONTRIBUTING.md to contribute

## Production Deployment

For production deployment:

### Frontend → Vercel
```bash
# 1. Push to GitHub
git push origin main

# 2. Import project on Vercel
# - Go to vercel.com
# - Import GitHub repository
# - Set root directory to "frontend"
# - Add VITE_API_URL environment variable

# 3. Deploy
```

### Backend → Railway
```bash
# 1. Push to GitHub
git push origin main

# 2. Create project on Railway
# - Go to railway.app
# - Create new project from GitHub
# - Add PostgreSQL database
# - Set environment variables:
#   - FLASK_ENV=production
#   - SECRET_KEY=your-secret-key

# 3. Deploy
```

See DEPLOYMENT.md for detailed deployment instructions.

## Support

- **Issues**: Open an issue on GitHub
- **Questions**: Check README.md and documentation
- **API Reference**: See API_DOCUMENTATION.md

## Resources

- **README.md**: Comprehensive overview
- **DEPLOYMENT.md**: Deployment guide
- **API_DOCUMENTATION.md**: Complete API reference
- **ROADMAP.md**: Future development plans
- **CONTRIBUTING.md**: Contribution guidelines

---

Happy coding! 🎉
