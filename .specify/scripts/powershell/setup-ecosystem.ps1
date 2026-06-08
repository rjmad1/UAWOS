#!/usr/bin/env pwsh

# UAWOS Delta Ecosystem Setup & Enablement Script
# Automates Python dependencies and Docker Compose validation for local runtime.

$ErrorActionPreference = 'Stop'
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   UAWOS Delta Ecosystem Discovery & Enablement Layer     " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Python Environment Setup
Write-Host "`n[1/3] Verifying Python Environment..." -ForegroundColor Yellow

$pythonCmd = "python"
$pythonArgs = @()

if (Get-Command py -ErrorAction SilentlyContinue) {
    $pyList = & py --list
    if ($pyList -match "3.11") {
        $pythonCmd = "py"
        $pythonArgs = @("-3.11")
        Write-Host "Preferring Python 3.11 via py launcher for wheel compatibility." -ForegroundColor Green
    }
}

if ($pythonCmd -eq "py" -or (Get-Command python -ErrorAction SilentlyContinue)) {
    if ($pythonCmd -eq "py") {
        $pythonVersion = & py -3.11 --version
    } else {
        $pythonVersion = & python --version
    }
    Write-Host "Using Python: $pythonVersion" -ForegroundColor Green
    
    $venvPath = Join-Path $PSScriptRoot "../../../.venv"
    if (-not (Test-Path $venvPath)) {
        Write-Host "Creating python virtual environment at $venvPath..." -ForegroundColor Cyan
        & $pythonCmd $pythonArgs -m venv $venvPath
    }
    
    # Activate virtual environment
    $pipPath = Join-Path $venvPath "Scripts/pip.exe"
    $pythonVenvPath = Join-Path $venvPath "Scripts/python.exe"
    
    Write-Host "Upgrading pip..." -ForegroundColor Cyan
    & $pythonVenvPath -m pip install --upgrade pip --quiet
    
    Write-Host "Installing python dependencies from requirements.txt..." -ForegroundColor Cyan
    $reqPath = Join-Path $PSScriptRoot "../../../requirements.txt"
    & $pipPath install -r $reqPath
    Write-Host "Python dependencies installed successfully." -ForegroundColor Green
} else {
    Write-Host "WARNING: Python was not found in your PATH. Please install Python 3.10+ to run local libraries." -ForegroundColor Red
}

# 2. Docker & Services Verification
Write-Host "`n[2/3] Verifying Docker environment for infrastructure services..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    $dockerInfo = docker info --format '{{.Name}}' 2>$null
    if ($dockerInfo) {
        Write-Host "Docker is running on: $dockerInfo" -ForegroundColor Green
        Write-Host "Ecosystem containers ready to start using: docker compose up -d" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Docker is installed, but the daemon is not running." -ForegroundColor Red
    }
} else {
    Write-Host "WARNING: Docker command not found. Please install Docker Desktop to run RAG, BI, and Governance databases." -ForegroundColor Red
}

# 3. Qualification Reports
Write-Host "`n[3/3] Enablement Summary..." -ForegroundColor Yellow
Write-Host "Ecosystem Enablement assets configured:" -ForegroundColor Cyan
Write-Host "  - Requirements Config: requirements.txt"
Write-Host "  - Service Orchestration: docker-compose.yml"
Write-Host "  - Setup Automation: .specify/scripts/powershell/setup-ecosystem.ps1"
Write-Host "`nTo start services:" -ForegroundColor Yellow
Write-Host "  docker compose up -d"
Write-Host "`nTo activate virtual environment:" -ForegroundColor Yellow
Write-Host "  .venv\Scripts\Activate.ps1"
Write-Host "`nLocal Endpoints Available Once Docker Compose runs:" -ForegroundColor Yellow
Write-Host "  - Qdrant Vector DB: http://localhost:6333"
Write-Host "  - Apache Superset BI: http://localhost:8088"
Write-Host "  - Marquez Lineage: http://localhost:5000"
Write-Host "  - Dependency-Track Security UI: http://localhost:8085 (Admin UI)"
Write-Host "==========================================================" -ForegroundColor Cyan
