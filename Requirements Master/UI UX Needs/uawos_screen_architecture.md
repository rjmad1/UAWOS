# Universal AI Workforce Operating System (UAWOS)
# Screen Architecture Specification (PHASE 5)

> **Workspace Context:** `rjmad1/UAWOS`  
> **Standards References:** UCA v1.0, WAAS v1.0, OPES v1.0, CIAS v1.0, GCF v1.0, PMCMS v1.0, VRMS v1.0, PRTCS v1.0, PVRS v1.0, RDMS v1.0

---

# 1. Screen Architecture Overview

## Screen Inventory Method
Screens within UAWOS are identified and categorized from the repository's frontend directory structure (`apps/web/`), the system daemon routing configurations in `apps/api/main.py`, and the workflows, dashboard requirements, and role-mapping protocols documented in the core standards. 

The division of screen layouts comprises:
*   **Primary Workspaces**: Ingestion Studio, Task Workspace. (High interactivity, split-screen, density-mutable).
*   **Dashboards**: Operational Command Center, Portfolio Value Dashboard, Governance Console. (Aggregated data display, telemetry polling, status rings).
*   **Detail Views / Slide-Overs**: Evidence Drawer, Marquez Lineage Explorer. (Progressive disclosure, read-only monospace logs).
*   **Administrative / Configuration Panels**: Rego Policy Editor, Role Mapping Registry, Token Authenticator. (Form-heavy configurations, verification indicators).

---

## Verified Application Areas
*   **Operational Command Center (`uawos_dashboard.html`)**: Circular health meters, container component lists, active blocker cards, and telemetry indicators.
*   **Requirement Ingestion Studio (`uawos_requirement_studio.html`)**: PRD Paste panel, critique checklists, and candidate plan comparisons.
*   **Timeline & Roadmaps (`uawos_roadmap.html`)**: Milestone timelines (`RD-01` to `RD-04`) and dependency re-sequencing tracks.
*   **Delivery Traceability (`uawos_delivery.html`)**: Traceability tables mapping functional requirements to code artifacts.
*   **C4 Topology Viewer (`uawos_architecture.html`)**: Interactive Neo4j-style component topology canvas.

---

## Inferred Application Areas
*   **Portfolio Value & Ledger Dashboard**: Implied by the PVRS and PSCB value realization requirements and executive buyer personas.
*   **Governance Exception & Waiver Queue**: Implied by the PRTCS exception models (EXC-xxx) and the Separation of Duties workflows.
*   **Agent Directory & Registry**: Implied by the WAAS agent management rules and trust score tracking.
*   **Rego Policy Editor & Compiler**: Implied by the PRTCS OPA integration requirements.
*   **Role Mapping Registry (OpenFGA)**: Implied by the CIAS relationship mapping and access control rules.
*   **Knowledge Graph Explorer**: Implied by the KMLS vector search and provenance requirements.
*   **Postmortem Review Board**: Implied by the PMCMS organizational learning requirements.

---

## Screen Architecture Gaps or Unknowns
*   **Multi-tenant workspace isolations**: The exact UI representation for switching tenant boundaries is undocumented.
*   **Agent Council consensus visualization**: Screens displaying multi-agent consensus scoring or strategic voting loops are not defined in the source.

---

# 2. Screen Inventory

## Executive Surfaces
1.  **Portfolio Value & Ledger Dashboard** (Inferred | Primary Persona: Executive / CFO | Trigger: Navigating to Portfolio tab | Core objects: Portfolios, Budgets, Realized ROI | Governance: Budget threshold adjustments).
2.  **Governance Exception & Waiver Queue** (Inferred | Primary Persona: Executive / CEO | Trigger: Push alert or Exception tab click | Core objects: Exception Request EXC-xxx, OPA policies | Governance: Separation of duties override sign-off).

