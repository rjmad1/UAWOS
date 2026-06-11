# Universal AI Workforce Operating System (UAWOS)
# Comprehensive Discovery & Experience Strategy Report

## Executive Summary

The objective of discovery is not simply to understand the product, but to eliminate uncertainty before design and engineering decisions become expensive. UAWOS (Universal AI Workforce Operating System) is a governed, objective-centric execution fabric designed to serve as the control plane for the autonomous enterprise. This document synthesizes findings from a comprehensive codebase analysis (Round 1), structures stakeholder and user validation protocols (Rounds 2 & 3), and establishes the Experience Architecture (Round 4) required to guide premium, friction-free interface design.

---

## Phase 1 — Strategic Truth

### 1. Why does this product exist?
Enterprise software is highly fragmented. Organizations manage intent using disconnected systems (e.g., emails, project trackers, documents, and messaging), resulting in communication gaps, lost context, and lack of alignment between daily activities and high-level outcomes. 

Furthermore, as organizations adopt AI agents, they face **agent sprawl**—creating autonomous agents faster than they can govern, track, or operationalize them. UAWOS exists to provide a unified, governed, and objective-centric execution fabric where the **Objective** is the primary abstraction.

### 2. Who creates value?
Value is created by the collaborative execution of a unified human and AI workforce.
*   **Humans** establish strategic direction, define objectives, configure governance policies, and provide critical human-in-the-loop approvals.
*   **AI Agents** (planners, orchestrators, executors, reviewers, learners, and governors) ingest objectives, translate domains, generate plans, run simulations, perform actions, and log operational telemetry.

### 3. What outcomes define success?
*   **Objective Success Rate**: Percentage of defined objectives successfully completed.
*   **Value Realization Rate**: Actual business value delivered versus the original value hypothesis.
*   **Governance Compliance Rate**: Percentage of executions complying with OPA/Rego policies and licensing constraints.
*   **Total Cost of Ownership (TCO) Reduction**: Decreased human effort and optimized token/compute spend per objective.
*   **Planning and Forecast Accuracy**: High correlation between simulated plan costs/durations and actual execution metrics.

### 4. What constraints cannot be violated?
*   **Human Accountability**: Irreversible or external actions (such as committing code, spending funds above thresholds, or publishing public content) require explicit human approvals.
*   **Governance Supremacy**: Governance rules and policies supersede autonomous agent execution. Under no circumstances can governance controls be bypassed.
*   **License Compliance**: Strict copyleft restrictions apply. For example, GPLv3-licensed components (such as the `Marker` document-parsing engine) must remain isolated in sandboxed service containers and never be imported directly into the core IP repository.

---

## Phase 2 — User Reality

### 5. Who are the users?
*   **Primary Users**: Founders, Product Managers, Program Managers, Operations Leaders, and Knowledge Workers.
*   **Secondary Users**: Executive Leadership (CIO/COO/CTO), Enterprise Architects, Governance/Compliance Teams, and Customer Success Teams.

### 6. What are they trying to accomplish?
Users are "hiring" UAWOS to transform unstructured operational intent (e.g., meeting recordings, typed memos, PDF requirements) into structured, planned, and successfully executed outcomes without managing tasks, tickets, or integrations manually.

### 7. What prevents success today?
*   **High Coordination Overhead**: Teams waste time tracking status, scheduling syncs, and moving data between tools.
*   **Opaque AI Autonomy**: Lack of trust in AI agents due to a lack of explainability, leading to low adoption.
*   **Siloed Knowledge**: Critical context remains locked in personal files, emails, or chat logs, resulting in duplicate work and knowledge loss.

### 8. What moments create friction, abandonment, or support burden?
*   **Requirement Ambiguity**: Input objectives that are vague or lack measurable outcomes.
*   **Unexpected Cost Spikes**: Rapid token consumption by uncontrolled looping agents during complex planning/execution.
*   **Execution Failures**: Fragile API integrations that fail without clear recovery states, leaving users unsure of system status.

---

## Phase 3 — System Reality

