# FitnessCRM 🏋️

A modern, full-stack Customer Relationship Management (CRM) system for fitness trainers and gyms. Inspired by industry leaders like TrueCoach and Trainerize, featuring a professional orange-red-white color scheme, comprehensive marketing pages, and a powerful management dashboard. Frontend deployed on Vercel, Flask API backend on Railway with PostgreSQL database.

> 🆕 **NEW: EspoCRM-Inspired Architecture** - FitnessCRM now features a modular, entity-based architecture inspired by EspoCRM for better organization and maintainability!
> 
> 📖 **[Read the Comprehensive Manual](MANUAL.md)** - Complete documentation covering all aspects of FitnessCRM including installation, architecture, API reference, deployment, testing, troubleshooting, and more.
>
> 🏗️ **[EspoCRM Architecture Guide](ESPOCRM_ARCHITECTURE.md)** - Learn about the new modular architecture
>
> 🔄 **[Migration Guide](MIGRATION_TO_ESPOCRM.md)** - Migrate to the new architecture

## 🎯 Features

### Marketing & Public Pages
- **Professional Landing Page**: Modern hero section with compelling CTAs
- **About Page**: Company story and values
- **Pricing Plans**: Three-tier pricing (Starter, Professional, Enterprise)
- **FAQ Section**: Common questions and answers
- **Contact Form**: Easy communication with potential customers
- **SEO Optimized**: Meta tags, keywords, and semantic HTML for search engines
- **Mobile Responsive**: Beautiful experience on all devices

### Role-Based Portals

#### Trainer Portal 🏋️
- **Client Management**: View assigned clients, assign new clients, track client progress
- **Workout Creation**: Create workout plans with difficulty levels and duration
- **Session Scheduling**: Schedule training sessions with clients
- **Calendar Management**: View and manage appointments
- **Messaging**: Send messages and emails to clients
- **Challenges**: Create client challenges with goals and metrics
- **Dashboard**: Real-time stats for clients, sessions, and activity

#### Client Portal 💪
- **Profile Management**: Update personal and fitness information
- **Workout Access**: View assigned workouts and workout history
- **Progress Tracking**: Log weight, body fat, measurements, and notes
- **Meal Planning**: View meal plans and log daily meals
- **Session Calendar**: View schedule and request training sessions
- **Trainer Communication**: Message trainer directly
- **Dashboard**: Personal stats, trainer info, and upcoming sessions

### CRM Dashboard & Management (Admin)
- **Trainer Management**: Add, view, update, and delete trainer profiles with specializations, certifications, and rates
- **Client Management**: Comprehensive client profiles with goals, medical conditions, emergency contacts, and membership tracking
- **Session Tracking**: Schedule and manage training sessions with status tracking
- **Progress Records**: Track client measurements, weight, body fat percentage, and progress photos
- **Payment Processing**: Financial tracking with payment history and status
- **Workout Plans**: Create and manage workout templates with exercise libraries
- **Assignment System**: Link clients to trainers with detailed notes
- **Real-time Dashboard**: Live statistics and activity feed
- **Settings Management**: Configure SendGrid email and Twilio SMS
- **Activity Logging**: Comprehensive audit trail of all actions
- **Modern UI**: Professional orange-to-red gradients with white accents
- **RESTful API**: Full CRUD operations for all resources
- **PostgreSQL Database**: Robust relational database with comprehensive schema

## 🏗️ Architecture

### Frontend
- **Framework**: Vite (Multi-page application)
- **Styling**: TailwindCSS with professional orange-red gradient theme
- **Typography**: Inter + Poppins (Google Fonts)
- **Language**: HTML5, CSS3, JavaScript (ES6+)
- **API Client**: Axios
- **Pages**: 
  - Home/Marketing (`/home.html`)
  - Admin Dashboard (`/index.html`)
  - Trainer Portal (`/trainer.html`) - NEW! 🎉
  - Client Portal (`/client.html`) - NEW! 🎉
