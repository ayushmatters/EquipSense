# Quick Activation Script for Chemical Equipment Visualizer
# Save this as: activate_env.ps1

Write-Host "🚀 Activating Chemical Equipment Visualizer Environment..." -ForegroundColor Cyan

# Navigate to project root
$projectRoot = "d:\Ayush Asus C Drive\Study\RGIPT\STUDY\MnC\Internships\FOSSEE_IITB\EquipSense"
Set-Location $projectRoot

# Check if .venv exists
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    # Activate virtual environment
    .\.venv\Scripts\Activate.ps1
    
    Write-Host "✅ Virtual Environment Activated!" -ForegroundColor Green
    Write-Host "📍 Location: $projectRoot" -ForegroundColor Yellow
    Write-Host ""
    
    # Show Python version
    Write-Host "🐍 Python Version:" -ForegroundColor Cyan
    python --version
    Write-Host ""
    
    # Show installed packages count
    $packageCount = (pip list | Measure-Object -Line).Lines - 2
    Write-Host "📦 Installed Packages: $packageCount" -ForegroundColor Cyan
    Write-Host ""
    
    # Show quick commands
    Write-Host "⚡ Quick Commands:" -ForegroundColor Magenta
    Write-Host "   Backend:  cd backend && python manage.py runserver" -ForegroundColor White
    Write-Host "   Frontend: cd frontend && npm run dev" -ForegroundColor White
    Write-Host "   Desktop:  cd desktop && python main.py" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🎯 Ready for development!" -ForegroundColor Green
}
else {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Run: py -3.11 -m venv .venv" -ForegroundColor Yellow
}
