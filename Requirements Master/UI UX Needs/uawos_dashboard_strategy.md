# Universal AI Workforce Operating System (UAWOS)
# Dashboard Strategy Specification (PHASE 6)

> **Workspace Context:** `rjmad1/UAWOS`  
> **Standards References:** UCA v1.0, WAAS v1.0, OPES v1.0, CIAS v1.0, GCF v1.0, PMCMS v1.0, VRMS v1.0, PRTCS v1.0, PVRS v1.0, RDMS v1.0

---

# 1. Dashboard Strategy Overview

## Dashboard Operating Model
UAWOS dashboards operate within a governed, objective-centric human + AI workforce operating model. Rather than serving as passive visualization screens, dashboards in UAWOS act as **operational control planes**. They are designed to show execution status and system compliance, mapping strategic intent directly to realized outcomes. 

Every signal displayed on a UAWOS dashboard must root back to an auditable objective and provide direct access to verifying evidence (e.g., git commits, OPA logs, or document transcripts).

---

## Dashboard Roles and Audience Mapping
*   **Executive Dashboard**: For Founders, CEOs, and CFOs. Focuses on portfolio ROI, managed value capacities, budget run-rates, and pending exceptions. (Monthly/weekly decision horizon).
*   **Product Dashboard**: For Product and Program Managers. Focuses on requirements ingestion readiness, completeness checklist critiques, plan simulation trade-offs, and roadmap timelines. (Daily decision horizon).
*   **Operations Dashboard**: For SREs and Operations Leaders. Focuses on system and service container status, component health scores, active blockers, and agent directory controls. (Real-time monitoring).
*   **Engineering Dashboard**: For developers and engineers. Focuses on active task DAG node progress, sandboxed tool confirmations, artifact compiler metrics, and HITL checklists. (Real-time task execution).
*   **Compliance Dashboard**: For Compliance and Security Officers. Focuses on OPA policy evaluations, OpenFGA relationship audits, exception waiver queues, and OpenLineage Marquez traces. (Audit and compliance horizon).

---

## Information Hierarchy Principles
1.  **Objective as Root**: All dashboards arrange their visual hierarchy starting with the Objective. Tasks and raw logs are nested sub-views.
2.  **Telemetry Priority**: Real-time system health, active blocker alerts, and loop warnings occupy top visual regions.
3.  **Governance Transparency**: OPA compile blocks, FGA lock status, and signature validations are permanently visible on action-sensitive controls.
4.  **Signal-to-Evidence Drill-down**: Clickable metric cards must immediately disclose provenance panels or evidence drawers.

---

## Real-Time vs Snapshot Strategy
*   **Real-Time Polling (Verified)**: The Operations Dashboard polls system component status and container states every 5 seconds (`GET /api/status`).
*   **Recommended Real-Time Streaming**: We recommend implementing Server-Sent Events (SSE) `/api/status/stream` for active agent execution monitoring, updating node states in the LangGraph DAG visualizer in real-time.
*   **Snapshot Cache (Inferred)**: Executive ROI ledgers, maturity models, and historical postmortems load snapshot databases on page mount to reduce network load.

---

## Dashboard Gaps or Unknowns
*   **Cross-Tenant Analytics**: Multi-tenant metrics and billing dashboards are undocumented in the current codebase.

---

# 2. Executive Dashboard

## Purpose
Provides executives and founders with portfolio-level economic oversight, actual vs. target ROI, and pending override gates.

## Primary Users
Executive / Founder (CEO/COO/CFO).

## KPI Hierarchy
1.  **Realized Portfolio Value ($)** (Primary success metric).
2.  **Portfolio ROI (%)** (Realized value vs. cumulative token/compute spent).
3.  **Active Objective Success Rate (%)** (Completed vs. failed/cancelled objectives).
4.  **Portfolio Budget Run-rate Variance ($)** (Actual spent vs. forecast model curves).

## Information Density Strategy
*   **Low-Density, High-Aspect Presentation**: Uses clean typography, large progress rings, and summary tables. Progressive disclosure slide-overs reveal detail logs.

## Widget Definitions