## Product and Planning Surfaces
3.  **Requirement Ingestion Studio** (Verified | Primary Persona: Product Manager | Trigger: Default load of `uawos_requirement_studio.html` | Core objects: PRD, Ingestion Checklist | Governance: Constitutional Law 1 measurability check).
4.  **Planning & Simulation Studio** (Verified | Primary Persona: Product Manager | Trigger: Successful critique of ingestion candidate | Core objects: Plans, Simulations | Governance: Evaluates plan cost boundaries).
5.  **Interactive Roadmap Timeline** (Verified | Primary Persona: Product Manager | Trigger: Load of `uawos_roadmap.html` | Core objects: Timestones, Objectives | Governance: Blocks re-sequencing of OPA blocked objectives).

## Operations Surfaces
6.  **Operational Command Center** (Verified | Primary Persona: Operations Leader / SRE | Trigger: Default load of `uawos_dashboard.html` | Core objects: strict health rings, component states | Governance: System status polling and agent loop monitoring).
7.  **Agent Directory & Registry** (Inferred | Primary Persona: Operations Leader / SRE | Trigger: Agent tab click | Core objects: Agent profiles, Trust Scores | Governance: Decommission / Kill Switch overrides).
8.  **Interactive C4 Topology Viewer** (Verified | Primary Persona: Operations Leader / SRE | Trigger: Load of `uawos_architecture.html` | Core objects: Component nodes, Docker container mappings | Governance: Visual verification of Marker service sandbox isolation).

## Engineering Surfaces
9.  **Delivery Traceability Board** (Verified | Primary Persona: Engineer / Developer | Trigger: Load of `uawos_delivery.html` | Core objects: Tasks, Artifacts | Governance: Enforces Law 11 Action verification).
10. **Task Execution Workspace** (Inferred | Primary Persona: Engineer / Developer | Trigger: Clicking active task card | Core objects: Code artifacts, sandboxed tools | Governance: Mandatory OPA pre-checks on tool calls).

## Governance and Compliance Surfaces
11. **Rego Policy Editor** (Inferred | Primary Persona: Compliance Officer | Trigger: Policy tab click | Core objects: Rego rules | Governance: Compiles declarative constraints).
12. **OpenLineage Marquez Explorer** (Inferred | Primary Persona: Compliance Officer | Trigger: Clicking lineage trace links | Core objects: Lineage trees | Governance: Enforces Law 7 Decision Traceability).

## Security and Administration Surfaces
13. **Role Mapping Registry** (Inferred | Primary Persona: SRE | Trigger: Settings tab click | Core objects: OpenFGA tuples | Governance: Access boundary configurations).
14. **Token Authenticator Panel** (Verified | Primary Persona: All Users | Trigger: Token refresh warning or Profile click | Core objects: JWT authorization header | Governance: Enforces CIAS authentication).

## Knowledge and Intelligence Surfaces
15. **Knowledge Graph Explorer** (Inferred | Primary Persona: PM / Compliance | Trigger: Knowledge tab search | Core objects: Claims, Evidence | Governance: Enforces Law 9 Provenance verification).

---

# 3. Detailed Screen Specifications

## 1. Portfolio Value & Ledger Dashboard (Inferred)
*   **Purpose**: Renders realized business ROI and budget run-rates across portfolios.
*   **Primary Persona**: Executive (CEO/CFO).
*   **Layout Blueprint**: 3-row layout: Top KPI stats block $\rightarrow$ Middle cost vs. progress graph $\rightarrow$ Bottom ledger table.
*   **Primary Sections**:
    *   *KPI Bar*: Displays Portfolio Value Capacity, Cumulative Spent, Target vs. Realized ROI.
    *   *Cost Variance Graph*: Scatter plot mapping simulated forecasts against actual spent tokens.
    *   *Ledger Table*: Rows displaying Portfolio Objectives, current state, and value scores.
