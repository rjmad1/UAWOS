#!/usr/bin/env bash
# ==============================================================================
# UAWOS Bootstrap Script — macOS / Linux
# One-command developer environment setup
# Usage: ./bootstrap.sh [--minimal]
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MINIMAL=${1:-""}

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   UAWOS — Universal AI Workforce Operating System        ║"
echo "║   Bootstrap Setup Script (macOS / Linux)                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

cd "$SCRIPT_DIR"

# --- Check prerequisites ---
echo "► Checking prerequisites..."

check_cmd() {
    if ! command -v "$1" &>/dev/null; then
        echo "  ✗ $1 not found. Please install it and re-run."
        echo "    See: $2"
        exit 1
    else
        echo "  ✓ $1 found: $($1 --version 2>&1 | head -1)"
    fi
}

check_cmd python3   "https://www.python.org/downloads/"
check_cmd docker    "https://docs.docker.com/get-docker/"
check_cmd git       "https://git-scm.com/downloads"

# --- Python version check ---
PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]); then
    echo "  ✗ Python 3.10+ required. Found: $PY_VERSION"
    exit 1
fi

# --- Virtual environment ---
echo ""
echo "► Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "  ✓ Virtual environment created at .venv"
else
    echo "  ✓ Virtual environment already exists"
fi

PYTHON=".venv/bin/python"
PIP=".venv/bin/pip"

$PIP install --upgrade pip --quiet

# --- Install dependencies ---
echo ""
echo "► Installing Python dependencies..."
if [ "$MINIMAL" = "--minimal" ]; then
    echo "  [Minimal mode] Installing core runtime only..."
    $PIP install fastapi uvicorn psycopg2-binary qdrant-client networkx --quiet
else
    echo "  Installing core runtime dependencies..."
    $PIP install -e ".[dev]" --quiet 2>/dev/null || \
    $PIP install -r requirements.txt --quiet
fi
echo "  ✓ Dependencies installed"

# --- Environment configuration ---
echo ""
echo "► Configuring environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  ✓ Created .env from .env.example"
    echo "  ⚠  Edit .env to set your passwords before production use!"
else
    echo "  ✓ .env already exists"
fi

# --- Docker infrastructure ---
echo ""
echo "► Starting core Docker infrastructure..."
if docker compose --profile core up -d 2>/dev/null; then
    echo "  ✓ Core services started (postgres, qdrant, opa, openfga)"
else
    echo "  ⚠  Docker Compose failed. Ensure Docker Desktop is running."
    echo "     You can start it manually later: docker compose --profile core up -d"
fi

# --- Wait for PostgreSQL ---
echo ""
echo "► Waiting for PostgreSQL to be ready..."
for i in $(seq 1 20); do
    if $PYTHON -c "import psycopg2; psycopg2.connect('host=127.0.0.1 port=5435 dbname=marquez user=marquez password=marquez')" 2>/dev/null; then
        echo "  ✓ PostgreSQL is ready"
        break
    fi
    echo "  ... waiting ($i/20)"
    sleep 3
done

# --- Done ---
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅  UAWOS setup complete!                               ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Activate venv:  source .venv/bin/activate               ║"
echo "║  Start daemon:   python uawos_dashboard_daemon.py        ║"
echo "║    or:           make run                                ║"
echo "║  Dashboard:      http://localhost:8099                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