### 1. Portfolio Value Ring
*   **Verification Status**: Verified.
*   **Purpose**: Displays realized value compared to the original portfolio capacity hypothesis.
*   **Metric / Signal**: Managed Value Capacity ($) vs. Realized Value ($).
*   **Visual Pattern**: Concentric SVG progress ring with Outfit display typography.
*   **Interaction**: Click ring to open Portfolio details slide-over.
*   **Drill-Down Destination**: Portfolio Details panel.
*   **Governance Sensitivity**: Read-only.

### 2. ROI Variance Curve
*   **Verification Status**: Verified.
*   **Purpose**: Plots cumulative actual spent against forecasted budgets.
*   **Metric / Signal**: Cumulative actual spend ($) vs. simulated forecast spend ($).
*   **Visual Pattern**: Multi-line trend chart.
*   **Interaction**: Hover curve to inspect point date; click to isolate objectives.
*   **Drill-Down Destination**: Objective Budget Ledger view.
*   **Governance Sensitivity**: Alerts on $>20\%$ variance.

### 3. Pending Waiver Queue
*   **Verification Status**: Verified.
*   **Purpose**: Lists active exception requests (EXC-xxx) awaiting signature.
*   **Metric / Signal**: Pending exception counts, requesting agent ID.
*   **Visual Pattern**: High-density list table with HSL status badges.
*   **Interaction**: Clicking row opens approval modal.
*   **Drill-Down Destination**: Exception Approval View modal.
*   **Governance Sensitivity**: High; requires signature override token (SoD rule).

---

## Drill-Down Architecture
Clicking a portfolio row traverses downstream: `Portfolio Details` $\rightarrow$ `Objective Outcomes` $\rightarrow$ `Metric Formulas` $\rightarrow$ `Evidence Logs`.

## Filters and Slicing
*   Slice by **Strategic Theme**, **Quarterly Milestone**, and **Active Portfolio Scope**.

## Alerts and Notifications
*   Renders red banner on **Budget Limit Breached** or **Un-mitigated Compliance Risk**.

## Real-Time Indicators
*   Pulsing indicator maps budget variance state (Green: normal, Red: warning variance $>20\%$).

## Governance and Trust Requirements
All value metrics and ROI data must contain evidence trace indicators linking directly to Marquez lineage log indices.

---

# 3. Product Dashboard

## Purpose
Supports requirement studio ingestion processes, plan selections, and roadmap sequencing.

## Primary Users
Product Manager / Program Manager.

## KPI Hierarchy
1.  **Requirements Ingestion Completeness (%)** (Ingested metrics check).
2.  **Requirements Ingestion Readiness (%)** (Strategic alignment check).
3.  **Planning Forecast Accuracy (%)** (Simulated cost/duration vs. actual execution).
4.  **Milestone Sequence Health (%)** (Cycle conflict status).

## Workspace Density Strategy
*   **High-Density Workspace**: Renders input forms, checklists, and plan grids in a split-screen view.

## Widget Definitions

### 1. Critique Checklist
*   **Verification Status**: Verified.
*   **Purpose**: Displays requirement critiques and clarifying questions.
*   **Metric / Signal**: Checklist complete count, missing success metrics.
*   **Visual Pattern**: Collapsible accordion checklist with checkbox items.
*   **Interaction**: Checking item updates completeness score.
*   **Drill-Down Destination**: Ingestion Studio text editor.
*   **Governance / Trust**: Enforces Constitutional Law 1.

### 2. Plan Simulation Selector
*   **Verification Status**: Verified.
*   **Purpose**: Compares plan candidates generated by the Planner Agent.
*   **Metric / Signal**: Cost forecast, duration forecast, success probability.
*   **Visual Pattern**: Side-by-side card grid with highlight status indicators.
*   **Interaction**: Click card to inspect Monte Carlo distribution chart.
*   **Drill-Down Destination**: Simulation Center details panel.
*   **Governance / Trust**: OPA checks cost bounds.

### 3. Interactive Roadmap milestones
*   **Verification Status**: Verified.
*   **Purpose**: Tracks objective timeline milestones.
*   **Metric / Signal**: Start/end dates, milestone IDs (`RD-01` to `RD-04`).
*   **Visual Pattern**: Horizontal Gantt-style timeline grid.
*   **Interaction**: Drag-and-drop bars to re-sequence.
*   **Drill-Down Destination**: Objective Management details panel.
*   **Governance / Trust**: DFS cycle check blocks invalid timelines.