*   **Core Components**: circular progress rings, scatter chart, dense data table.
*   **Key Data Displayed**: Portfolio ID, budget spent ($), realized ROI ($), variance score.
*   **Primary User Actions**: Adjust portfolio budget bounds, drill down to objective outcomes.
*   **System Responses**: Updates ledger metrics, checks FGA role scopes.
*   **Governance Touchpoints**: Restricts limit modifications to CEO role.
*   **Explainability Surfaces**: Clicking realized ROI opens Evidence Drawer displaying calculation formula.
*   **Auditability**: Read-only ledger data synchronized with `log_audit` PostgreSQL records.
*   **Risks if Failed**: Opaque budget data leads to undetected token spending loops.

---

## 2. Governance Exception & Waiver Queue (Inferred)
*   **Purpose**: Manages pending exception requests (EXC-xxx) and risk acceptances.
*   **Primary Persona**: Executive (CEO/CPO).
*   **Layout Blueprint**: Split view: Left pane displays waiver list $\rightarrow$ Right panel renders active waiver detail and override signature controls.
*   **Primary Sections**:
    *   *Waiver List*: Vertical list of pending and expired exception requests.
    *   *Waiver Details*: Displays requestor ID, violated Rego policy code block, and justification.
    *   *Signature Panel*: Secure token input form and justification checkbox.
*   **Core Components**: list group, monospace code reader, secure input form, primary override button.
*   **Key Data Displayed**: Exception ID, target policy, requesting agent, justification string, expiration date.
*   **Primary User Actions**: Authorize override waiver, reject exception, input signature.
*   **System Responses**: Writes signed token to postgres, updates OpenFGA relationship tuple, resumes workflow.
*   **Governance Touchpoints**: Enforces SoD (requestor ID != approver ID).
*   **Explainability Surfaces**: Displays Challenger agent risk assessment report.
*   **Auditability**: Generates immutable audit logs on signature submission.
*   **Risks if Failed**: Stalled execution DAGs due to manual signoff latency.

---

## 3. Requirement Ingestion Studio (Verified)
*   **Purpose**: Ingests unstructured inputs, masks PII, and runs critiques.
*   **Primary Persona**: Product Manager.
*   **Layout Blueprint**: Split screen: Left input pane $\rightarrow$ Right workspace tabs (Critique, Proposition, Roadmap).
*   **Primary Sections**:
    *   *Input Pane*: Drag-and-drop file upload and free-text description text areas.
    *   *Critique Checklist*: Vertical list of completeness checks (Problem Statement, Scope, Metrics).
    *   *Proposition Board*: Candidate requirement list with confidence scores.
*   **Core Components**: File uploader, text editor area, completeness meters, checklist accordion.
*   **Key Data Displayed**: Ingestion status, completeness score (%), readiness score (%), PII warnings.
*   **Primary User Actions**: Upload PRD PDF, submit text for critique, answer clarifying questions.
*   **System Responses**: Invokes DTASE, runs Marker parser, generates check checklists, updates status rings.
*   **Governance Touchpoints**: Masking PII before LLM calls; enforces Constitutional Law 1.
*   **Explainability Surfaces**: Displays critique checklists showing missing success metrics.
*   **Auditability**: Ingestion events and source hashes logged.
*   **Risks if Failed**: CPU timeouts on large PDFs lock user interface.

---

## 4. Planning & Simulation Studio (Verified)
*   **Purpose**: Generates, simulates, and compares candidate plan paths.
*   **Primary Persona**: Product Manager.
*   **Layout Blueprint**: Card grid comparison view with split-screen sidebar showing forecast detail.
*   **Primary Sections**:
    *   *Plan Grid*: Side-by-side comparative plan cards displaying duration and cost forecasts.
    *   *Forecast Details*: Monte Carlo probability distributions and duration variance curves.
    *   *Constraint Settings*: Inputs for cost ceilings and target duration limits.