### 9. How does the system actually work?
UAWOS works by separating responsibilities between a **Governance Control Plane** (handling policies, risk, approvals, and autonomy limits) and an **Execution Plane** (managing planning, orchestration, workflows, and resource allocation). 
1. Unstructured input (voice, text, images, APIs) is processed by the **Domain Translation & Artifact Synthesis Engine (DTASE)**.
2. Structured objectives are generated with priority, dependencies, ownership, and health scores.
3. The **Planning Engine** generates and ranks candidate execution paths.
4. The **Governance Engine** checks the chosen plan against active OPA/Rego policy rules.
5. Coordinated agents (Planner, Orchestrator, Executor) execute actions under human-in-the-loop oversight.
6. Execution telemetry is ingested into the **Knowledge Graph** via OpenLineage/Marquez.

### 10. What data exists?
*   **Objective Graph**: Captures objectives, sub-objectives, priorities, owner mappings, lifecycle states, and dependency links.
*   **Budget Ledger**: Tracks actual expenditures, token consumption, and model pricing (TinyLlama, Llama3, DeepSeek, Gemini).
*   **Policy Registry**: Stores declarative rules (OPA/Rego), exception registers, and audit logs.
*   **Knowledge Graph**: Connects domain ontologies, document metadata, and historical outcomes.

### 11. What integrations exist?
*   **Vector DB (Qdrant)**: Ingests memory vectors and semantic records.
*   **Lineage Ingestion (Marquez)**: Automatically tracks execution data flows and metadata.
*   **Declarative Policy Engine (OPA)**: Validates cost governance and licensing rules.
*   **Document Parser (Marker Service)**: Isolated REST service container wrapping GPLv3 libraries for PDF transcription.
*   **Model Gateway (LiteLLM/Ollama)**: Integrates local LLM instances (TinyLlama) for parsing and reasoning.

### 12. What technical constraints exist?
*   **Latency**: Local LLMs (running on CPU/GPU) create response-time bottlenecks.
*   **Context Windows**: Limited model context windows restrict the volume of historical knowledge injected into prompts.
*   **Single-Tenant Focus**: Currently optimized for single-tenant, local-first environments to ensure strict data privacy.

---

## Phase 4 — Experience Architecture

### 13. What journeys exist?
*   **Objective Ingestion Journey**: Transcribing a voice memo -> Parsing structure -> Reviewing domain opportunities/risks -> Publishing active objective.
*   **Plan Simulation Journey**: Reviewing alternative plans -> Inspecting cost/time forecasts -> Submitting budget approval requests.
*   **Governance Audit Journey**: Viewing OPA check results -> Reviewing exceptions -> Granting overrides.

### 14. What workflows exist?
*   **Conflict Resolution**: System identifies circular dependencies or priority mismatches and alerts the user to update the graph.
*   **Exception Handling**: Triggered when an agent requests access to a restricted tool or exceeds a budget threshold, placing execution on hold until human approval is received.

### 15. What information must users see?
*   **Objective Health**: Visual indicators (Green, Yellow, Red) representing execution status, conflict risk, and compliance.
*   **Value-to-Cost ROI**: Clear visualizations showing business value score mapped against actual token/compute cost.
*   **Traceability Chain**: Step-by-step breadcrumbs connecting original unstructured inputs to final execution artifacts and outcomes.

### 16. What states can every screen enter?
*   **Empty State**: Welcoming onboarding wizards, templates, and import triggers.
*   **Loading State**: Progressive skeletons showing active background planning/analysis.
*   **Error State**: Actionable explainers detailing failures, API timeouts, or policy breaches, complete with retry hooks.
*   **Execution/Success State**: High-fidelity, real-time status updates and telemetry feeds.

---

## Phase 5 — Operational Excellence

### 17. Accessibility
*   Interface elements must comply with WCAG 2.1 AA standards.
*   Contrast ratios on light/dark themes must meet 4.5:1 standards.
*   Keyboard navigation support is required for all objective tables and network graphs.

### 18. Security
*   Secret scanning using Gitleaks must run in CI pipelines.
*   Container vulnerability auditing using Trivy and dependency license checks using Dependency-Track SBOM analysis.
*   Sandboxed runtime environments for third-party tools (Falco/OpenHands).

### 19. Performance
*   Dashboard pages must load in under 1.5 seconds.
*   Heuristic fallback parsers must run synchronously in <100ms when LLMs are offline or timing out.

### 20. Scalability
*   Federated graph structure supports independent scaling of vector, relational, and graph databases.
*   Local-first deployment models easily migrate to AWS/Azure cloud runtimes.

---

## Questions Answerable From Codebase (Discovery Round 1)