---

## Drill-Down Architecture
Double-clicking a Gantt bar traverses: `Objective Details` $\rightarrow$ `Plan Candidate Card` $\rightarrow$ `Simulation Run logs`.

## Filters and Slicing
*   Filters by **Objective Priority** (Critical, High, Medium, Low) and **Milestone Track**.

## Alerts
*   Warning cards highlight **Circular Dependency Conflicts** and **Vague Requirement Warnings**.

## Real-Time Indicators
*   Progress bar renders active Monte Carlo run states.

## Governance and Trust Requirements
Requirement Studio enforces masked PII views; DTASE critiques must check validation rules.

---

# 4. Operations Dashboard

## Purpose
Command Center dashboard for real-time service monitoring, container health, and agent loops.

## Primary Users
Operations Leader / SRE.

## KPI Hierarchy
1.  **strict health score (%)** (Core service container health indicator).
2.  **Core Service Component Status** (Postgres, OPA, Ollama, Qdrant ports).
3.  **Active Blocker count** (Incident warnings, GPLv3 risks).
4.  **Agent Trust Score Average** (Calculated registry status).

## Information Density Strategy
*   **Maximum Density Control Grid**: Compact layout fitting health rings, container list tables, and live alarm timelines on a single monitor layout.

## Widget Definitions

### 1. health circular ring
*   **Verification Status**: Verified.
*   **Purpose**: Real-time display of strict health vs. weighted health score.
*   **Metric / Signal**: strict health score (%).
*   **Visual Pattern**: SVG circular progress ring with centered text and pulsing live dot.
*   **Interaction**: Click ring to trigger compliance audit.
*   **Drill-Down Destination**: System Status Terminal.
*   **Governance / Trust**: Updates via `/api/status` polling.

### 2. Component Status Table
*   **Verification Status**: Verified.
*   **Purpose**: Displays status of Docker containers and REST APIs.
*   **Metric / Signal**: Engine status, severity, dependency, current issue.
*   **Visual Pattern**: Compact table with HSL status badges.
*   **Interaction**: Click row to open container diagnostics panel.
*   **Drill-Down Destination**: Interactive C4 Topology Viewer.
*   **Governance / Trust**: Verifies sandbox isolation boundaries.

### 3. Agent registry cards
*   **Verification Status**: Verified.
*   **Purpose**: Directory of active agents, trust scores, and manual overrides.
*   **Metric / Signal**: Trust score, autonomy profile, status.
*   **Visual Pattern**: Card grid with trust meters and Kill Switch button.
*   **Interaction**: Hover trust score to view history; click Kill Switch to suspend.
*   **Drill-Down Destination**: Agent Details panel.
*   **Governance / Trust**: Suspends agent if trust score drops below 70.

---

## Drill-Down Architecture
Clicking a component status row navigates directly to the node log console in the C4 Topology Viewer.

## Filters and Slicing
*   Filters by **Agent Class** (Planner, Executor, Reviewer) and **Health State** (Green, Yellow, Red).

## Alerts and Notifications
*   Flashing banner triggers on **License Compliance Risks** (GPLv3) and **Database Locks**.

## Real-Time Indicators
*   Pulsing green live dot indicates connection to `GET /api/status` daemon loop.

## Governance and Trust Requirements
Kill Switch overrides require SRE role validation; agent suspension events are logged to the immutable ledger.

---

# 5. Engineering Dashboard

## Purpose
Provides developers with task execution workspaces, sandboxed terminals, and artifact QA metrics.

## Primary Users
Engineer / Developer.

## KPI Hierarchy
1.  **Task Success Rate (%)** (Completed vs. failed actions).
2.  **Artifact QA Pass Rate (%)** (Semgrep/Gitleaks verification status).
3.  **HITL Approvals Queue count** (Pending tool execution reviews).
4.  **Token spent vs. Progress variance** (Cost efficiency tracking).

## Information Density Strategy
*   **Console-Optimized Split Layout**: Integrates a monospace code editor, split code diff reader, and sandboxed console panel.

## Widget Definitions

