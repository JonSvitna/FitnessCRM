#!/bin/bash

# Railway Backend Boot Diagnosis Script
# Run this to check if your configuration is correct

echo "========================================="
echo "Railway Backend Configuration Check"
echo "========================================="
echo ""

# Check 1: File Structure
echo "✓ Checking file structure..."
if [ -f "railway.toml" ]; then
    echo "  ✅ railway.toml found in root"
else
    echo "  ❌ railway.toml missing!"
fi

if [ -f "backend/Procfile" ]; then
    echo "  ✅ backend/Procfile found"
else
    echo "  ❌ backend/Procfile missing!"
fi

if [ -f "backend/requirements.txt" ]; then
    echo "  ✅ backend/requirements.txt found"
else
    echo "  ❌ backend/requirements.txt missing!"
fi

if [ -f "backend/app.py" ]; then
    echo "  ✅ backend/app.py found"
else
    echo "  ❌ backend/app.py missing!"
fi

echo ""

# Check 2: Python Dependencies
echo "✓ Checking Python version..."
if command -v python3 &> /dev/null; then
    python3 --version
else
    echo "  ❌ Python3 not installed"
fi

echo ""

# Check 3: Required packages in requirements.txt
echo "✓ Checking requirements.txt content..."
if [ -f "backend/requirements.txt" ]; then
    echo "  Required packages:"
    grep -E "Flask|gunicorn|psycopg2" backend/requirements.txt || echo "  ⚠️  Some packages might be missing"
else
    echo "  ❌ requirements.txt not found"
fi

echo ""

# Check 4: Configuration files content
echo "✓ Checking configuration..."

echo "  railway.toml start command:"
if [ -f "railway.toml" ]; then
    grep "startCommand" railway.toml | head -1
else
    echo "    ❌ File not found"
fi

echo ""
echo "  Procfile command:"
if [ -f "backend/Procfile" ]; then
    cat backend/Procfile
else
    echo "    ❌ File not found"
fi

echo ""

# Check 5: Test local import
echo "✓ Testing if app can be imported..."
cd backend 2>/dev/null || { echo "  ❌ backend directory not found"; exit 1; }

if python3 -c "import app" 2>/dev/null; then
    echo "  ✅ app.py can be imported"
else
    echo "  ❌ Cannot import app - missing dependencies or syntax error"
    echo "     Run: pip install -r requirements.txt"
fi

cd ..

echo ""
echo "========================================="
echo "Configuration Summary"
echo "========================================="
echo ""
echo "For Railway Deployment:"
echo ""
echo "1. Root Directory Setting:"
echo "   Option A: Leave EMPTY → uses railway.toml (recommended)"
echo "   Option B: Set to 'backend' → uses backend/Procfile"
echo ""
echo "2. Required Environment Variables in Railway:"
echo "   - DATABASE_URL (auto-set when you add PostgreSQL)"
echo "   - FLASK_ENV=production"
echo "   - SECRET_KEY=<generate-random-key>"
echo "   - CORS_ORIGINS=https://your-frontend.vercel.app"
echo ""
echo "3. Test Commands:"
echo "   Local test: cd backend && gunicorn app:app --bind 0.0.0.0:8000"
echo "   API test:   curl https://your-app.railway.app/api/health"
echo ""
echo "========================================="