*   **Core Components**: card group, probability distribution scatter plot, number sliders.
*   **Key Data Displayed**: Success probability (%), forecast duration (days), forecast cost ($), risk score.
*   **Primary User Actions**: Run Monte Carlo simulation, select plan candidate, authorize budget ceiling.
*   **System Responses**: Invokes Simulation Engine, evaluates plan cost against OPA budget rules, dispatches workflow.
*   **Governance Touchpoints**: Blocks plan selection if cost exceeds portfolio budget limits.
*   **Explainability Surfaces**: Challenger Agent contrarian reports explaining simulation risk variables.
*   **Auditability**: Commits chosen plan parameters to plan state.
*   **Risks if Failed**: PM dispatches plans with low success probabilities.

---

## 5. Interactive Roadmap Timeline (Verified)
*   **Purpose**: Visualizes objective dependency tracks and roadmap milestones.
*   **Primary Persona**: Product Manager.
*   **Layout Blueprint**: Full screen interactive horizontal track canvas.
*   **Primary Sections**:
    *   *Roadmap Track*: Horizontal milestone bars (RD-01 to RD-04) mapping objectives.
    *   *Dependency Panel*: Interactive links displaying blocked parent nodes.
    *   *Capacity Sidebar*: Displays agent/human resource allocation trends.
*   **Core Components**: interactive timeline track, SVG milestone nodes, allocation line chart.
*   **Key Data Displayed**: Milestone IDs, objective title, start/end dates, allocation percentage.
*   **Primary User Actions**: Drag-and-drop to re-sequence timeline, resolve dependency conflict.
*   **System Responses**: Executes DFS cycle check, highlights conflicts on timelines, saves roadmap state.
*   **Governance Touchpoints**: Blocks timeline rescheduling of OPA blocked objectives.
*   **Explainability Surfaces**: Displays re-planning recommendations.
*   **Auditability**: Timeline modifications logged.
*   **Risks if Failed**: Undetected circular dependencies brick planning state.

---

## 6. Operational Command Center (Verified)
*   **Purpose**: Real-time system monitoring and container health checks.
*   **Primary Persona**: Operations Leader / SRE.
*   **Layout Blueprint**: 3-column dashboard: Left health rings $\rightarrow$ Middle active blockers list $\rightarrow$ Right components grid.
*   **Primary Sections**:
    *   *Health Panel*: Displays strict vs. weighted health circular progress rings and live dot.
    *   *Active Blocker List*: Card list of system incidents and license compliance risks (GPLv3 alerts).
    *   *Component Grid*: Status grid of core containers (Postgres, OPA, Ollama, Qdrant).
*   **Core Components**: circular progress rings, pulsing live dot, alert cards, status badges.
*   **Key Data Displayed**: strict health score (%), active component counts, warning descriptions.
*   **Primary User Actions**: Execute Agent Kill Switch, trigger compliance audit.
*   **System Responses**: Suspends executor containers, polls status endpoints.
*   **Governance Touchpoints**: Blocks non-compliant agent actions immediately; handles loop alerts.
*   **Explainability Surfaces**: Active Blocker card highlights the exact copyleft package violating rules.
*   **Auditability**: Health status records and manual override events written to postgres.
*   **Risks if Failed**: Unchecked agent loops deplete budget before manual override is possible.

---

## 7. Agent Directory & Registry (Inferred)
*   **Purpose**: Manages AI agent profiles, trust scores, and runtime states.
*   **Primary Persona**: Operations Leader / SRE.
*   **Layout Blueprint**: Directory card grid layout with slide-over metric panel.
*   **Primary Sections**:
    *   *Agent Grid*: Cards displaying agent class, autonomy level, and status.
    *   *Metrics Panel*: Trust score history radar charts and token cost run-rates.
    *   *Controls*: Registration forms and manual override buttons.
*   **Core Components**: card grid, status badges, trust radar chart, manual suspension button.
*   **Key Data Displayed**: Agent ID, Agent Class, Trust Score (0.00-1.00), Autonomy Profile (L0-L4), Status.
*   **Primary User Actions**: Register agent, suspend running agent, adjust autonomy limits.
*   **System Responses**: Updates agent state, suspends active container, logs action.
*   **Governance Touchpoints**: Automatically suspends agents whose trust falls below 70.
*   **Explainability Surfaces**: Displays performance logs and execution success rates.
*   **Auditability**: Registry modifications logged.
*   **Risks if Failed**: Opaque agent profiles hide trust drift or loop risks.

