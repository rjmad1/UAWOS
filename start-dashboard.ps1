#!/usr/bin/env pwsh
# start-dashboard.ps1
# Starts the UAWOS status monitoring daemon in the background and opens the web UI.

$Port = 8099
$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) {
    $ScriptDir = Get-Location
}
$DaemonScript = Join-Path $ScriptDir "uawos_dashboard_daemon.py"


# Find active python from virtual environment
$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"
$PythonPath = "python"
if (Test-Path $VenvPython) {
    $PythonPath = $VenvPython
    Write-Host "Using Virtual Environment Python: $PythonPath" -ForegroundColor Green
} else {
    Write-Host "Virtual environment not detected. Falling back to system python..." -ForegroundColor Yellow
}

Write-Host "Checking if dashboard is already running on port $Port..." -ForegroundColor Yellow
$PortActive = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($PortActive) {
    Write-Host "Port $Port is already active. A dashboard instance may already be running." -ForegroundColor Cyan
} else {
    Write-Host "Starting UAWOS Dashboard Daemon in the background..." -ForegroundColor Yellow
    
    $VbsPath = Join-Path $ScriptDir "uawos-dashboard.vbs"
    if (Test-Path $VbsPath) {
        Write-Host "Launching background daemon via VBScript wrapper..." -ForegroundColor Cyan
        Start-Process "wscript.exe" -ArgumentList "`"$VbsPath`""
    } else {
        Write-Host "VBScript wrapper not found. Launching via hidden PowerShell..." -ForegroundColor Yellow
        $PersistentScript = Join-Path $ScriptDir "run-daemon-persistent.ps1"
        Start-Process "powershell.exe" -ArgumentList "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$PersistentScript`""
    }
    Start-Sleep -Seconds 3
}

Write-Host "Opening Dashboard Web Interface..." -ForegroundColor Green
Start-Process "http://localhost:$Port"
Write-Host "Dashboard launched successfully at http://localhost:$Port" -ForegroundColor Green
Write-Host "Logs are being written to $OutLog and $ErrLog" -ForegroundColor Gray
