@echo off
REM EquipSense Authentication System - Quick Start Script (Windows)
REM This script sets up and runs all services

echo ==================================
echo 🚀 EquipSense Auth System Startup
echo ==================================
echo.

REM Step 1: Setup Backend
echo 📦 Step 1: Setting up Django Backend...
cd backend
pip install -r requirements-auth.txt
python manage.py migrate
if %ERRORLEVEL% EQU 0 (
    echo ✅ Django Migrations completed
) else (
    echo ⚠️  Django setup encountered errors
)

REM Step 2: Check OTP Service
echo.
echo 📧 Step 2: Setting up OTP Service...
cd ..\otp_service

if not exist ".env" (
    echo ⚠️  WARNING: .env file not found!
    echo    Creating from .env.example...
    copy .env.example .env
    echo    Please edit otp_service\.env with your Gmail credentials
    echo    Instructions: https://myaccount.google.com/apppasswords
)

call npm install
if %ERRORLEVEL% EQU 0 (
    echo ✅ OTP Service Dependencies installed
) else (
    echo ⚠️  OTP Service setup encountered errors
)

REM Step  3: Setup Frontend
echo.
echo ⚛️  Step 3: Setting up React Frontend...
cd ..\frontend

if not exist ".env" (
    echo Creating frontend .env file...
    (
        echo REACT_APP_API_URL=http://localhost:8000/api
        echo REACT_APP_GOOGLE_CLIENT_ID=640198960520-lsfcnevaavlmqopo28og82smrvicv5hr.apps.googleusercontent.com
    ) > .env
)

call npm install axios react-toastify @react-oauth/google react-icons framer-motion
if %ERRORLEVEL% EQU 0 (
    echo ✅ Frontend Dependencies installed
) else (
    echo ⚠️  Frontend setup encountered errors
)

REM Step 4: Instructions to run
echo.
echo ==================================
echo ✅ Setup Complete!
echo ==================================
echo.
echo To start all services, open 3 terminals:
echo.
echo Terminal 1 (Django Backend):
echo   cd backend
echo   python manage.py runserver
echo.
echo Terminal 2 (OTP Service):
echo   cd otp_service
echo   npm run dev
echo.
echo Terminal 3 (React Frontend):
echo   cd frontend
echo   npm start
echo.
echo 📖 Full documentation: AUTHENTICATION_SETUP_GUIDE.md
echo ==================================
echo.

pause