---

## 8. Interactive C4 Topology Viewer (Verified)
*   **Purpose**: Renders visual system topologies and Docker engine runtimes.
*   **Primary Persona**: Operations Leader / SRE.
*   **Layout Blueprint**: Full screen interactive link-node canvas.
*   **Primary Sections**:
    *   *Topology Canvas*: Node-link diagram of server containers and APIs.
    *   *Diagnostic Console*: Monospace error logs and component latency readouts.
*   **Core Components**: interactive canvas, monospace log terminal.
*   **Key Data Displayed**: Component names, connection links, response latencies (ms).
*   **Primary User Actions**: Pan/zoom canvas, select node to inspect logs.
*   **System Responses**: Fetches status payload, renders terminal logs.
*   **Governance Touchpoints**: Verifies Marker parser isolation on port 8000.
*   **Explainability Surfaces**: Displays connection logs.
*   **Auditability**: Diagram state maps to actual docker configurations.
*   **Risks if Failed**: Hidden API failures go un-alerted.

---

## 9. Delivery Traceability Board (Verified)
*   **Purpose**: Maps functional requirements to roadmaps and code.
*   **Primary Persona**: Engineer / Developer.
*   **Layout Blueprint**: Multi-column matrix view with details sidebar.
*   **Primary Sections**:
    *   *Trace Matrix*: Rows mapping requirements to epics, tasks, and commits.
    *   *Verification Log*: Security scan logs and code build checklists.
*   **Core Components**: high-density data grid, verification checkbox list, status pills.
*   **Key Data Displayed**: Functional Requirement ID, Epic status, task verification verdict.
*   **Primary User Actions**: Trigger task verification scan, submit execution evidence.
*   **System Responses**: Executes verification scripts, validates output artifacts, logs evidence.
*   **Governance Touchpoints**: Enforces Law 11 (Action verification).
*   **Explainability Surfaces**: Clicking task opens code verification report.
*   **Auditability**: Generates immutable audit records for verification states.
*   **Risks if Failed**: Committing un-verified or non-compliant artifacts to main.

---

## 10. Task Execution Workspace (Inferred)
*   **Purpose**: Coordinates code/document synthesis and tool sandboxing.
*   **Primary Persona**: Engineer / Developer.
*   **Layout Blueprint**: Split pane: Left task specifications $\rightarrow$ Right sandboxed console and diff viewer.
*   **Primary Sections**:
    *   *Task Specs*: Displays goal, inputs, and allowed tool parameters.
    *   *Sandboxed Console*: Monospace terminal displaying executor operations.
    *   *Diff Viewer*: Code/document change comparisons with verification checks.
*   **Core Components**: monospace terminal, diff block, tool parameter input, authorize button.
*   **Key Data Displayed**: Task ID, allowed tools, console output, code diff.
*   **Primary User Actions**: Authorize tool execution (HITL), execute sandboxed command, log evidence.
*   **System Responses**: Queries OPA, runs sandboxed command, outputs console logs.
*   **Governance Touchpoints**: Mandatory OPA pre-checks on tool calls; Enforces Law 5.
*   **Explainability Surfaces**: Displays console execution trails and parameter inputs.
*   **Auditability**: Sandboxed command runs and approvals logged.
*   **Risks if Failed**: Sandbox execution bypasses OPA checks, risking code contamination.

---

## 11. Rego Policy Editor (Inferred)
*   **Purpose**: Authors, compiles, and deploys OPA Rego policies.
*   **Primary Persona**: Compliance Officer.
*   **Layout Blueprint**: 3-panel workspace: Left policy files list $\rightarrow$ Middle code editor $\rightarrow$ Right compiler checker.
*   **Primary Sections**:
    *   *Policy List*: Tree view of OPA policy registry files.
    *   *Code Editor*: Interactive text area with syntax highlighting for Rego code.
    *   *Compiler Pane*: Monospace display of compile errors and policy conflict warnings.
