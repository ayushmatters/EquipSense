# Install PyQtWebEngine for Desktop-Frontend Integration
# Run this script to update desktop dependencies

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PyQtWebEngine Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if ($env:VIRTUAL_ENV) {
    Write-Host "✓ Virtual environment active: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "⚠ Virtual environment not active" -ForegroundColor Yellow
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    
    $venvPath = Join-Path $PSScriptRoot ".." ".venv" "Scripts" "Activate.ps1"
    if (Test-Path $venvPath) {
        & $venvPath
        Write-Host "✓ Virtual environment activated" -ForegroundColor Green
    } else {
        Write-Host "✗ Virtual environment not found at: $venvPath" -ForegroundColor Red
        Write-Host "Please create virtual environment first" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Installing/Upgrading packages..." -ForegroundColor Cyan

# Upgrade pip
Write-Host "  → Upgrading pip..." -ForegroundColor Gray
python -m pip install --upgrade pip

# Install PyQtWebEngine
Write-Host "  → Installing PyQtWebEngine..." -ForegroundColor Gray
pip install PyQtWebEngine==5.15.6

# Install all requirements
Write-Host "  → Installing all requirements..." -ForegroundColor Gray
pip install -r requirements.txt

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Start Backend:  cd ../backend && python manage.py runserver" -ForegroundColor White
Write-Host "  2. Start OTP:      cd ../otp_service && npm start" -ForegroundColor White
Write-Host "  3. Start Frontend: cd ../frontend && npm run dev" -ForegroundColor White
Write-Host "  4. Start Desktop:  python main.py" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
