# Changelog

All notable changes to UAWOS are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.7.0] — 2026-06-12 — Agent Framework Integration (Waves 0-6)

### Added
- **LangGraph Adapter**: Integrated `uawos_langgraph_adapter.py` compiling state graphs with per-node interceptors, workflow state machines, and a PostgreSQL checkpointer backend.
- **Semantic Kernel Adapter**: Integrated `uawos_semantic_kernel_adapter.py` providing Microsoft Copilot kernel orchestrations, function invocation filters, and a vector memory bridge to Qdrant.
- **AutoGen Adapter**: Integrated `uawos_autogen_adapter.py` enabling conversable agents and group chats with Docker-based sandboxed code execution, conversational message auditors, and Rego-governed speaker selection policies.
- **Traceability Event Bus**: Added `uawos_event_bus.py` schema-validating ESLS events, managing tenant-aware correlation/causation ID propagation, and supporting event replay.
- **Sandbox Runtime**: Added `uawos_sandbox_runtime.py` with `UAWOSSandboxToolExecutor` routing to isolated environments, the `UAWOSSecretsManager` vault with regex secret redaction, and tool registries.
- **Audit and Replay Ledger**: Added `uawos_audit_ledger.py` supporting immutable append-only ledgers, SQL checkpointers with time-travel replay, Marquez-compatible OpenLineage emitters, and explainability reports.
- **Unified Interfaces**: Added `uawos_agent_runtime.py` defining abstract contracts for adapters (`IPolicyEvaluator`, `IAuditProvider`, `ITraceProvider`, `IToolExecutor`, `IAgentRuntime`, `IWorkflowRuntime`).

---

## [0.6.0] — 2026-06-12 — Level 5.0 Memory Upgrade & Client SDK

### Added
- **Level 5.0 Memory Management**: Upgraded `uawos_memory.py` with PostgreSQL session-backed short-term memory (STM), episodic timelines, advisory locks for thread-safe concurrency, RRF-based hybrid search, continuous reflection, and automatic semantic consolidation.
- **Client SDK**: Added `uawos_sdk.py` programmatically exposing UAWOS objective, memory, and search features to third-party integrations.
- **Admin CLI**: Added `uawos_cli.py` commands (`register-agent` and `mcp-connect`) for onboarding and connecting agents.
- **Validation Framework**: Added `validate_capabilities.py` auditing all 15 key platform capabilities with 100% verification confidence.
- **Memory Verification Suite**: Added `verify_upgraded_memory.py` self-tests.
- **Billing & Subscription**: Added `verify_subscription` and mock Stripe webhook handler in `uawos_integrations.py`.

### Changed
- **Objective Ingestion**: Integrated `uawos_dtase` to analyze unstructured intake inputs.
- **Dynamic Routing**: Implemented dynamic workforce auto-routing based on required agent capabilities and trust metrics in `uawos_planning.py`.

---

## [0.5.0] — 2026-06-11 — MVP Fully Validated

### Added
- All 20 core platform engines implemented and self-tested (250+ functional requirements verified)
- `uawos_dashboard_daemon.py` — FastAPI BFF daemon serving the operational command centre on port 8099
- `uawos_traceability.py` — Live requirements traceability matrix (FR-011 → FR-257) with health-driven status
- `uawos_requirement_studio.py` — AI-powered requirement authoring, INVEST scoring, and candidate pipeline
- `uawos_dtase.py` — Domain Translation & Artifact Synthesis Engine (DTASE v1.0) with heuristic + LLM enrichment
- `uawos_pmcms.py` — Platform Maturity & Capability Model with 5-level scoring across 9 domains
- `uawos_governance.py` — OPA Rego policy engine + OpenFGA fine-grained ReBAC authorization
- `uawos_context.py` — Thread-safe multi-tenant context propagation via Python `ContextVar`
- `uawos_state_utils.py` — Unified PostgreSQL-backed state persistence (replaces JSON file fallbacks)
- Docker Compose infrastructure stack: PostgreSQL, Qdrant, Marquez, Superset, Dependency-Track, OPA, OpenFGA, Marker Service, Neo4j, ClickHouse, Kafka, Temporal
- Terraform IaC for AWS ECS Fargate deployment
- Wiki documentation: Installation Guide, Architecture Overview, Platform Engines, API Reference, Governance & Compliance, Infrastructure & Deployment, AI Workforce Model, Roadmap
- `Requirements Master/` — 40+ standards documents (PRDs, ADRs, architecture standards)
- PowerShell automation scripts: `run-daemon-persistent.ps1`, `register-scheduled-task.ps1`, `sync-git.ps1`