*   **Core Components**: folder tree, code text area, monospace diagnostic output.
*   **Key Data Displayed**: Policy ID, compilation status, conflict alerts.
*   **Primary User Actions**: Edit Rego rules, run compiler checks, publish policy.
*   **System Responses**: Validates syntax, verifies rule dependencies, deploys to OPA.
*   **Governance Touchpoints**: Highest governance authority; rules govern all execution.
*   **Explainability Surfaces**: Highlighted code lines show compiler warnings.
*   **Auditability**: Commits policy version modifications.
*   **Risks if Failed**: Invalid policies brick active execution pipelines.

---

## 12. OpenLineage Marquez Explorer (Inferred)
*   **Purpose**: Slide-over drawer displaying data provenance and lineages.
*   **Primary Persona**: Compliance Officer.
*   **Layout Blueprint**: Right-side slide-over panel.
*   **Primary Sections**:
    *   *Lineage Tree*: Visual DAG displaying data flow inputs and output artifacts.
    *   *Provenance Logs*: Detailed JSON display of OpenLineage metadata records.
*   **Core Components**: lineage canvas, monospace metadata panel.
*   **Key Data Displayed**: Lineage ID, compile times, data sources, output hashes.
*   **Primary User Actions**: Select node to inspect JSON metadata, print audit trace.
*   **System Responses**: Fetches Marquez API log, parses metadata.
*   **Governance Touchpoints**: Enforces Law 7 (Decision Traceability).
*   **Explainability Surfaces**: Node connections show complete data lineage.
*   **Auditability**: Renders read-only, immutable lineage records.
*   **Risks if Failed**: Inability to trace artifacts during compliance audits.

---

## 13. Role Mapping Registry (Inferred)
*   **Purpose**: Manages OpenFGA access tuples and role-based mappings.
*   **Primary Persona**: Operations Leader / SRE.
*   **Layout Blueprint**: Directory table layout with FGA node visualization.
*   **Primary Sections**:
    *   *User Table*: Lists users and assigned roles (CEO, Developer, Compliance).
    *   *Tuple Visualizer*: Node-link diagram showing FGA relationship trees.
*   **Core Components**: high-density user table, FGA canvas.
*   **Key Data Displayed**: User ID, assigned role, active permissions.
*   **Primary User Actions**: Bind role to user, audit relationship tuples.
*   **System Responses**: Calls OpenFGA APIs, commits tuple update.
*   **Governance Touchpoints**: Controls authorization boundaries.
*   **Explainability Surfaces**: Canvas diagrams explain permission access paths.
*   **Auditability**: Role modifications logged.
*   **Risks if Failed**: Static configurations hide access drift.

---

## 14. Token Authenticator Panel (Verified)
*   **Purpose**: Refreshes JWT authorization headers.
*   **Primary Persona**: All Users.
*   **Layout Blueprint**: Center modal layout.
*   **Primary Sections**:
    *   *Token Form*: Text inputs for refresh token keys.
    *   *Profile Settings*: Display active JWT scope, expiration duration, and roles.
*   **Core Components**: Secure text input, refresh button, timer widget.
*   **Key Data Displayed**: Expiration count down, token scopes, JWT signatures.
*   **Primary User Actions**: Submit refresh token key, sign out.
*   **System Responses**: Authenticates key, overrides authorization header, extends session.
*   **Governance Touchpoints**: Restricts scopes based on active FGA role mappings.
*   **Explainability Surfaces**: Displays token scopes.
*   **Auditability**: Session creations and authentication keys logged.
*   **Risks if Failed**: Expired sessions freeze active SRE dashboard monitoring.

---

