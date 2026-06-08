# Universal AI Workforce Operating System (UAWOS)

# Agent Catalog

## Version

1.0

## Status

Normative Catalog Specification

---

# 1. Purpose

This catalog details the mandatory and specialized AI workforce agent classes, their memory configurations, available toolsets, and structural assignments within the UAWOS architecture. It aligns with the [Workforce, Agent & Autonomy Standard (WAAS)](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/Workforce,%20Agent%20&%20Autonomy%20Standard%20(WAAS).md).

---

# 2. Mandatory Agent Classes

Every UAWOS-compliant runtime instance MUST register and support the following core agent classes:

### 2.1. Planner Agent
* **Purpose**: Deconstructs objective intent, evaluates alternatives, and outputs execution plans.
* **Specialized Memory**: Short-term plan history, context maps.
* **Core Toolset**: Plan Generators, Dependency analyzers.
* **Council Assignment**: Architecture Council, Strategy Council.

### 2.2. Orchestrator Agent
* **Purpose**: Coordinates work processes, assigns tasks to executors, and monitors states.
* **Specialized Memory**: Active workflow run states, execution logs.
* **Core Toolset**: State managers, Scheduler controls.
* **Council Assignment**: Product Council.

### 2.3. Executor Agent
* **Purpose**: Performs actions, edits code, writes documents, and generates artifacts.
* **Specialized Memory**: Task context, file buffers.
* **Core Toolset**: Filesystem MCP, GitLab/GitHub MCP, Terminal executables.
* **Council Assignment**: None.

### 2.4. Reviewer Agent
* **Purpose**: Audits work outputs, reviews code changes, and checks document alignment.
* **Specialized Memory**: Review checklists, quality standards.
* **Core Toolset**: Semgrep MCP, SonarQube MCP.
* **Council Assignment**: Architecture Council, Security Council.

### 2.5. Governor Agent
* **Purpose**: Enforces system policies, checks license compliance, and scores risk.
* **Specialized Memory**: Policy Graph cache, active risk rules.
* **Core Toolset**: OPA evaluator, OpenFGA client.
* **Council Assignment**: Governance Council (Core Lead).

### 2.6. Learner Agent
* **Purpose**: Analyzes logs and performance feedback to generate system optimizations.
* **Specialized Memory**: Historical optimization records, feedback scores.
* **Core Toolset**: DSPy optimizer, evaluation query scripts.
* **Council Assignment**: Research Council.

### 2.7. Knowledge Manager Agent
* **Purpose**: Cures memory graphs, indexes documents, and manages organizational ontologies.
* **Specialized Memory**: Graphiti temporal cache, Wikidata endpoints.
* **Core Toolset**: Neo4j MCP, LlamaIndex tools.
* **Council Assignment**: Research Council.

---

# 3. Specialized Agent Classes

### 3.1. Portfolio Governor Agent
* **Purpose**: Optimizes strategic project portfolios and business outcome alignment.
* **Specialized Memory**: Strategic outcomes database.
* **Core Toolset**: Value forecasters.
* **Council Assignment**: Strategy Council (Core Lead).

### 3.2. Value Analyst Agent
* **Purpose**: Measures outcome metrics and compiles value realization sheets.
* **Specialized Memory**: Value Graph data.
* **Core Toolset**: dbt-core query tool, Superset API.
* **Council Assignment**: Strategy Council.

### 3.3. Resource Manager Agent
* **Purpose**: Plans resource capacity, computes work limits, and monitors billing.
* **Specialized Memory**: Team workload charts, API token budgets.
* **Core Toolset**: Capacity models, budget auditors.
* **Council Assignment**: Product Council.

### 3.4. Simulation Agent
* **Purpose**: Runs scenario forecasting models and models agent team trajectories.
* **Specialized Memory**: Simulation state snapshots.
* **Core Toolset**: Mesa models, NetworkX algorithms.
* **Council Assignment**: Architecture Council.

### 3.5. Challenger Agent
* **Purpose**: Performs contrarian assessments of plans and lists hidden assumptions.
* **Specialized Memory**: Common risk patterns database.
* **Core Toolset**: Red-teaming prompts, risk check lists.
* **Council Assignment**: Security Council, Research Council.

---

# 4. Agent Memory Architecture Configuration

Each agent maintains a tiered memory model:
1. **Short-Term Memory**: Session variables, local state (handled via LangGraph state models).
2. **Long-Term Memory**: Declarative user facts and personal context (handled via Mem0).
3. **Temporal Graph Memory**: Networked event relationships (handled via Graphiti temporal schemas stored in Qdrant/Neo4j).
