#!/bin/bash

# Fitness CRM Setup Script
# This script automates the local development setup

set -e

echo "🏋️  Fitness CRM Setup Script"
echo "=============================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found:$(node --version)${NC}"

if ! command_exists npm; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm found: $(npm --version)${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.11+ from https://python.org/"
    exit 1
fi
echo -e "${GREEN}✓ Python found: $(python3 --version)${NC}"

if ! command_exists psql; then
    echo -e "${YELLOW}⚠️  PostgreSQL client not found${NC}"
    echo "PostgreSQL is recommended but not required for initial setup"
fi

echo ""
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating backend .env file..."
    cp .env.example .env
    echo -e "${GREEN}✓ Backend .env created${NC}"
    echo -e "${YELLOW}⚠️  Please edit backend/.env with your database credentials${NC}"
else
    echo -e "${GREEN}✓ Backend .env already exists${NC}"
fi

cd ..

echo ""
echo "🎨 Setting up frontend..."
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install --silent
echo -e "${GREEN}✓ Node.js dependencies installed${NC}"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating frontend .env file..."
    cp .env.example .env
    echo -e "${GREEN}✓ Frontend .env created${NC}"
else
    echo -e "${GREEN}✓ Frontend .env already exists${NC}"
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Configure your database in backend/.env"
echo "2. Create the PostgreSQL database: createdb fitnesscrm"
echo "3. Initialize the database with sample data:"
echo "   cd backend && source venv/bin/activate && python init_db.py seed"
echo "4. Start the backend: cd backend && python app.py"
echo "5. Start the frontend (new terminal): cd frontend && npm run dev"
echo ""
echo "📚 For detailed instructions, see QUICKSTART.md"
echo ""
echo -e "${GREEN}Happy coding! 🎉${NC}"