## 15. Knowledge Graph Explorer (Inferred)
*   **Purpose**: Visualizes and searches semantic ontologies and document logs.
*   **Primary Persona**: Product Manager.
*   **Layout Blueprint**: 3-panel: Left semantic search input $\rightarrow$ Middle Neo4j graph canvas $\rightarrow$ Right details card.
*   **Primary Sections**:
    *   *Search Bar*: Input query panel executing vector searches.
    *   *Graph Canvas*: Interactive node-link diagram rendering Neo4j Cypher mappings.
    *   *Details Card*: Displays metadata, source provenance, and confidence tags.
*   **Core Components**: Query input, Neo4j interactive canvas, provenance details card.
*   **Key Data Displayed**: Knowledge Node ID, confidence score, source type.
*   **Primary User Actions**: Execute semantic search, select node, query Cypher.
*   **System Responses**: Queries Qdrant/Neo4j, updates canvas nodes.
*   **Governance Touchpoints**: Enforces Law 9 (No Knowledge without Provenance).
*   **Explainability Surfaces**: Provenance cards show original intake transcripts.
*   **Auditability**: Search records and knowledge ingestions logged.
*   **Risks if Failed**: Duplicate work occurs due to search latency.

---

# 4. State Architecture

## Loading States
*   **Trigger**: Triggered on page transition, PDF upload, or planning simulation execution.
*   **UI Communications**: Renders progressive skeleton layouts mapped to grid coordinates. Display status logs ("PII Masking...", "Running Monte Carlo...").
*   **User Action Options**: User can cancel operation, returning the UI to the previous active state.
*   **Governance / Audit Context**: Displays progress step indicators.
*   **Ambiguity Avoidance**: Spinners must include text descriptions; progress bars update in real-time.

---

## Empty States
*   **Trigger**: No exceptions pending, search returns zero nodes, or new workspaces onboarded.
*   **UI Communications**: Renders illustration cards with clear descriptions ("No active exceptions pending", "Waiver queue is clean").
*   **User Action Options**: Provide a clear primary action button ("Onboard Objective", "Create Policy", "Upload PRD").
*   **Governance / Audit Context**: Displays verify checkmark badges.
*   **Ambiguity Avoidance**: The empty card must clarify that the lack of data is normal (e.g., in exception dashboards).

---

## Error States
*   **Trigger**: DB timeout, container offline, or API error.
*   **UI Communications**: Displays orange/red alerts containing exact system failure message.
*   **User Action Options**: Clickable retry button, copy error log button, connection reset triggers.
*   **Governance / Audit Context**: Exposes component diagnostics (latency, ports).
*   **Ambiguity Avoidance**: Clarify the specific failure component (e.g., "Ollama service is unreachable").

---

## Success States
*   **Trigger**: Plan selection confirmed, exception override signed, or verification completed.
*   **UI Communications**: Displays green alert checkmarks with status messages ("Plan Dispatched Successfully", "Waiver EXC-001 Signed").
*   **User Action Options**: Primary link to next workflow step ("Go to Roadmap", "View Active DAG").
*   **Governance / Audit Context**: Displays signed approval hashes and transaction tokens.
*   **Ambiguity Avoidance**: Expose verification certificates.

---

## Access and Permission States
*   **Trigger**: User role does not possess permissions to edit inputs or click buttons.
*   **UI Communications**: Button elements are disabled; fields are marked read-only; lock icons display.
*   **User Action Options**: Hovering locks displays a tooltip link: "Request role override / waiver."
*   **Governance / Audit Context**: Displays FGA role mappings.
*   **Ambiguity Avoidance**: Avoid hiding elements completely; disabled elements clarify boundaries.

---

## Governance Block States
*   **Trigger**: Executor Agent tool call violates OPA, or actual spent exceeds budget limits.
*   **UI Communications**: Active workflow halts, DAG node outlines turn flashing Red, and a critical incident card renders.
*   **User Action Options**: "Request Exception Waiver" button, "Pause Workflow" option.
*   **Governance / Audit Context**: Monospace code panel displays violating OPA Rego rule code.
*   **Ambiguity Avoidance**: Display the exact budget spent vs. limit metrics that triggered the block.

