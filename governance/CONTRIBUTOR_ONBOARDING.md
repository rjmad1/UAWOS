# UAWOS Contributor Onboarding Guide

Welcome to the Universal AI Workforce Operating System (UAWOS) developer onboarding guide. This document establishes setup instructions, coding conventions, and a Component Owner Mapping table to distribute knowledge across the engineering team, ensuring the platform's bus factor is maximized.

---

## 1. Quick Start Setup Instructions

### 1.1 Prerequisites
* Python 3.10 or 3.11
* Docker & Docker Compose
* Git

### 1.2 Development Environment Initialization
1. Clone the repository and navigate to the project root:
   ```powershell
   git clone https://github.com/rjmad1/UAWOS.git
   cd UAWOS
   ```
2. Initialize virtual environment and install dependencies:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Boot the operational database and security sidecars (PostgreSQL, Qdrant, OPA, OpenFGA, Marquez):
   ```powershell
   docker compose up -d
   ```
4. Run the operational check script to verify local service health:
   ```powershell
   python validate_capabilities.py
   ```
5. Run the developer test suite:
   ```powershell
   python -m pytest scratch/
   ```

---

## 2. Core Coding Conventions

1. **Strict Concurrency Safety:** When performing read-modify-write loops on local JSON files or shared database tables, always wrap operations in the `state_transaction` lock helper from `uawos_state_utils.py` to prevent PostgreSQL deadlock conditions.
2. **License Isolation (POL-03):** Never import `marker` directly into any python engine. Parse PDFs exclusively using the sandboxed container service via REST call on port 5001.
3. **Multi-Tenancy Isolation:** Always resolve and pass `tenant_id` from the context using the `uawos_context.get_tenant_id()` method.
4. **Structured Logging:** Emit OpenLineage execution context tokens on Marquez metadata registries rather than raw print logs.

---

## 3. Engine & Component Owner Mapping

To resolve the bus factor gap of 1, each of the 21 UAWOS operational engines has a designated Principal Owner and an active Secondary Backup Cover.

| # | Python Module / Component | Engine Functional Area | Primary Owner | Backup Cover | Reviewer Scope |
|---|---------------------------|-------------------------|---------------|--------------|----------------|
| 1 | `uawos_objective.py` | Objective Management | Enterprise Arch | Software Arch | System Lead |
| 2 | `uawos_outcome.py` | Outcome Management | FinOps Lead | Product Owner | FinOps Team |
| 3 | `uawos_planning.py` | Planning & Simulation | Software Arch | Enterprise Arch | Platform Team |
| 4 | `uawos_workflow.py` | Workflow Orchestration | Platform Eng Lead | SRE Lead | Dev Team |
| 5 | `uawos_action.py` | Action Lifecycle | Platform Eng Lead | Software Arch | Dev Team |
| 6 | `uawos_workforce.py` | Workforce Coordination | Software Arch | Platform Eng Lead| Dev Team |
| 7 | `uawos_agent_workforce.py`| Agent Identities & Trust| Security Arch | Software Arch | Security Team  |
| 8 | `uawos_governance.py` | Governance & Exceptions | Security Arch | FinOps Lead | Governance Bd  |
| 9 | `uawos_knowledge.py` | Knowledge Management | Knowledge Eng | Software Arch | Knowledge Team |
| 10| `uawos_memory.py` | Memory Infrastructure | Knowledge Eng | Platform Eng Lead| Knowledge Team |
| 11| `uawos_learning.py` | Continuous Learning | Knowledge Eng | Software Arch | AI Council |
| 12| `uawos_resource.py` | Resource Allocations | SRE Lead | Platform Eng Lead| Ops Team |
| 13| `uawos_budget.py` | Budget & Cost Management| FinOps Lead | Security Arch | FinOps Team |
| 14| `uawos_decision.py` | Decision Causal Capture | Software Arch | Product Owner | Platform Team |
| 15| `uawos_simulation.py` | Scenario Forecasting | Software Arch | SRE Lead | Platform Team |
| 16| `uawos_value.py` | Value Realization | FinOps Lead | Product Owner | FinOps Team |
| 17| `uawos_observability.py` | System Observability | SRE Lead | Platform Eng Lead| Ops Team |
| 18| `uawos_integrations.py` | Adapters & Webhooks | Platform Eng Lead | SRE Lead | Dev Team |
| 19| `uawos_pmcms.py` | Maturity Calculation | SRE Lead | Enterprise Arch | Operations Bd  |
| 20| `uawos_dtase.py` | Domain Translation | Knowledge Eng | Security Arch | Knowledge Team |
| 21| `uawos_dashboard_daemon.py`| BFF & APIs Server | Platform Eng Lead | SRE Lead | Platform Team |
