# Contributing to UAWOS

Thank you for your interest in contributing to the **Universal AI Workforce Operating System (UAWOS)**! This guide covers the development workflow, code standards, and PR process.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Branch Strategy](#branch-strategy)
- [Commit Message Format](#commit-message-format)
- [Reporting Issues](#reporting-issues)

---

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork:
   ```powershell
   git clone https://github.com/<your-username>/UAWOS.git
   cd UAWOS
   ```
3. **Add upstream remote:**
   ```powershell
   git remote add upstream https://github.com/rjmad1/UAWOS.git
   ```

---

## Development Setup

```powershell
# 1. Create virtual environment and install all deps
make setup

# 2. Copy and configure environment variables
copy .env.example .env
# Edit .env with your local settings

# 3. Start core infrastructure
make infra-up

# 4. Initialize the database
make db-init

# 5. Start the daemon
make run
```

### Manual Setup (without make)

```powershell
python -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
copy .env.example .env
docker compose --profile core up -d
.venv\Scripts\python uawos_dashboard_daemon.py
```

---

## Code Standards

### Style

- **Line length:** 120 characters max
- **Formatter:** `ruff format` (Black-compatible)
- **Linter:** `ruff check`
- **Type hints:** Encouraged for all new public functions

Run before committing:
```powershell
make lint     # Check for issues
make format   # Auto-fix formatting
```

### Architecture Rules

1. **One engine per module** — each `uawos_*.py` file manages exactly one domain
2. **No cross-engine direct imports** — engines communicate via the state layer (`uawos_db.py`) not direct function calls
3. **Graceful degradation** — all external service calls must use try/except with a working fallback
4. **Multi-tenancy** — always pass `tenant_id` through `uawos_context.get_tenant_id()` 
5. **No GPLv3 imports** — any GPL-licensed library must go through the isolated `marker-service` REST API
6. **State via PostgreSQL** — use `uawos_state_utils.load_state()` / `save_state()` — never read/write JSON files directly

### Pre-commit Hooks (Optional but Recommended)

```powershell
.venv\Scripts\pre-commit install
```

This runs ruff, gitleaks (secret detection), and trailing-whitespace checks automatically on every commit.

---

## Testing

Every engine module must have a `run_self_tests()` function that verifies its own functional requirements:

```python
def run_self_tests():
    print("Running <Engine> self tests...")
    tests = [
        ("FR-XXX", verify_fr_xxx),
        ...
    ]
    for code, fn in tests:
        try:
            fn()
            print(f"  [PASS] {code} verified.")
        except AssertionError as e:
            print(f"  [FAIL] {code}: {e}")
```

Run all tests:
```powershell
make test
```

Run a single engine's tests:
```powershell
.venv\Scripts\python uawos_objective.py
```

All tests must pass before submitting a PR.

---

## Pull Request Process

1. **Create a feature branch** from `develop`:
   ```powershell
   git checkout develop
   git pull upstream develop
   git checkout -b feature/my-feature
   ```

2. **Make your changes** — keep commits focused and atomic

3. **Run the full test suite:**
   ```powershell
   make lint
   make test
   ```

4. **Push and open a PR** against `develop` (not `main`)

5. **PR checklist:**
   - [ ] Tests pass locally
   - [ ] Lint passes (`make lint`)
   - [ ] New functionality has `verify_fr_xxx()` tests
   - [ ] Documentation updated (wiki or inline docstrings)
   - [ ] No hardcoded credentials or paths
   - [ ] No new GPL-licensed dependencies imported directly

6. **Review:** At least 1 approval required before merge

---

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable production releases — merge via PR only |
| `develop` | Integration branch — merge feature/* branches here |
| `feature/*` | New features and improvements |
| `fix/*` | Bug fixes |
| `chore/*` | Dependency updates, refactoring, tooling |

---

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

[optional body]

[optional footer]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`

**Examples:**
```
feat(governance): add OpenFGA ReBAC check for budget actions
fix(db): handle psycopg2 reconnect on transient connection loss
docs(install): add Linux setup instructions to wiki guide
chore(deps): pin qdrant-client to v1.9.7
ci: add gitleaks secret scanning to GitHub Actions
```

---

## Reporting Issues

Use [GitHub Issues](https://github.com/rjmad1/UAWOS/issues) with one of the following labels:

- **bug** — Something isn't working
- **enhancement** — New feature request
- **documentation** — Documentation gap or error
- **security** — Security vulnerability (use private disclosure for critical issues)
- **good first issue** — Good for new contributors

When reporting a bug, include:
1. UAWOS version / git commit hash
2. Operating system and Python version
3. Steps to reproduce
4. Expected vs. actual behaviour
5. Relevant log output from the daemon console