---

## Partial Data and Degraded Mode States
*   **Trigger**: Marquez lineage server or Qdrant vector engine is offline, but primary PostgreSQL database is active.
*   **UI Communications**: Dashboard displays connection alert warning; telemetry status badges change to Grey ("Offline").
*   **User Action Options**: Data refresh button, continue using primary databases.
*   **Governance / Audit Context**: Highlights impacted modules (e.g., "Lineage mapping is currently degraded").
*   **Ambiguity Avoidance**: Retain access to primary objective state files, ensuring the control plane remains functional.

---

# 5. Accessibility Requirements

## Global Accessibility Rules
*   All active controls must satisfy WCAG 2.1 AA target size parameters ($>44\times44\text{px}$).
*   Contrast ratios on slate glassmorphic surfaces must meet $4.5:1$ requirements.
*   Every active control must implement `aria-label` or semantic text descriptors.

## Dense Data View Rules
*   High-density tables (e.g., audit log ledger) must define scopes (`scope="col"`, `scope="row"`) and implement caption descriptions.
*   Text sizes inside grid elements cannot scale below `0.75rem` (12px).

## Workflow and Graph Interaction Rules
*   Neo4j graphs and LangGraph DAG canvases must support keyboard traversal. Arrow keys navigate node links.
*   Pressing `Enter` on a selected node displays the details slide-over panel.

## Keyboard and Screen Reader Rules
*   Modals must trap keyboard focus and release focus on close.
*   Aria-live zones (`aria-live="polite"`) announce background updates (e.g., container status changes, critique completion).
*   Focus indicators implement high-contrast colors (`outline: 2px solid #818cf8` with offsets).

## Responsive Behavior Rules
*   Dense 12-column grids adapt to single-column vertical scrolls below `--breakpoint-md` ($768\text{px}$).
*   Multi-panel workspaces collapse sidebars and drawers into slide-overs, accessible via touch triggers.

---

# 6. Validation Review

## UX Review
*   *Strongly Supported*: Standalone primary workspaces, high-density dashboard layouts, and progressive disclosure drawers are verified.
*   *Design Decisions Needed*: Exact SVG animation configurations for health progress rings.
*   *Clarification Required*: Visual presentation rules for displaying plan critiques.

## Accessibility Review
*   *Strongly Supported*: Focus outline tokens and multi-modal status indicators are verified.
*   *Design Decisions Needed*: Touch layout mappings for complex topology canvases.
*   *Clarification Required*: Text alternatives for dynamic node relationships.

## Governance Review
*   *Strongly Supported*: Separation of duties forms, waiver exception queues, and immutable audit logs are verified.
*   *Design Decisions Needed*: Override approval templates for quick executive signatures.
*   *Clarification Required*: Integration paths for external compliance standards.

## Scalability Review
*   *Strongly Supported*: Standalone SPA files served by lightweight routing prevent framework bottlenecks.
*   *Design Decisions Needed*: Telemetry polling throttle rules during network congestion.
*   *Clarification Required*: Storage bounds for postgres audit ledger tables.

## Implementation Readiness Review
*   *Strongly Supported*: BFF REST endpoints and docker network configurations are active.
*   *Design Decisions Needed*: Shared CSS tokens deployment rules.
*   *Clarification Required*: Latency constraints for local Ollama/TinyLlama text parsing gateway.

---

# 7. Assumptions
*   We assume that the client application communicates with the backend HTTP server over port 8099 with connection timeouts set to 30 seconds.
*   We assume that the user's browser is modern and supports ES6 module imports and CSS custom variables natively.
*   We assume that PII masking heuristics in the DTASE engine occur on the client or in a secure gateway before sending data to Ollama.
*   We assume that the PostgreSQL audit logs and Marquez lineage records are read-only and cannot be modified by any user role.
*   We assume the C4 topology viewer renders static configuration maps generated from the system’s Docker compose layout.