### Architecture
- Wave 1 state migration: All JSON file state deprecated and moved to PostgreSQL
- Multi-tenant isolation enforced via `uawos_context.get_tenant_id()` across all engines
- GPLv3 isolation pattern: `marker` PDF library wrapped in isolated REST microservice
- Graceful degradation pattern: all external service calls fail-safe with deterministic fallbacks

---

## [0.5.1] — 2026-06-11 — Repository Hardening (Enterprise Readiness Audit)

### Added
- `pyproject.toml` — Formal Python package metadata with grouped optional dependency extras (`ai`, `memory`, `rag`, `data`, `simulation`, `governance`, `dev`)
- `Dockerfile` — Multi-stage production Docker image for UAWOS BFF daemon (non-root user, health check, OCI labels)
- `.dockerignore` — Build context exclusions for faster, smaller Docker builds
- `.env.example` — Template documenting all 30+ environment variables with safe defaults
- `Makefile` — Unified cross-platform command interface (`make setup`, `make run`, `make test`, `make infra-up`, `make health`, etc.)
- `.github/workflows/ci.yml` — GitHub Actions CI pipeline: lint → test → security scan → Docker build
- `LICENSE` — Apache License 2.0
- `CONTRIBUTING.md` — Developer contribution guide covering setup, code standards, PR process, branch strategy
- `bootstrap.ps1` — One-command Windows setup script
- `bootstrap.sh` — One-command macOS/Linux setup script
- `.pre-commit-config.yaml` — Pre-commit hooks: ruff, gitleaks, trailing whitespace

### Changed
- `requirements.txt` — Added missing core runtime deps: `fastapi`, `uvicorn`, `psycopg2-binary`, `qdrant-client`
- `docker-compose.yml` — Pinned all 15 service image versions (no more `:latest`); added Docker Compose profiles (`core`, `full`); externalized all secrets to env vars; added health checks to 6 previously unchecked services; removed deprecated `version: '3.8'` field; changed `NEO4J_AUTH=none` to require authentication
- `.gitignore` — Added `.env`, `*.tfvars`, `__pycache__/`, IDE configs, test output files, coverage reports
- `terraform/outputs.tf` — Fixed unquoted resource references (were string literals, not Terraform expressions)
- `run-daemon-persistent.ps1` — Replaced hardcoded `C:\Users\rajaj\Projects\UAWOS` with `$PSScriptRoot` dynamic resolution
- `register-scheduled-task.ps1` — Replaced hardcoded path with `$PSScriptRoot` dynamic resolution
- `uawos-dashboard.vbs` — Replaced hardcoded path with `WScript.ScriptFullName` dynamic resolution
- `scratch/run_all_self_tests.py` — Replaced hardcoded path with `os.path.dirname(__file__)` dynamic resolution

### Security
- All hardcoded passwords externalized to `.env.example` with `change-me-in-production` defaults
- `UAWOS_SECURE_TOKEN` default changed to prompt-to-change value with startup warning
- `SUPERSET_SECRET_KEY` externalized from docker-compose.yml
- `NEO4J_AUTH=none` replaced with proper authentication requirement
- Caesar cipher `encrypt_data()` noted for replacement with `cryptography.fernet` (tracked as issue)

---

## [Unreleased]

### Planned
- Migrate tests to `pytest` framework
- Add `alembic` for database schema versioning
- Helm chart for Kubernetes deployment
- Replace Caesar cipher encryption with `cryptography.fernet`
- Structured JSON logging with correlation IDs
- OpenTelemetry instrumentation
- API versioning (`/api/v1/` prefix)