### Architecture
*   **System Architecture**: Single-tenant, service-oriented control plane coordinating with localized worker agents.
*   **Frontend Framework**: HTML5 single-page dashboard apps (`uawos_dashboard.html`, `uawos_requirement_studio.html`, `uawos_delivery.html`, `uawos_architecture.html`) utilizing pure Vanilla CSS and custom ES6 JavaScript. The styling implements modern CSS custom properties, HSL color palettes, responsive flexbox/grid layouts, and light/dark theme systems.
*   **Backend Framework**: Pure Python HTTPServer utilizing `http.server.BaseHTTPRequestHandler` running on port 8099. No external web frameworks (e.g., FastAPI, Flask) are used for the main control server, making it lightweight and dependency-minimal.
*   **Deployment Model**: Orchestrated via `docker-compose.yml`, which deploys PostgreSQL (port 5435), Qdrant (port 6333), Marquez (port 5000), Superset (port 8088), Dependency-Track API (port 8081), OPA (port 8181), OpenFGA (port 8083), and a mock backend wrapper. LiteLLM serves as the local LLM gateway.
*   **Authentication Model**: Policy-based access controls using OpenFGA and Open Policy Agent (OPA). Authorization exception rules are coded in `uawos_governance.py`.

### Data
*   **Database Schema**: The system currently runs on a file-based state store (`uawos_*_state.json` files) for local MVP configuration. PostgreSQL (port 5435) provides transactional relational storage, and Neo4j/Qdrant handle graph and vector indexes respectively.
*   **Entity Relationships**: Mapped in `uawos_traceability.py`, linking PRD Functional Requirements (FR) to roadmap milestones (`RD-01` to `RD-04`) and epics. Portfolios are composed of Objectives, which depend on Outcomes, Plans, and Workflows.
*   **Validation Rules**: Implemented in `uawos_objective.py`. Includes priority validation (Critical, High, Medium, Low) and dependency verification. Cost validation in `uawos_budget.py` enforces Rego checks that evaluate actual cost against allocated budgets.
*   **Data Constraints**: Constitutional Law 1 in `uawos_objective.py` enforces that every objective must contain a measurable outcome, deducting 20 points from the health score if none exist.

### APIs
*   **Endpoints**:
    *   `GET /api/status`: System-wide health checks (Docker, containers, plugins, and ports).
    *   `GET /api/objective/list` & `/api/objective/conflicts`: Loads objectives and identifies cycle or priority conflicts.
    *   `POST /api/dtase/analyze`: Unstructured text processing.
    *   `POST /api/budget/action`: Records token usage (`record_tokens`) and budget adjustments (`adjust_budget`).
    *   `GET /api/traceability` & `/api/roadmap`: Returns matrices mapping requirements to implementation code.
    *   `POST /api/requirement/submit` & `/api/requirement/clarify`: Requirement Studio endpoints for input validation.
*   **Payload Structures**: JSON payloads (e.g., cost tracking: `{"action": "record_tokens", "agent": "Executor", "model": "tinyllama", "tokens_in": 1000, "tokens_out": 500}`).
*   **Error Responses**: Standard JSON response `{"error": "message"}` on exception.
*   **Rate Limits**: Governed by the underlying LiteLLM model provider endpoint configurations.

### Workflows
*   **Implemented Workflows**: 
    *   Objective intake parsing (unstructured text parsed by TinyLlama model via `/api/generate` Ollama gateway).
    *   Cost forecasting and budget variance evaluation (Linear daily run-rate projection).
    *   Cycle detection via Depth-First Search (DFS) for circular objective dependencies.
    *   Policy audit workflow in `uawos_governance.py` (Enforces Law 11: Action verification).
*   **Role-Based Permissions**: Evaluated via mock/draft methods in `uawos_governance.py`, utilizing exception models like `EXC-001`.
*   **Business Rules**: Direct import of copyleft packages (Marker) is forbidden in core packages; OPA budget limits block agent action if actual spent exceeds allocated cost.

### Technical Debt
*   **Local File State DB**: Storing application state in local JSON files (`uawos_budget_state.json`, etc.) introduces concurrent write risks. Moving database state logic directly to Postgres is needed.
*   **BaseHTTPRequestHandler Routing**: String matching in HTTP handlers (`do_GET`, `do_POST`) is error-prone. Migrating to FastAPI would clean up routing.
*   **Duplicate Parsing Logic**: Both `uawos_objective.py` and `uawos_dtase.py` run independent heuristic text parsing methods, leading to redundant code.