### 1. Sandboxed CLI Terminal
*   **Verification Status**: Inferred.
*   **Purpose**: Monospace console displaying Executor Agent tool operations.
*   **Metric / Signal**: Terminal output logs, OPA parameters check logs.
*   **Visual Pattern**: High-contrast monospace code panel.
*   **Interaction**: Command line input.
*   **Drill-Down Destination**: Marquez Lineage logs.
*   **Governance / Trust**: Mandatory OPA pre-checks on tool calls.

### 2. HITL Approval Panel
*   **Verification Status**: Verified.
*   **Purpose**: Validates tool calls before execution.
*   **Metric / Signal**: Executing command parameters, code diff.
*   **Visual Pattern**: Split comparison card with "Authorize" button.
*   **Interaction**: Click Authorize to execute sandboxed tool.
*   **Drill-Down Destination**: Delivery Traceability matrix.
*   **Governance / Trust**: Separation of duties guard.

### 3. Artifact Verification Checklist
*   **Verification Status**: Verified.
*   **Purpose**: Runs security and license checks on code deliverables.
*   **Metric / Signal**: Semgrep status, Gitleaks status, license validation.
*   **Visual Pattern**: Checklist with checkmark status tags.
*   **Interaction**: Click item to view code scan details.
*   **Drill-Down Destination**: QA scan reports drawer.
*   **Governance / Trust**: Enforces Law 11.

---

## Drill-Down Architecture
Clicking a task code commit in the traceability board opens the Marquez Lineage drawer.

## Filters and Slicing
*   Filters by **Task Status** (Pending, Running, Blocked, Completed).

## Alerts and Notifications
*   Renders warning card when **High-Risk Tool Executions** require manual validation.

## Real-Time Indicators
*   Spinner displays active compiler runs.

## Governance and Trust Requirements
All code synthesized by the Executor Agent must undergo developer review before repository commits.

---

# 6. Compliance Dashboard

## Purpose
Enables compliance officers to inspect OPA status, evaluate relationship tuples, and trace lineage.

## Primary Users
Governance / Compliance Officer.

## KPI Hierarchy
1.  **Policy Compliance Rate (%)** (Approved vs. rejected checks ratio).
2.  **OPA Response Latency (ms)** (Check speed evaluation).
3.  **Active Exceptions Waiver count** (Pending waivers).
4.  **Vulnerability Scan Status** (Syft/Trivy scanner checks).

## Information Density Strategy
*   **Tree & Ledger Split Layout**: Left folder trees map policy registries; right consoles display Marquez lineage flows.

## Widget Definitions

### 1. OPA Policy Registry Tree
*   **Verification Status**: Verified.
*   **Purpose**: Directory of Rego policy rules.
*   **Metric / Signal**: Policy ID, compilation check status.
*   **Visual Pattern**: Collapsible nested list folder structure.
*   **Interaction**: Selecting node opens Rego code editor.
*   **Drill-Down Destination**: Rego Policy Editor.
*   **Governance / Trust**: Enforces Principles 3.

### 2. OpenLineage Marquez visualizer
*   **Verification Status**: Verified.
*   **Purpose**: Traces data flow and artifact provenance.
*   **Metric / Signal**: Data inputs, compile nodes, artifact outputs.
*   **Visual Pattern**: Flowchart canvas with link-node mapping.
*   **Interaction**: Clicking node displays JSON OpenLineage metadata drawer.
*   **Drill-Down Destination**: Marquez Lineage Logs.
*   **Governance / Trust**: Enforces Law 7.

### 3. OpenFGA Tuple Diagram
*   **Verification Status**: Verified.
*   **Purpose**: Displays relationship access boundaries.
*   **Metric / Signal**: User mappings, role scopes, tool permissions.
*   **Visual Pattern**: Node-link canvas.
*   **Interaction**: Click node to audit relationships.
*   **Drill-Down Destination**: Role Mapping Registry.
*   **Governance / Trust**: Enforces CIAS standard.

---

## Drill-Down Architecture
Selecting an exception ID in the waivers table opens the Exception approvals details modal.

## Filters and Slicing
*   Filters by **Policy Severity** (High, Medium, Low) and **Compliance Status** (Approved, Blocked).

