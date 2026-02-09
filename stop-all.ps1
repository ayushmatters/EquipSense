# EquipSense - Stop All Services
# This script safely stops all running EquipSense services

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ⚙️  EquipSense Shutdown Manager" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find and stop processes on specific ports
$ports = @{
    "8000" = "Backend (Django)"
    "3000" = "Frontend (React/Vite)"
    "5000" = "OTP Service (Node.js)"
}

$stoppedCount = 0

foreach ($port in $ports.Keys) {
    $serviceName = $ports[$port]
    Write-Host "🔍 Checking port $port ($serviceName)..." -ForegroundColor Cyan
    
    $connections = netstat -ano | Select-String ":$port\s+.*LISTENING"
    
    if ($connections) {
        foreach ($conn in $connections) {
            $pid = ($conn -split '\s+')[-1]
            
            try {
                $process = Get-Process -Id $pid -ErrorAction Stop
                Write-Host "   ├─ Found process: $($process.ProcessName) (PID: $pid)" -ForegroundColor Yellow
                Write-Host "   └─ Stopping..." -NoNewline -ForegroundColor Yellow
                
                Stop-Process -Id $pid -Force -ErrorAction Stop
                Write-Host " ✅ Stopped" -ForegroundColor Green
                $stoppedCount++
                Start-Sleep -Milliseconds 500
            } catch {
                Write-Host " ⚠️  Already stopped" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "   └─ No process found" -ForegroundColor Gray
    }
}

# Stop Desktop App (PyQt5)
Write-Host ""
Write-Host "🔍 Checking Desktop App (PyQt5)..." -ForegroundColor Cyan

$desktopProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object { 
    $_.Path -like "*EquipSense*" -and $_.MainWindowTitle -ne ""
}

if ($desktopProcesses) {
    foreach ($proc in $desktopProcesses) {
        Write-Host "   ├─ Found process: python (PID: $($proc.Id))" -ForegroundColor Yellow
        Write-Host "   └─ Stopping..." -NoNewline -ForegroundColor Yellow
        
        try {
            Stop-Process -Id $proc.Id -Force -ErrorAction Stop
            Write-Host " ✅ Stopped" -ForegroundColor Green
            $stoppedCount++
        } catch {
            Write-Host " ⚠️  Already stopped" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "   └─ No process found" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Green

if ($stoppedCount -gt 0) {
    Write-Host "   ✅ Stopped $stoppedCount service(s)" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  No running services found" -ForegroundColor Yellow
}

Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Final verification
Write-Host "🔍 Verifying shutdown..." -ForegroundColor Cyan
$remainingPorts = @()

foreach ($port in $ports.Keys) {
    $check = netstat -ano | Select-String ":$port\s+.*LISTENING"
    if ($check) {
        $remainingPorts += $port
    }
}

if ($remainingPorts.Count -gt 0) {
    Write-Host "   ⚠️  Some services still running on ports: $($remainingPorts -join ', ')" -ForegroundColor Yellow
    Write-Host "   Try running this script again or manually close terminal windows" -ForegroundColor Gray
} else {
    Write-Host "   ✅ All services stopped successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "✨ Shutdown complete!" -ForegroundColor Green
Write-Host ""