- **Deployment**: Vercel

### Backend
- **Framework**: Flask
- **Architecture**: EspoCRM-inspired modular system with EntityManager
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **API**: RESTful with CORS support
- **Modules**: Clients, Trainers, Sessions (organized by feature)
- **Entity System**: Metadata-driven with relationship management
- **Deployment**: Railway

## 📁 Project Structure

```
FitnessCRM/
├── frontend/                 # Frontend application
│   ├── src/
│   │   ├── components/      # (Future component modules)
│   │   ├── assets/          # Static assets
│   │   ├── styles/          # CSS and TailwindCSS
│   │   │   └── main.css     # Main stylesheet with custom utilities
│   │   ├── api.js           # API client and endpoints
│   │   └── main.js          # Application logic
│   ├── index.html           # Main HTML file
│   ├── package.json         # Dependencies
│   ├── vite.config.js       # Vite configuration
│   ├── tailwind.config.js   # TailwindCSS configuration
│   ├── postcss.config.js    # PostCSS configuration
│   ├── vercel.json          # Vercel deployment config
│   └── .env.example         # Environment variables template
│
└── backend/                 # Backend API
    ├── api/
    │   └── routes.py        # API endpoints
    ├── models/
    │   └── database.py      # Database models
    ├── config/
    │   └── settings.py      # Application configuration
    ├── app.py               # Application factory
    ├── requirements.txt     # Python dependencies
    ├── Procfile             # Railway deployment config
    ├── runtime.txt          # Python version
    └── .env.example         # Environment variables template
```

## 🚀 Quick Start

### Option 1: Docker Setup (Recommended)

The fastest way to get started is with Docker:

```bash
# Start all services (database, backend, frontend)
docker-compose up

# Initialize database with sample data (in another terminal)
docker-compose exec backend python init_db.py seed
```

Access the application at `http://localhost:3000`

### Option 2: Automated Setup Script

```bash
# Run the setup script
./setup.sh

# Follow the instructions to complete setup
```

### Option 3: Manual Setup

#### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 15+

#### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your API URL
npm run dev
```

The frontend will be available at `http://localhost:3000`

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
python app.py
```

The API will be available at `http://localhost:5000`

#### Database Setup

```bash
# Create database
createdb fitnesscrm

# Initialize with sample data
cd backend
source venv/bin/activate
python init_db.py seed
```

## 🗄️ Database Schema

### Trainers Table
- id (Primary Key)
- name, email (Unique), phone
- specialization, certification, experience (years)
- bio (Text), hourly_rate, active (Boolean)
- created_at, updated_at
- **Relationships**: assignments, sessions, workout_plans

### Clients Table
- id (Primary Key)
- name, email (Unique), phone, age
- goals (Text), medical_conditions (Text)
- emergency_contact, emergency_phone
- status (active/inactive/pending)
- membership_type (monthly/quarterly/annual)
- start_date, created_at, updated_at
- **Relationships**: assignments, sessions, progress_records, payments

### Assignments Table
- id (Primary Key)
- trainer_id (FK → trainers), client_id (FK → clients)
- notes (Text), status (active/completed/cancelled)
- created_at, updated_at

### Sessions Table
- id (Primary Key)
- trainer_id (FK → trainers), client_id (FK → clients)
- session_date, duration (minutes)
- session_type (personal/group/online)
- notes (Text), status (scheduled/completed/cancelled/no-show)
- created_at, updated_at

### Progress Records Table
- id (Primary Key)
- client_id (FK → clients)
- record_date, weight, body_fat_percentage
- measurements (JSON), photos (JSON)
- notes (Text), created_at

### Payments Table
- id (Primary Key)
- client_id (FK → clients)
- amount, payment_date
- payment_method (credit_card/cash/check)
- payment_type (membership/session/product)
- status (pending/completed/refunded/failed)
- transaction_id, notes (Text)
- created_at