## Alerts and Notifications
*   Alert cards highlight **Active policy conflicts** and **Un-audited access tuple overrides**.

## Real-Time Indicators
*   Status badges update during OPA compiler rule additions.

## Governance and Trust Requirements
Access to the OPA Rego Editor requires dual authentication signatures (Executive + Compliance).

---

# 7. Shared Dashboard Patterns

## Widget Taxonomy
*   **KPI Widgets**: Outfit typography, concentric circular SVG progress rings.
*   **Status Badges**: HSL status pills mapping Green, Yellow, Red, Grey states.
*   **Ledger Tables**: High-density compact data rows.
*   **Evidence Drawers**: Slide-over panels displaying Marquez JSON logs and ROI formulas.
*   **Active Blocker Cards**: Red HSL border cards flashing on critical system failure.

---

## Cross-Dashboard Filters
*   Shared filters map across all active dashboards: **Portfolio ID**, **Objective ID**, **Milestone Track**, **Severity level**.

---

## Alerting Model
*   **Passive Alerts**: In-card badges, status pills, or tooltips for low-priority alerts.
*   **Interruptive Alarms**: Flashing red banners, modal overlays, or active blocker cards for critical blocks (e.g., GPLv3 license warnings).

---

## Explainability Surfaces
*   **"Why Blocked"**: Monospace OPA Rego rule display inside blocked action cards.
*   **"Why this Plan"**: Challenger Agent contrarian reports displayed inside candidate cards.
*   **"Why Trust Dropped"**: Performance metrics and success rate charts inside suspended agent cards.

---

## Empty, Error, Stale, and Degraded-State Rules
*   **Empty State**: Illustrative card showing clear checkmark states ("No active exceptions pending").
*   **Error State**: Red banner with connection status and reconnect triggers.
*   **Stale Data**: Grey-scale indicators indicating metric latency $>1$ minute.
*   **Degraded State**: Grey badges for offline components; continue loading cached snapshots.

---

## Accessibility Rules for Dashboards
*   Visual KPI progress rings must accompany text-equivalent labels.
*   Keyboard navigation traversals follow a logical top-to-bottom, left-to-right tab order.
*   Contrast levels meet $4.5:1$ requirements across light/dark themes.

---

# 8. Validation Review

## UX Review
*   *Strongly Supported*: High-density dashboard widgets, circular health progress rings, and active blocker cards are verified.
*   *Design Decisions Needed*: Custom icon libraries for specific agent classifications.
*   *Clarification Required*: Visual presentation rules for displaying plan critiques.

## Accessibility Review
*   *Strongly Supported*: HSL status pills and contrast requirements are verified.
*   *Design Decisions Needed*: Screen-reader traversals on node-link diagrams.
*   *Clarification Required*: Text alternatives for dynamic node relationships.

## Governance Review
*   *Strongly Supported*: Separation of duties checks, OPA policy block alerts, and audit ledger integrations are verified.
*   *Design Decisions Needed*: Visual builders for OPA policies to avoid writing raw Rego text.
*   *Clarification Required*: Default policy templates for enterprise compliance.

## Scalability Review
*   *Strongly Supported*: Standalone SPA files served by lightweight routing prevent framework bottlenecks.
*   *Design Decisions Needed*: Telemetry polling throttle rules during network congestion.
*   *Clarification Required*: Storage bounds for postgres audit ledger tables.

## Implementation Readiness Review
*   *Strongly Supported*: BFF REST endpoints and docker network configurations are active.
*   *Design Decisions Needed*: Central tokens css file compilation pipeline.
*   *Clarification Required*: Latency constraints for local Ollama/TinyLlama text parsing gateway.

---

# 9. Assumptions
*   We assume that the client application communicates with the backend HTTP server over port 8099 with connection timeouts set to 30 seconds.
*   We assume that the user's browser is modern and supports ES6 module imports and CSS custom variables natively.
*   We assume that PII masking heuristics in the DTASE engine occur on the client or in a secure gateway before sending data to Ollama.
*   We assume that the PostgreSQL audit logs and Marquez lineage records are read-only and cannot be modified by any user role.
*   We assume the C4 topology viewer renders static configuration maps generated from the system’s Docker compose layout.
