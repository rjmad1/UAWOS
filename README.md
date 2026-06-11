# Universal AI Workforce Operating System (UAWOS)

[![CI](https://github.com/rjmad1/UAWOS/actions/workflows/ci.yml/badge.svg)](https://github.com/rjmad1/UAWOS/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](./LICENSE)
[![Status: MVP Validated](https://img.shields.io/badge/Status-MVP%20Validated-brightgreen.svg)](#status)

> Transforming Objectives into Measurable Value through Governed Human and AI Workforce Execution.

---

## ⚡ Quick Start

```powershell
# 1. Clone the repository
git clone https://github.com/rjmad1/UAWOS.git
cd UAWOS

# 2. One-command setup (Windows)
.\bootstrap.ps1

# --- OR manually ---
# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env    # then edit .env with your settings

# Start infrastructure
docker compose --profile core up -d

# Start the dashboard
python uawos_dashboard_daemon.py
```

**macOS / Linux:**
```bash
chmod +x bootstrap.sh && ./bootstrap.sh
# or: source .venv/bin/activate && python uawos_dashboard_daemon.py
```

Open **http://localhost:8099** in your browser.

| Interface | URL |
|-----------|-----|
| Main Dashboard | http://localhost:8099 |
| API Status | http://localhost:8099/api/status |
| Roadmap | http://localhost:8099/roadmap |
| Requirement Studio | http://localhost:8099/requirement_studio |
| Architecture | http://localhost:8099/architecture |

> **Full installation guide:** [wiki/Installation-Guide](https://github.com/rjmad1/UAWOS/wiki/Installation-Guide)

---

## Overview

Universal AI Workforce Operating System (UAWOS) is an objective-centric execution platform designed to serve as the operating system for the AI era.

Organizations today manage work through fragmented tools, workflows, documents, meetings, knowledge repositories, and increasingly, AI agents. While these systems digitize work, they do not provide a unified execution fabric capable of transforming organizational intent into measurable outcomes and value.

UAWOS addresses this challenge by introducing a universal operating model where the **Objective** becomes the primary abstraction.

Users define objectives.

The platform automatically discovers context, generates plans, orchestrates human and AI workforce execution, governs decisions and actions, captures organizational knowledge, continuously learns, and measures value realization.

---

## Vision

Enable organizations to operate through objectives rather than tools.

---

## Mission

Transform any objective into measurable value through governed human and AI workforce execution.

---

## Core Concept

```text
Objective
    ↓
Discovery
    ↓
Planning
    ↓
Governance
    ↓
Execution
    ↓
Learning
    ↓
Value Realization
```

---

## What Makes UAWOS Different

Unlike:

* Project Management Platforms
* Workflow Automation Tools
* Knowledge Management Systems
* AI Assistants
* Agent Builders
* Multi-Agent Frameworks

UAWOS serves as a complete execution operating system that unifies:

* Objectives
* Plans
* Workflows
* Human Workforce
* AI Workforce
* Governance
* Knowledge
* Learning
* Resources
* Value Realization

into a single operating model.

---

## Foundational Principles

### Objective-Centric

Everything starts with an Objective.

### Governance-Native

Nothing bypasses governance.

### Knowledge-First

Every interaction becomes organizational intelligence.

### Human Accountability

Humans remain accountable for outcomes.

### AI Workforce

Agents are first-class workforce entities.

### Value Realization

Success is measured by value created, not work completed.

---

## Core Platform Components

### Objective Engine

Transforms intent into structured objectives.

### Domain Translation & Artifact Synthesis Engine (DTASE)

Transforms unstructured human communication and multimodal inputs into structured, domain-specific knowledge and professional-grade execution artifacts.

### Discovery Engine

Identifies assumptions, risks, constraints, stakeholders, and context.

### Planning Engine

Generates and evaluates execution plans.

### Governance Engine

Applies policies, approvals, risk controls, and compliance.

### Execution Engine

Coordinates human and AI workforce execution.

### Knowledge Engine

Builds organizational memory and knowledge graphs.

### Learning Engine

Captures institutional learning and best practices.

### Value Engine

Measures outcomes and value realization.

### Simulation Engine

Forecasts future states and evaluates alternatives.

---

## Core Architecture

```text
Experience Layer
        ↓
Control Plane
        ↓
Platform Engines
        ↓
Federated Graph Layer
        ↓
Integration Layer
        ↓
Infrastructure Layer
```

---

## Federated Graph Model

UAWOS is built on a federated graph architecture.

Core graphs include:

* Objective Graph
* Knowledge Graph
* Agent Graph
* Resource Graph
* Policy Graph
* Value Graph
* Portfolio Graph
* Context Graph

---

## AI Workforce Model

Mandatory workforce agent classes:

* Planner
* Orchestrator
* Executor
* Reviewer
* Governor
* Learner
* Knowledge Manager

Agents operate under governance and collaborate with human workforce members to achieve objectives.

---

## Supported Inputs

* Voice Conversations
* Chat
* Documents
* PDFs
* Images
* Screenshots
* Meetings
* Emails
* Structured Data
* APIs

All inputs are transformed into actionable objectives and organizational knowledge.

---

## Long-Term Vision

UAWOS aims to become the foundational operating system for the Autonomous Enterprise:

A governed, continuously learning environment where human and AI workforce entities collaborate to transform intent into measurable value at scale.

---

## Status

Current Stage: **MVP Implementation — Fully Validated**

All engines are implemented, self-tested, and verified against their FR (Functional Requirements) specifications.

### Implemented & Verified Engines

| Engine | Module | FRs Covered | Tests |
|---|---|---|---|
| Objective Management | `uawos_objective.py` | FR-011 to FR-030 | ✅ 20/20 |
| Outcome Management | `uawos_outcome.py` | FR-031 to FR-040 | ✅ 10/10 |
| Planning | `uawos_planning.py` | FR-041 to FR-060 | ✅ 20/20 |
| Workflow Management | `uawos_workflow.py` | FR-061 to FR-070 | ✅ 10/10 |
| Action Management | `uawos_action.py` | FR-071 to FR-080 | ✅ 10/10 |
| Workforce Management | `uawos_workforce.py` | FR-081 to FR-090 | ✅ 10/10 |
| Agent Workforce | `uawos_agent_workforce.py` | FR-091 to FR-100 | ✅ 10/10 |
| Governance | `uawos_governance.py` | FR-101 to FR-111 | ✅ 11/11 |
| Knowledge Management | `uawos_knowledge.py` | FR-111 to FR-120 | ✅ 10/10 |
| Memory Management | `uawos_memory.py` | FR-121 to FR-130 | ✅ 10/10 |
| Learning | `uawos_learning.py` | FR-131 to FR-140 | ✅ 10/10 |
| Resource Management | `uawos_resource.py` | FR-141 to FR-150 | ✅ 10/10 |
| Budget & Cost | `uawos_budget.py` | FR-151 to FR-160 | ✅ 10/10 |
| Decision Intelligence | `uawos_decision.py` | FR-161 to FR-170 | ✅ 10/10 |
| Simulation & Forecasting | `uawos_simulation.py` | FR-171 to FR-180 | ✅ 10/10 |
| Value Realization | `uawos_value.py` | FR-181 to FR-190 | ✅ 10/10 |
| Observability | `uawos_observability.py` | FR-191 to FR-200 | ✅ 10/10 |
| Integrations & Optimization | `uawos_integrations.py` | FR-201 to FR-250 | ✅ 50/50 |
| Requirement Intelligence Studio | `uawos_requirement_studio.py` | Full pipeline | ✅ Pass |
| PMCMS Maturity | `uawos_pmcms.py` | PMCMS + FR-236 | ✅ Pass |

All changes are fully verified using self-test suites (`scratch/run_all_self_tests.py`) and mapped dynamically into the roadmap and traceability matrices on the dashboard UI.

### Running Tests

```powershell
.venv\Scripts\python.exe scratch\run_all_self_tests.py
```

