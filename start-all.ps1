# EquipSense - Start All Services
# This script starts Backend, Frontend, OTP Service, and Desktop App in separate terminals

$projectRoot = "d:\Ayush Asus C Drive\Study\RGIPT\STUDY\MnC\Internships\FOSSEE_IITB\EquipSense"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ⚙️  EquipSense Startup Manager" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if project directory exists
if (-not (Test-Path $projectRoot)) {
    Write-Host "❌ Error: Project directory not found!" -ForegroundColor Red
    Write-Host "   Path: $projectRoot" -ForegroundColor Yellow
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "$projectRoot\.venv\Scripts\python.exe")) {
    Write-Host "❌ Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Please run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting services..." -ForegroundColor Green
Write-Host ""

# Start Backend (Django)
Write-Host "1️⃣  Starting Backend (Django) on port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$projectRoot'; Write-Host '🐍 Backend Server' -ForegroundColor Green; Write-Host 'URL: http://localhost:8000' -ForegroundColor Cyan; Write-Host ''; & '.\.venv\Scripts\python.exe' 'backend\manage.py' runserver"
)
Start-Sleep -Seconds 2

# Start Frontend (React/Vite)
Write-Host "2️⃣  Starting Frontend (React/Vite) on port 3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$projectRoot\frontend'; Write-Host '⚛️  Frontend Server' -ForegroundColor Green; Write-Host 'URL: http://localhost:3000' -ForegroundColor Cyan; Write-Host ''; npm run dev"
)
Start-Sleep -Seconds 2

# Start OTP Service (Node.js)
Write-Host "3️⃣  Starting OTP Service (Node.js) on port 5000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$projectRoot\otp_service'; Write-Host '📧 OTP Email Service' -ForegroundColor Green; Write-Host 'URL: http://localhost:5000' -ForegroundColor Cyan; Write-Host ''; `$env:PORT=5000; node server.js"
)
Start-Sleep -Seconds 2

# Start Desktop App (PyQt5)
Write-Host "4️⃣  Starting Desktop App (PyQt5)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$projectRoot'; Write-Host '🖥️  Desktop Application' -ForegroundColor Green; Write-Host 'Starting PyQt5 window...' -ForegroundColor Cyan; Write-Host ''; & '.\.venv\Scripts\python.exe' 'desktop\main.py'"
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ✅ All Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access Points:" -ForegroundColor Cyan
Write-Host "   ├─ Frontend (Web):  " -NoNewline -ForegroundColor White
Write-Host "http://localhost:3000" -ForegroundColor Yellow
Write-Host "   ├─ Backend (API):   " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000" -ForegroundColor Yellow
Write-Host "   ├─ OTP Service:     " -NoNewline -ForegroundColor White
Write-Host "http://localhost:5000" -ForegroundColor Yellow
Write-Host "   └─ Desktop App:     " -NoNewline -ForegroundColor White
Write-Host "Native Window" -ForegroundColor Yellow
Write-Host ""
Write-Host "⏳ Waiting for services to initialize (10 seconds)..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# Verify services are running
Write-Host ""
Write-Host "🔍 Verifying services..." -ForegroundColor Cyan

# Check Backend
try {
    $backend = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/google/config/" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "   ✅ Backend:    " -NoNewline -ForegroundColor White
    Write-Host "Running (HTTP $($backend.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Backend:    " -NoNewline -ForegroundColor White
    Write-Host "Not responding (Starting up...)" -ForegroundColor Yellow
}

# Check Frontend
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000/" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "   ✅ Frontend:   " -NoNewline -ForegroundColor White
    Write-Host "Running (HTTP $($frontend.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Frontend:   " -NoNewline -ForegroundColor White
    Write-Host "Not responding (Starting up...)" -ForegroundColor Yellow
}

# Check OTP Service
$otpPort = netstat -ano | Select-String ":5000.*LISTENING"
if ($otpPort) {
    Write-Host "   ✅ OTP Service:" -NoNewline -ForegroundColor White
    Write-Host "Running" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  OTP Service:" -NoNewline -ForegroundColor White
    Write-Host "Not detected (Starting up...)" -ForegroundColor Yellow
}

# Check Desktop App
$desktopProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*EquipSense*" -and $_.MainWindowTitle -ne "" }
if ($desktopProcess) {
    Write-Host "   ✅ Desktop App:" -NoNewline -ForegroundColor White
    Write-Host "Running" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Desktop App:" -NoNewline -ForegroundColor White
    Write-Host "Not detected (Starting up...)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Quick Tips:" -ForegroundColor Cyan
Write-Host "   • Press Ctrl+C in any terminal to stop that service" -ForegroundColor White
Write-Host "   • Close terminal windows to stop all services" -ForegroundColor White
Write-Host "   • Check STARTUP_GUIDE.md for detailed instructions" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to open frontend in browser..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open frontend in default browser
Write-Host "🌐 Opening browser..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "✨ Enjoy using EquipSense!" -ForegroundColor Green
Write-Host ""