### UX Debt
*   **No Central Design System CSS**: Dashboard pages use ad-hoc vanilla CSS declarations rather than importing a shared tokens stylesheet, leading to minor color and layout inconsistencies.
*   **Lack of Validation Indicators**: Budget entry screens allow submitting negative or empty amounts, relying on python API errors instead of immediate client-side validation.
*   **Accessibility Failures**: Dynamic tables and visual node graphs lack Aria-labels, keyboard focus styles, and screen-reader support, causing WCAG violations.

---

## Questions Requiring Stakeholder Input (Discovery Round 2)

1.  **Business Outcomes & Success Metrics**: What specific business KPI (e.g., 20% faster product launches, 30% reduction in workflow errors) is leadership expecting this platform to solve in Year 1?
2.  **Product Prioritization**: What are the top three capabilities that define the absolute MVP minimum? (e.g., Objective Intake vs. Simulation Engines).
3.  **Governance & Compliance Policies**: Are there specific industry regulations (like HIPAA, GDPR, or SOC2) that must be hardcoded into OPA policy templates for Phase 1?
4.  **Autonomy Levels**: What is the acceptable threshold for autonomous agent spending before human approval is strictly required?
5.  **Integration Priorities**: Which legacy enterprise tools (e.g., Jira, Slack, Salesforce, GitLab) are high-priority integrations, and which can be deferred?

---

## Questions Requiring User Research (Discovery Round 3)

1.  **User Goals**: In your day-to-day workflow, what specific tasks (like status reporting, task assignment, writing requirements) consume the most time?
2.  **Productivity Bottlenecks**: How do you currently handle handoffs and resource conflicts when an objective starts slipping?
3.  **Mental Models**: How do you conceptualize the relationship between a high-level "Objective," a "Plan," and a "Workflow"?
4.  **Trust Mappings**: What information would you need to see on-screen to trust an AI agent to execute an action (like refactoring code or allocating budget) autonomously?
5.  **Accessibility Needs**: Are there keyboard navigation or screen reader requirements we must prioritize for operators using the dashboard?

---

## Discovery Gaps Identified

1.  **Organizational UX (Support Workflows)**: The PRDs do not specify the user experience for support teams who must troubleshoot failed agent loops.
2.  **AI-Specific UX (Confidence & Failure)**: Current UI mocks do not define how the system visualizes "low-confidence" translation results or prompt history.
3.  **Enterprise Governance (Tenancy & Permissions)**: No clear specification for multi-tenant isolation, department-level budgeting permissions, or inherited role access.
4.  **Experience Operations (Maintenance Alerting)**: Gaps exist in specifying the UX when an external tool integration (like Slack or GitHub) goes offline during execution.

---

## Recommended Next Steps (Synthesis Round 4)

### Round 1: AI Codebase Assessment (Completed)
*   Verified system status: Infrastructure is **70% operational** (Docker containers, DBs, and core Python modules are active).
*   Documented system models, API endpoints, and technical debt.

### Round 2: Stakeholder Validation
*   Present the stakeholder questions to product leadership.
*   Validate the MVP capability priority list and governance cost limits.

### Round 3: User Research Interview Loops
*   Run mock user interviews with Product and Operations leaders.
*   Establish journey maps and map JTBD (Jobs-to-be-done) friction points.

### Round 4: Experience Architecture Blueprint
*   **Experience Strategy**: Define the voice-first/chat-native input strategy and human-in-the-loop validation checkpoints.
*   **Service Blueprint**: Map front-stage interactions (user submitting objective) to back-stage processes (DTASE, Planning, Governance evaluation, agent loops).
*   **Information Architecture**: Structure the primary navigation objects (Objective Graph, Budget ledgers, Policy catalogs).
*   **Task Flows**: Build visual flows for conflict resolution, exceptions, and budget approvals.
*   **Screen Inventory & Wireframe Specs**: Define specifications for the Conversation Workspace, Objective Dashboard, Execution Workspace, Governance controls, and Value dashboards.
*   **Design-System CSS Foundation**: Standardize layout tokens, typography, and light/dark mode variables.
*   **Risk Registers**: Document both UX/CX risks (e.g., trust failure, abandonment) and technical risks (latency, model hallucinations).
*   **Readiness Assessment**: Establish criteria to determine when backend engines are mature enough to unlock wireframing.