### Workout Plans Table
- id (Primary Key)
- trainer_id (FK → trainers)
- name, description (Text)
- difficulty_level (beginner/intermediate/advanced)
- duration_weeks, exercises (JSON)
- public (Boolean)
- created_at, updated_at

## 🔌 API Endpoints

### Trainers
- `GET /api/trainers` - Get all trainers
- `GET /api/trainers/:id` - Get specific trainer
- `POST /api/trainers` - Create new trainer
- `PUT /api/trainers/:id` - Update trainer
- `DELETE /api/trainers/:id` - Delete trainer

### Clients
- `GET /api/clients` - Get all clients
- `GET /api/clients/:id` - Get specific client
- `POST /api/clients` - Create new client
- `PUT /api/clients/:id` - Update client
- `DELETE /api/clients/:id` - Delete client

### CRM Management
- `GET /api/crm/dashboard` - Get dashboard statistics
- `GET /api/crm/stats` - Get detailed statistics
- `POST /api/crm/assign` - Assign client to trainer
- `GET /api/crm/assignments` - Get all assignments
- `DELETE /api/crm/assignments/:id` - Delete assignment

### Health
- `GET /api/health` - Health check endpoint

## 🎨 Design System

### Color Palette
- **Primary Orange**: `#ea580c` (orange-600)
- **Dark Background**: `#1a1a1a`
- **Dark Secondary**: `#2d2d2d`
- **Dark Tertiary**: `#3d3d3d`

### Components
- Buttons: Primary (orange) and Secondary (gray)
- Input Fields: Dark theme with orange focus rings
- Cards: Elevated surfaces with borders
- Navigation: Horizontal tabs with active states

## 🚢 Deployment

### Frontend Deployment (Vercel)

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Set environment variable:
   - `VITE_API_URL`: Your Railway backend URL
4. Deploy

### Backend Deployment (Railway)

1. Create a new project on Railway
2. Connect your GitHub repository
3. **Configuration is automatic** via `railway.toml` in repository root
   - Alternatively, manually set "Root Directory" to `backend` in Railway UI
   - **Note**: "Root Directory" is a text input field where you type `backend`, not a dropdown
4. Add PostgreSQL database service
5. Set environment variables:
   - `DATABASE_URL`: (Auto-configured by Railway)
   - `SECRET_KEY`: Your secret key
   - `FLASK_ENV`: production
6. Deploy

**Complete Guide**: 📗 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Full deployment instructions for Vercel, Railway, and Docker

### Database Setup (Railway PostgreSQL)

Railway automatically provisions a PostgreSQL database. The connection URL is automatically set in the `DATABASE_URL` environment variable.

## 🗺️ Release Roadmap

### Phase 1-7: Core Features ✅ COMPLETED
- ✅ Foundation (v1.0) - Core CRM functionality
- ✅ Enhanced Features (v1.1) - Search, filters, pagination
- ✅ Advanced CRM (v1.2) - Scheduling, progress tracking
- ✅ Analytics & Reporting (v1.3) - Revenue, metrics, reports
- ✅ Communication (v1.4) - Messaging, campaigns, automation
- ✅ Mobile & Integrations (v2.0) - PWA, API, third-party integrations
- ✅ Advanced Features (v2.1) - AI, analytics, security

### Phase 8: System-Wide Debugging & Testing (v2.2) ✅ COMPLETED
**Timeline**: Weeks 25-32
- ✅ Testing infrastructure (pytest, coverage)
- ✅ Debugging tools and procedures
- ✅ System health checks
- ✅ Documentation and knowledge base
- ⏳ Integration testing (in progress)
- ⏳ Performance testing (in progress)
- ⏳ Security audit (in progress)

### Phase 9: Production Deployment & Optimization (v2.3) 🚀 IN PROGRESS
**Timeline**: Weeks 33-40  
**Current Status**: Planning & Setup

**Goals**:
- 🚀 Production-ready deployment configuration
- ⚡ Performance optimization and scalability
- 📊 Comprehensive monitoring and observability
- 🔒 Production security hardening
- 📈 Scalability and load balancing
- 🔄 Backup and disaster recovery
- 📝 Complete operations documentation

