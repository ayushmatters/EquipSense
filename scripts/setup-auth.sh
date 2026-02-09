#!/bin/bash

# EquipSense Authentication System - Quick Start Script
# This script sets up and runs all services

echo "=================================="
echo "🚀 EquipSense Auth System Startup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if service is running
check_service() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1 started successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  $1 failed to start${NC}"
    fi
}

# Step 1: Setup Backend
echo "📦 Step 1: Setting up Django Backend..."
cd backend
pip install -r requirements-auth.txt
python manage.py migrate
check_service "Django Migrations"

# Step 2: Check OTP Service
echo ""
echo "📧 Step 2: Setting up OTP Service..."
cd ../otp_service

if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "   Creating from .env.example..."
    cp .env.example .env
    echo "   Please edit otp_service/.env with your Gmail credentials"
    echo "   Instructions: https://myaccount.google.com/apppasswords"
fi

npm install
check_service "OTP Service Dependencies"

# Step 3: Setup Frontend
echo ""
echo "⚛️  Step 3: Setting up React Frontend..."
cd ../frontend

if [ ! -f ".env" ]; then
    echo "Creating frontend .env file..."
    cat > .env << EOL
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_GOOGLE_CLIENT_ID=640198960520-lsfcnevaavlmqopo28og82smrvicv5hr.apps.googleusercontent.com
EOL
fi

npm install axios react-toastify @react-oauth/google react-icons framer-motion
check_service "Frontend Dependencies"

# Step 4: Instructions to run
echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "To start all services, open 3 terminals:"
echo ""
echo "Terminal 1 (Django Backend):"
echo "  cd backend"
echo "  python manage.py runserver"
echo ""
echo "Terminal 2 (OTP Service):"
echo "  cd otp_service"
echo "  npm run dev"
echo ""
echo "Terminal 3 (React Frontend):"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "📖 Full documentation: AUTHENTICATION_SETUP_GUIDE.md"
echo "=================================="
