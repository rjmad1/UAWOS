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

### 3.6. Community / Imported Agents (Claude Directory)
These specialized developer agents are imported from [Claude Directory](https://www.claudedirectory.org/) and saved locally in [Requirements Master/claudedirectory_imports/agents/](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/).

| Agent Name | Primary Purpose | Council Assignment | Link |
| :--- | :--- | :--- | :--- |
| **code-architect** | Core software design patterns and system architecture mapping. | Architecture Council | [code-architect.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/code-architect.md) |
| **cloud-architect** | Designing and reviewing deployment architecture on public cloud platforms. | Architecture Council | [cloud-architect.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/cloud-architect.md) |
| **backend-architect** | Optimizing services, APIs, database integration, and performance. | Architecture Council | [backend-architect.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/backend-architect.md) |
| **ai-engineer** | Building LLM-powered applications, RAG pipelines, and vector databases. | Research Council | [ai-engineer.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/ai-engineer.md) |
| **prompt-engineer** | Prompt tuning, Chain-of-Thought setups, and output structural validations. | Research Council | [prompt-engineer.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/prompt-engineer.md) |
| **api-developer** | Building and documenting REST, gRPC, and GraphQL contracts. | Product Council | [api-developer.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/api-developer.md) |
| **frontend-developer** | UX implementation, modular web components, and responsive views. | Product Council | [frontend-developer.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/frontend-developer.md) |
| **nextjs-pro** | High-performance Next.js architectures and page routing systems. | Product Council | [nextjs-pro.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/nextjs-pro.md) |
| **python-pro** | PEP-compliant coding, async patterns, and package architecture. | Architecture Council | [python-pro.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/python-pro.md) |
| **typescript-pro** | Strictly-typed application code and package configurations. | Architecture Council | [typescript-pro.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/typescript-pro.md) |
| **database-expert** | Query auditing, migration designs, and indexing structures. | Architecture Council | [database-expert.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/database-expert.md) |
| **debugger** | Root-cause analysis, tracing bugs, and resolving stack dumps. | Research Council | [debugger.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/debugger.md) |
| **test-automator** | Writing unit, integration, and E2E test suites with mocks. | Product Council | [test-automator.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/test-automator.md) |
| **code-reviewer** | Automated pull request checking, security auditing, and formatting. | Architecture / Security | [code-reviewer.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/code-reviewer.md) |
| **observability-engineer**| Configuring OpenTelemetry bindings, trace collection, and logs. | Architecture Council | [observability-engineer.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/observability-engineer.md) |
| **sre-engineer** | System operations, reliability budgets, and recovery pipelines. | Security Council | [sre-engineer.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/sre-engineer.md) |
| **devops-incident-responder**| Real-time alerts triage, log analysis, and system failovers. | Security Council | [devops-incident-responder.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/devops-incident-responder.md) |
| **deployment-engineer** | CI/CD YAML configuration, container packaging, and GitOps deployments. | Product Council | [deployment-engineer.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/deployment-engineer.md) |
| **software-configuration-manager** | SCM baseline identification, change control, configuration auditing, and enterprise packaging. | Architecture / Security | [software-configuration-manager.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/software-configuration-manager.md) |
| **performance-optimizer**| CPU/memory optimization, service load benchmarks, and caching models. | Research Council | [performance-optimizer.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/performance-optimizer.md) |
| **design-system-engineer**| Token generation, Style Dictionary mapping, CSS primitives. | Product Council | [design-system-engineer.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/design-system-engineer.md) |
| **accessibility-expert** | WCAG 2.1 compliance audits, screen reader assets, and contrast. | Product Council | [accessibility-expert.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/accessibility-expert.md) |
| **product-manager** | Spec design, PRD reviews, features priority, and scoping. | Product Council (Lead) | [product-manager.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/product-manager.md) |
| **technical-writer** | C4 specification documents, API references, and user manuals. | Research Council | [technical-writer.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/technical-writer.md) |
| **documentation-expert**| Service catalogs (Backstage) and OpenAPI specification templates. | Research Council | [documentation-expert.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/agents/documentation-expert.md) |

---

# 4. Agent Memory Architecture Configuration

Each agent maintains a tiered memory model:
1. **Short-Term Memory**: Session variables, local state (handled via LangGraph state models).
2. **Long-Term Memory**: Declarative user facts and personal context (handled via Mem0).
3. **Temporal Graph Memory**: Networked event relationships (handled via Graphiti temporal schemas stored in Qdrant/Neo4j).
