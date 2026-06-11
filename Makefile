# ============================================================
# UAWOS — Universal AI Workforce Operating System
# Makefile — Unified development command interface
# ============================================================
# Usage:
#   make setup      — Create venv, install dependencies, copy .env
#   make run        — Start the UAWOS dashboard daemon
#   make test       — Run all self-tests
#   make lint       — Run linting and formatting checks
#   make health     — Check infrastructure service health
#   make infra-up   — Start Docker infrastructure (core profile)
#   make infra-full — Start all Docker infrastructure
#   make infra-down — Stop all Docker infrastructure
#   make clean      — Remove venv and caches
#   make docker     — Build the UAWOS BFF Docker image
# ============================================================

.DEFAULT_GOAL := help

# Detect OS and set Python/pip paths
ifeq ($(OS),Windows_NT)
    PYTHON := .venv\Scripts\python.exe
    PIP := .venv\Scripts\pip.exe
    VENV_CREATE := python -m venv .venv
    SEP := \\
    RM_RF := rmdir /s /q
    COPY := copy
    ACTIVATE_HINT := .venv\Scripts\Activate.ps1
else
    PYTHON := .venv/bin/python
    PIP := .venv/bin/pip
    VENV_CREATE := python3 -m venv .venv
    SEP := /
    RM_RF := rm -rf
    COPY := cp
    ACTIVATE_HINT := source .venv/bin/activate
endif

# ---- Primary Targets ----

.PHONY: help
help: ## Show this help message
	@echo.
	@echo UAWOS Development Commands:
	@echo ===========================
	@echo   make setup        Create venv, install deps, copy .env
	@echo   make run          Start the dashboard daemon
	@echo   make test         Run all self-tests
	@echo   make lint         Run ruff linting
	@echo   make health       Check infrastructure health
	@echo   make infra-up     Start core Docker services
	@echo   make infra-full   Start all Docker services
	@echo   make infra-down   Stop Docker services
	@echo   make docker       Build the BFF Docker image
	@echo   make clean        Remove venv and caches
	@echo.

.PHONY: setup
setup: .venv .env ## Create venv, install dependencies, prepare environment
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	@echo.
	@echo ============================================
	@echo  UAWOS setup complete!
	@echo  Activate your venv:  $(ACTIVATE_HINT)
	@echo  Start infra:         make infra-up
	@echo  Start daemon:        make run
	@echo ============================================

.venv:
	$(VENV_CREATE)

.env:
ifeq ($(OS),Windows_NT)
	@if not exist .env $(COPY) .env.example .env
else
	@test -f .env || $(COPY) .env.example .env
endif

.PHONY: run
run: ## Start the UAWOS dashboard daemon
	$(PYTHON) uawos_dashboard_daemon.py

.PHONY: test
test: ## Run all self-tests
	$(PYTHON) scratch$(SEP)run_all_self_tests.py

.PHONY: test-pytest
test-pytest: ## Run tests via pytest (if installed)
	$(PYTHON) -m pytest scratch/ -v --tb=short

.PHONY: lint
lint: ## Run ruff linting and formatting checks
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

.PHONY: format
format: ## Auto-format code with ruff and black
	$(PYTHON) -m ruff check --fix .
	$(PYTHON) -m ruff format .

.PHONY: typecheck
typecheck: ## Run mypy type checking
	$(PYTHON) -m mypy uawos_dashboard_daemon.py uawos_db.py uawos_context.py --ignore-missing-imports

.PHONY: audit
audit: ## Run dependency vulnerability audit
	$(PYTHON) -m pip_audit

.PHONY: health
health: ## Check infrastructure service health
	@echo Checking UAWOS infrastructure...
	$(PYTHON) -c "import json; exec(open('scratch/health_check.py').read())" 2>/dev/null || \
	$(PYTHON) -c "\
import socket;\
services = [('PostgreSQL', '127.0.0.1', 5435), ('Qdrant', '127.0.0.1', 6333), ('OPA', '127.0.0.1', 8181), ('OpenFGA', '127.0.0.1', 8083), ('Daemon', '127.0.0.1', 8099)];\
[print(f'  {n:.<30} {\"OK\" if (lambda h,p: (lambda s: (s.settimeout(1), s.connect((h,p)), s.close(), True))( socket.socket(socket.AF_INET, socket.SOCK_STREAM)))(h,p) else \"DOWN\"}') for n,h,p in services]\
" 2>nul || echo "  Run 'make infra-up' to start infrastructure."

# ---- Infrastructure ----

.PHONY: infra-up
infra-up: ## Start core Docker services (postgres, qdrant, opa, openfga)
	docker compose --profile core up -d

.PHONY: infra-full
infra-full: ## Start ALL Docker services
	docker compose --profile core --profile full up -d

.PHONY: infra-down
infra-down: ## Stop all Docker services
	docker compose --profile core --profile full down

.PHONY: infra-destroy
infra-destroy: ## Stop all Docker services AND remove volumes
	docker compose --profile core --profile full down -v

.PHONY: db-init
db-init: ## Initialize PostgreSQL and Qdrant schemas
	$(PYTHON) -c "import uawos_db; uawos_db.init_db(); uawos_db.init_qdrant(); print('Database initialization complete.')"

# ---- Docker ----

.PHONY: docker
docker: ## Build the UAWOS BFF Docker image
	docker build -t uawos-bff-image:latest .

.PHONY: docker-run
docker-run: ## Run the UAWOS BFF as a Docker container
	docker run --rm -p 8099:8099 --env-file .env --name uawos-bff uawos-bff-image:latest

# ---- Cleanup ----

.PHONY: clean
clean: ## Remove venv, caches, and build artifacts
ifeq ($(OS),Windows_NT)
	@if exist .venv $(RM_RF) .venv
	@if exist __pycache__ $(RM_RF) __pycache__
	@if exist dist $(RM_RF) dist
	@if exist build $(RM_RF) build
	@if exist *.egg-info $(RM_RF) *.egg-info
else
	$(RM_RF) .venv __pycache__ dist build *.egg-info
endif
	@echo Cleaned.