**Key Milestones**:
1. **M9.1**: Production Configuration (Weeks 33-34)
   - Redis cache, Nginx, SSL, auto-scaling
2. **M9.2**: Performance Optimization (Weeks 35-36)
   - Database optimization, caching, frontend optimization
3. **M9.3**: Monitoring & Observability (Weeks 36-37)
   - APM, logging, dashboards, alerts
4. **M9.4**: Security Hardening (Weeks 37-38)
   - Security headers, secrets management, WAF
5. **M9.5**: Backup & Disaster Recovery (Weeks 38-39)
   - Automated backups, DR plan, incident response
6. **M9.6**: Scalability & Load Testing (Weeks 39-40)
   - Load testing, benchmarking, capacity planning
7. **M9.7**: Operations & Documentation (Week 40)
   - Operations manual, user guides, knowledge base

**Documentation**:
- 📗 [PHASE_HISTORY.md](PHASE_HISTORY.md) - Complete phase history with Phase 9 details
- 🗺️ [ROADMAP.md](ROADMAP.md) - Updated roadmap with all phases
- 🚀 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment guide

### Future Phases (v3.0+)
- Advanced AI features
- Mobile native apps
- Multi-language support
- Enterprise features

## 📝 Notes

- **No Authentication**: As per requirements, user authentication is NOT implemented in this version
- **Security**: Add authentication before deploying to production
- **Scalability**: The current architecture supports horizontal scaling
- **Built Similar to**: TrueCoach CRM platform
- **NEW Architecture**: EspoCRM-inspired modular system for better organization

## 🏗️ New EspoCRM-Inspired Architecture

FitnessCRM now features a robust, modular architecture inspired by EspoCRM:

### Key Features
- **Entity System**: All models inherit from `BaseEntity` with common fields and lifecycle hooks
- **EntityManager**: Centralized CRUD operations for all entities
- **Module System**: Features organized into independent modules (Clients, Trainers, Sessions)
- **Relationship Management**: Metadata-driven relationships with automatic resolution
- **Generic API**: Consistent REST API endpoints for all entities
- **Backward Compatible**: All existing API routes continue to work

### Quick Example

```python
from core.entity_manager import entity_manager

# Create a client
client = entity_manager.create('clients', {
    'name': 'John Doe',
    'email': 'john@example.com'
})

# Get related entities
assignments = entity_manager.get_related('trainers', 1, 'assignments')
```

### Documentation
- 📘 **[ESPOCRM_ARCHITECTURE.md](ESPOCRM_ARCHITECTURE.md)** - Complete architecture guide
- 🔄 **[MIGRATION_TO_ESPOCRM.md](MIGRATION_TO_ESPOCRM.md)** - Migration guide for developers

## 📚 Documentation

**📖 [MANUAL.md](MANUAL.md)** - Complete comprehensive guide to FitnessCRM (1,600+ lines)

### Quick Start & Deployment
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete deployment guide (Vercel, Railway, Docker)

### Development Resources
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete REST API reference
- **[ESPOCRM_ARCHITECTURE.md](ESPOCRM_ARCHITECTURE.md)** - EspoCRM-inspired architecture guide 🆕
- **[MIGRATION_TO_ESPOCRM.md](MIGRATION_TO_ESPOCRM.md)** - Migration guide 🆕
- **[FEATURES.md](FEATURES.md)** - Feature overview and capabilities
- **[ROADMAP.md](ROADMAP.md)** - Development roadmap and future plans
- **[PHASE_HISTORY.md](PHASE_HISTORY.md)** - Complete development history (Phases 1-9)

### Operations & Support
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing and QA procedures
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[AI_GUIDE.md](AI_GUIDE.md)** - AI Orchestrator complete guide

### Project Management
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## 📄 License

This project is proprietary software for fitness training management.

## 🆘 Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ for fitness professionals
