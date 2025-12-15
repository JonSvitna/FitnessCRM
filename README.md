# FitnessCRM 🏋️

A modern, full-stack Customer Relationship Management (CRM) system for fitness trainers and clients. Built with a clean dark orange color scheme, featuring a static frontend deployed on Vercel and a Flask API backend on Railway with PostgreSQL database.

## 🎯 Features

- **Trainer Management**: Add, view, update, and delete trainer profiles with specializations and certifications
- **Client Management**: Comprehensive client profiles with fitness goals and medical conditions tracking
- **CRM Dashboard**: Real-time statistics and activity tracking
- **Assignment System**: Link clients to trainers with notes and management capabilities
- **Modern UI**: Dark theme with orange accents, built with TailwindCSS
- **RESTful API**: Full CRUD operations for all resources
- **PostgreSQL Database**: Robust relational database for data persistence

## 🏗️ Architecture

### Frontend
- **Framework**: Vite
- **Styling**: TailwindCSS with custom dark orange theme
- **Language**: HTML5, CSS3, JavaScript (ES6+)
- **API Client**: Axios
- **Deployment**: Vercel

### Backend
- **Framework**: Flask
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **API**: RESTful with CORS support
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

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 15+

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your API URL
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend Setup

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

## 🗄️ Database Schema

### Trainers Table
- id (Primary Key)
- name
- email (Unique)
- phone
- specialization
- certification
- experience (years)
- created_at
- updated_at

### Clients Table
- id (Primary Key)
- name
- email (Unique)
- phone
- age
- goals (Text)
- medical_conditions (Text)
- created_at
- updated_at

### Assignments Table
- id (Primary Key)
- trainer_id (Foreign Key)
- client_id (Foreign Key)
- notes (Text)
- created_at
- updated_at

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
2. Add PostgreSQL database service
3. Connect your GitHub repository
4. Set environment variables:
   - `DATABASE_URL`: (Auto-configured by Railway)
   - `SECRET_KEY`: Your secret key
   - `FLASK_ENV`: production
5. Deploy

### Database Setup (Railway PostgreSQL)

Railway automatically provisions a PostgreSQL database. The connection URL is automatically set in the `DATABASE_URL` environment variable.

## 🗺️ Release Roadmap

### Phase 1: Foundation (Current) ✅
- [x] Frontend setup with Vite and TailwindCSS
- [x] Backend Flask API with PostgreSQL
- [x] Core CRUD operations for trainers and clients
- [x] Assignment system for CRM management
- [x] Deployment configurations

### Phase 2: Enhanced Features (v1.1)
**Target: 2-3 weeks**
- [ ] Search and filter functionality
- [ ] Pagination for large datasets
- [ ] Export data to CSV/PDF
- [ ] Email notifications for assignments
- [ ] Activity logging and audit trail

### Phase 3: Advanced CRM (v1.2)
**Target: 4-6 weeks**
- [ ] Session scheduling and calendar
- [ ] Progress tracking for clients
- [ ] File uploads (workout plans, documents)
- [ ] Client progress photos and measurements
- [ ] Workout template library

### Phase 4: Analytics & Reporting (v1.3)
**Target: 7-9 weeks**
- [ ] Revenue tracking and reporting
- [ ] Client retention analytics
- [ ] Trainer performance metrics
- [ ] Custom report generation
- [ ] Data visualization dashboards

### Phase 5: Communication (v1.4)
**Target: 10-12 weeks**
- [ ] In-app messaging between trainers and clients
- [ ] SMS notifications
- [ ] Email campaign system
- [ ] Automated reminders
- [ ] Client feedback system

### Phase 6: Mobile & API Enhancement (v2.0)
**Target: 13-16 weeks**
- [ ] Progressive Web App (PWA) support
- [ ] Mobile-responsive improvements
- [ ] Public API documentation
- [ ] Webhook system for integrations
- [ ] Third-party integrations (Stripe, Calendly, etc.)

## 📝 Notes

- **No Authentication**: As per requirements, user authentication is NOT implemented in this version
- **Security**: Add authentication before deploying to production
- **Scalability**: The current architecture supports horizontal scaling
- **Built Similar to**: TrueCoach CRM platform

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is proprietary software for fitness training management.

## 🆘 Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ for fitness professionals
