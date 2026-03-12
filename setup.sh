#!/bin/bash
# NewsHub - Quick Start Script
# Run this script to get NewsHub up and running locally in seconds

set -e

echo "🚀 NewsHub - Quick Start Setup"
echo "================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION detected"

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Copy .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env from template..."
    cp .env.example .env
    echo "   → Edit .env to customize settings if needed"
fi

# Run migrations
echo "🗄️  Setting up database..."
python manage.py migrate --quiet

# Create superuser if database is new
if [ ! -f "db.sqlite3" ] || [ $(sqlite3 db.sqlite3 "SELECT COUNT(*) FROM auth_user;" 2>/dev/null || echo 0) -eq 0 ]; then
    echo "👤 Creating admin user (admin / admin123)..."
    python manage.py createsuperuser --noinput \
        --username admin \
        --email admin@newshub.local \
        2>/dev/null || true
    python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.filter(username='admin').first(); u and u.set_password('admin123') and u.save()"
fi

# Seed data
echo "🌱 Seeding example data..."
python manage.py seed_data --quiet 2>/dev/null || python manage.py seed_data

# Done!
echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Start the dev server:"
echo "      python manage.py runserver"
echo ""
echo "   2. Visit in your browser:"
echo "      http://localhost:8000"
echo ""
echo "   3. Admin credentials:"
echo "      Username: admin"
echo "      Password: admin123"
echo ""
echo "📚 More login credentials in README.md"
echo ""

