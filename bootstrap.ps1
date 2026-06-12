#!/usr/bin/env pwsh
# ==============================================================================
# UAWOS Bootstrap Script — Windows PowerShell
# One-command developer environment setup
# Usage: .\bootstrap.ps1 [-Minimal]
# ==============================================================================
param(
    [switch]$Minimal
)

$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) { $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $ScriptDir) { $ScriptDir = Get-Location }

Set-Location $ScriptDir

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   UAWOS — Universal AI Workforce Operating System        ║" -ForegroundColor Cyan
Write-Host "║   Bootstrap Setup Script (Windows)                       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# --- Check prerequisites ---
Write-Host "► Checking prerequisites..." -ForegroundColor Yellow

function Test-Command($cmd, $url) {
    try {
        $null = & $cmd --version 2>&1
        Write-Host "  ✓ $cmd found" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  ✗ $cmd not found. Install from: $url" -ForegroundColor Red
        return $false
    }
}

$ok = $true
$ok = (Test-Command "python" "https://www.python.org/downloads/") -and $ok
$ok = (Test-Command "docker" "https://www.docker.com/products/docker-desktop/") -and $ok
$ok = (Test-Command "git" "https://git-scm.com/downloads") -and $ok

if (-not $ok) {
    Write-Host "`nPlease install the missing prerequisites and re-run." -ForegroundColor Red
    exit 1
}

# Python version check
$pyVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$parts = $pyVersion.Split(".")
if ([int]$parts[0] -lt 3 -or ([int]$parts[0] -eq 3 -and [int]$parts[1] -lt 10)) {
    Write-Host "  ✗ Python 3.10+ required. Found: $pyVersion" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Python $pyVersion (>=3.10)" -ForegroundColor Green

# --- Virtual environment ---
Write-Host ""
Write-Host "► Setting up Python virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "  ✓ Virtual environment already exists" -ForegroundColor Green
}

# --- Install dependencies ---
Write-Host ""
Write-Host "► Installing Python dependencies..." -ForegroundColor Yellow
& ".venv\Scripts\pip.exe" install --upgrade pip --quiet

if ($Minimal) {
    Write-Host "  [Minimal mode] Installing core runtime only..." -ForegroundColor Gray
    & ".venv\Scripts\pip.exe" install fastapi uvicorn psycopg2-binary qdrant-client networkx --quiet
} else {
    try {
        & ".venv\Scripts\pip.exe" install -e ".[dev]" --quiet
    } catch {
        & ".venv\Scripts\pip.exe" install -r requirements.txt --quiet
    }
}
Write-Host "  ✓ Dependencies installed" -ForegroundColor Green

# --- Environment configuration ---
Write-Host ""
Write-Host "► Configuring environment..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  ✓ Created .env from .env.example" -ForegroundColor Green
    Write-Host "  ⚠  Edit .env to set your passwords before production use!" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ .env already exists" -ForegroundColor Green
}

# --- Docker infrastructure ---
Write-Host ""
Write-Host "► Starting core Docker infrastructure..." -ForegroundColor Yellow
try {
    docker compose --profile core up -d 2>&1 | Out-Null
    Write-Host "  ✓ Core services started (postgres, qdrant, opa, openfga)" -ForegroundColor Green
} catch {
    Write-Host "  ⚠  Docker Compose failed — ensure Docker Desktop is running." -ForegroundColor Yellow
    Write-Host "     Start manually later: docker compose --profile core up -d" -ForegroundColor Gray
}

# --- Pull tinyllama model for Ollama ---
Write-Host ""
Write-Host "► Checking Ollama local model..." -ForegroundColor Yellow
$ollamaUrl = "http://127.0.0.1:11434"
try {
    $tags = Invoke-RestMethod -Uri "$ollamaUrl/api/tags" -Method Get -TimeoutSec 5
    $hasModel = $false
    if ($tags -and $tags.models) {
        foreach ($m in $tags.models) {
            if ($m.name -like "*tinyllama*") {
                $hasModel = $true
                break
            }
        }
    }
    if (-not $hasModel) {
        Write-Host "  ... Pulling tinyllama model (this may take a minute)..." -ForegroundColor Yellow
        $body = @{ name = "tinyllama" } | ConvertTo-Json
        $null = Invoke-RestMethod -Uri "$ollamaUrl/api/pull" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 300
        Write-Host "  ✓ tinyllama model pulled successfully" -ForegroundColor Green
    } else {
        Write-Host "  ✓ tinyllama model already present" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠  Ollama is not running on $ollamaUrl or failed to pull model." -ForegroundColor Yellow
    Write-Host "     Please start Ollama and run: ollama pull tinyllama" -ForegroundColor Gray
}

# --- Wait for PostgreSQL ---
Write-Host ""
Write-Host "► Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
$ready = $false
for ($i = 1; $i -le 20; $i++) {
    try {
        & ".venv\Scripts\python.exe" -c "import psycopg2; psycopg2.connect('host=127.0.0.1 port=5435 dbname=marquez user=marquez password=marquez')" 2>$null
        Write-Host "  ✓ PostgreSQL is ready" -ForegroundColor Green
        $ready = $true
        break
    } catch {
        Write-Host "  ... waiting ($i/20)" -ForegroundColor Gray
        Start-Sleep -Seconds 3
    }
}
if (-not $ready) {
    Write-Host "  ⚠  PostgreSQL not yet ready — start daemon after services are up." -ForegroundColor Yellow
}

# --- Done ---
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅  UAWOS setup complete!                               ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  Activate venv:  .venv\Scripts\Activate.ps1             ║" -ForegroundColor Green
Write-Host "║  Start daemon:   .venv\Scripts\python uawos_dashboard_daemon.py" -ForegroundColor Green
Write-Host "║    or:           make run                                ║" -ForegroundColor Green
Write-Host "║  Dashboard:      http://localhost:8099                   ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
