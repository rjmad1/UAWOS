# Universal AI Workforce Operating System (UAWOS)
# Data Visualization Architecture Specification (PHASE 7)

> **Workspace Context:** `rjmad1/UAWOS`  
> **Standards References:** UCA v1.0, WAAS v1.0, OPES v1.0, CIAS v1.0, GCF v1.0, PMCMS v1.0, VRMS v1.0, PRTCS v1.0, PVRS v1.0, RDMS v1.0

---

# 1. Visualization Architecture Overview

## Visualization Operating Principles
Data visualizations in UAWOS are not decorative graphics. They serve as primary operational controls and audit interfaces that reveal human-agent execution paths. Visualizations are governed by three core principles:
1.  **Decision-Utility**: Every graph, chart, and map must directly support an operational decision (e.g., plan selection, workflow suspension, or exception waiver signoff).
2.  **Verifiable Grounding**: Visual representations of realized value, spent tokens, or learning assets must expose direct traceability to raw logs and hashes.
3.  **Governance Transparency**: Compliance limits, policy evaluation bounds, and access tuple constraints are permanently visible within execution visuals.

---

## Role-to-Visualization Mapping
*   **Executive (CEO/CFO)**: Accesses Portfolio Heatmaps and Value Realization metric rings to analyze ROI and authorize waivers.
*   **Product Manager (PM)**: Accesses Objective Dependency Graphs, Simulation Outcome probability curves, and Roadmap timelines to decompose goals and prioritize roadmaps.
*   **Operations Leader (SRE)**: Accesses strict health circular progress rings, component container lists, and Agent Relationship networks to monitor system telemetry and invoke Kill Switches.
*   **Engineer (Developer)**: Accesses LangGraph DAG visualizers, task consoles, and code scanner diff indicators to write and verify code artifacts.
*   **Compliance Officer**: Accesses OPA Policy registries, OpenFGA Tuple Diagrams, and Marquez Lineage trees to execute compliance audits.

---

## Real-Time vs Analytical Visualization Strategy
*   **Real-Time Observability**: Component status grids and health meters update dynamically via `/api/status` polling loops.
*   **Analytical Modeling**: Monte Carlo probability distributions, forecast variance scatter plots, and Neo4j ontology trees run off backend snapshot databases to represent predictive models.

---

## Explainability and Auditability Strategy
Visualizations must display calculation inputs. Hovering or clicking on a graph node (e.g., an objective health score) opens inline drawers showing the specific variables (checklist complete count, missing outcome penalty) that calculated the score.

---

## Visualization Gaps or Unknowns
*   **Cross-Tenant Analytics**: Multi-tenant metrics and cross-tenant policy registries are undocumented in the current codebase.

---

# 2. Visualization Specifications

## Objective Dependency Graphs
*   **Verification Status**: Verified.
*   **Purpose**: Visualizes objective networks to detect cycle conflicts and priority mismatches.
*   **Primary Users**: Product Manager, Operations Leader.
*   **Decision / Workflow Supported**: Resolving circular dependency blocks on roadmap timelines.
*   **Underlying Data Model**: `uawos_objective_state.json`.
*   **Required Entities or Measures**: Objective ID, parent/child relationships, health score (%), lifecycle status.
*   **Recommended Visual Form**: D3 force-directed node-link graph.
*   **Visual Encoding Strategy**: Node fill maps to status (Green: completed, Red: blocked, Grey: archived). Edges represent dependency direction. Flashing red border highlights cycle conflicts.
*   **Interaction Model**: Drag nodes to reposition; click node to open detail slide-over.
*   **Drill-Down Model**: Double-clicking node opens the Ingestion Studio planning tab.
*   **Explainability Requirements**: Hovering blocked node displays list of violating OPA rules.
*   **Governance / Trust Implications**: Enforces Constitutional Law 1 (health score deduction).
*   **Accessibility Requirements**: Node links navigable via keyboard tab index.
*   **Failure Risks**: High canvas complexity lags browser rendering under large networks.

---

## Agent Relationship Graphs
*   **Verification Status**: Verified.
*   **Purpose**: Directory of active agents, trust scores, and runtime states.
*   **Primary Users**: Operations Leader, SRE.
*   **Decision / Workflow Supported**: Identifying agent loop overruns and executing manual suspension kill switches.
*   **Underlying Data Model**: `uawos_agent_workforce_state.json`.
*   **Required Entities**: Agent ID, agent class, trust score (0.00-1.00), status, autonomy profile.
*   **Recommended Visual Form**: Multi-layered node network.
*   **Visual Encoding Strategy**: Node size encodes trust score; color maps to status (Green: active, Red: suspended).
*   **Interaction Model**: Hover displays trust history tooltips; click button to suspend executor.
*   **Drill-Down Model**: Double-click opens Agent performance log details.
*   **Explainability Requirements**: Radar charts show trust score metrics (historical runs, compliance verification rates).
*   **Governance / Trust Implications**: Automatically suspends agents whose trust falls below 70.
*   **Accessibility Requirements**: Aria-live zones announce status transitions.
*   **Failure Risks**: Latency spikes on telemetry update loops.

---

## Portfolio Heatmaps
*   **Verification Status**: Inferred.
*   **Purpose**: Renders portfolio value allocations, spent distributions, and readiness rankings.
*   **Primary Users**: Executive, C-Suite.
*   **Decision / Workflow Supported**: Portfolio capacity adjustment.
*   **Underlying Data Model**: `uawos_budget_state.json`, PVRS standard.
*   **Required Measures**: Managed Value Capacity ($), actual spent ($), readiness score (%).
*   **Recommended Visual Form**: Nested Treemap.
*   **Visual Encoding Strategy**: Box size maps to managed capacity; color hue maps to readiness score.
*   **Interaction Model**: Hover displays tooltip; click box to drill into portfolio objectives.
*   **Drill-Down Model**: Navigates to Portfolio details dashboard.
*   **Explainability Requirements**: Displays baseline value hypothesis calculations.
*   **Governance / Trust Implications**: Limits managed capacity allocations.
*   **Accessibility Requirements**: Keyboard focus indicators map focus outlines to active boxes.
*   **Failure Risks**: Missing metrics cause layout calculation failures.

---

## Risk Matrices
*   **Verification Status**: Inferred.
*   **Purpose**: Maps identified execution risks and compliance drift.
*   **Primary Users**: Executive, Compliance Officer.
*   **Decision / Workflow Supported**: Reviewing risk exposure and signing risk acceptances.
*   **Underlying Data Model**: `uawos_governance_state.json`, PRTCS standard.
*   **Required Measures**: Risk impact (1-5), risk likelihood (1-5), severity score.
*   **Recommended Visual Form**: $5\times5$ Grid Matrix.
*   **Visual Encoding Strategy**: Grid colors map to severity (Green: low, Red: critical). Matrix bubbles represent active risk events.
*   **Interaction Model**: Hover bubble displays risk ID and owner; click bubble opens waiver request modal.
*   **Drill-Down Model**: Opens Exception approvals details workspace.
*   **Explainability Requirements**: Risk scoring model (Impact $\times$ Likelihood $\times$ Confidence).
*   **Governance / Trust Implications**: CEO must sign off on critical bubble overrides.
*   **Accessibility Requirements**: High contrast borders around grid cells.
*   **Failure Risks**: Opaque risk parameters lead to blind waivers.

---

## Budget Analytics
*   **Verification Status**: Verified.
*   **Purpose**: Trend tracking of actual spent tokens vs. forecast limits.
*   **Primary Users**: Executive, Product Manager.
*   **Decision / Workflow Supported**: Adjusting objective budget limits.
*   **Underlying Data Model**: `uawos_budget_state.json`.
*   **Required Measures**: Allocated Limit ($), actual spent ($), token cost velocity.
*   **Recommended Visual Form**: Dual axis line and bar chart.
*   **Visual Encoding Strategy**: Bar charts represent daily token count; line curves map cumulative cost.
*   **Interaction Model**: Tooltip on point hover; zoom window controls.
*   **Drill-Down Model**: Opens Budget Ledger details screen.
*   **Explainability Requirements**: Displays spent breakdown by agent and LLM gateway.
*   **Governance / Trust Implications**: OPA pre-checks cost limits on adjustments.
*   **Accessibility Requirements**: Alt-text description lists chart values.
*   **Failure Risks**: Fallback JSON state writes fail due to write concurrency locks.

---

## Simulation Outcomes
*   **Verification Status**: Verified.
*   **Purpose**: Compares plan candidates cost/time forecasting curves.
*   **Primary Users**: Product Manager.
*   **Decision / Workflow Supported**: Selecting plan candidate.
*   **Underlying Data Model**: `uawos_simulation_state.json`.
*   **Required Measures**: Cost forecast ($), duration forecast (days), success probability (%).
*   **Recommended Visual Form**: Monte Carlo probability distribution scatter plot.
*   **Visual Encoding Strategy**: Points represent simulated runs; shaded area bounds $90\%$ confidence interval.
*   **Interaction Model**: Select plan dropdown to toggle chart overlay.
*   **Drill-Down Model**: Opens Simulation Center run details console.
*   **Explainability Requirements**: Challenger Agent contrarian reports explaining simulation risk variables.
*   **Governance / Trust Implications**: Forecasts precede planning selection.
*   **Accessibility Requirements**: Chart labels meet contrast ratio of 4.5:1.
*   **Failure Risks**: Plan candidate comparisons fail if parameter bounds are empty.

---

## Value Realization Metrics
*   **Verification Status**: Verified.
*   **Purpose**: Live tracking of actual spend vs. target metrics.
*   **Primary Users**: Executive, PM.
*   **Decision / Workflow Supported**: Verifying ROI.
*   **Underlying Data Model**: `uawos_value_state.json`.
*   **Required Measures**: Target metrics, realized value ($), spent tokens.
*   **Recommended Visual Form**: Concentric progress gauge.
*   **Visual Encoding Strategy**: Gauge arcs display outcome milestones; text shows realized ROI.
*   **Interaction Model**: Clicking metric opens Evidence Drawer.
*   **Drill-Down Model**: Opens Marquez Lineage drawer.
*   **Explainability Requirements**: Trace path maps outputs back to requirements.
*   **Governance / Trust Implications**: Enforces Law 12.
*   **Accessibility Requirements**: Text alternatives display formulas.
*   **Failure Risks**: Missing outcome data breaks calculations.

---

## Governance Status Maps
*   **Verification Status**: Verified.
*   **Purpose**: Displays OPA policy compliance and access boundaries.
*   **Primary Users**: Compliance Officer.
*   **Decision / Workflow Supported**: Auditing compliance drift.
*   **Underlying Data Model**: `uawos_governance_state.json`, OpenFGA API.
*   **Required Entities**: Policy status, FGA tuples.
*   **Recommended Visual Form**: Blended visual dashboard (Tuple diagram node-link graph + Policy status indicators).
*   **Visual Encoding Strategy**: Badge color maps to verdict ( Emerald: OPA Approved, Red: Blocked).
*   **Interaction Model**: Clicking tuple opens Role Mapping registry.
*   **Drill-Down Model**: Opens OPA status console.
*   **Governance / Trust Implications**: Central audit dashboard.
*   **Accessibility Requirements**: Scopes defined on tables.
*   **Failure Risks**: Static FGA tuples hide access drift.

---

## Knowledge Graphs
*   **Verification Status**: Verified.
*   **Purpose**: Visualizes Cypher mappings of knowledge nodes and learning assets.
*   **Primary Users**: PM, Compliance.
*   **Decision / Workflow Supported**: Context checking.
*   **Underlying Data Model**: `uawos_knowledge_state.json`, Neo4j.
*   **Required Entities**: KnowledgeAsset, Claim, Evidence, Learning.
*   **Recommended Visual Form**: Interactive Node-link canvas.
*   **Visual Encoding Strategy**: Node types mapped by icon symbol; color maps to source provenance (IMAP, Slack, OCR).
*   **Interaction Model**: Pan/zoom canvas, click node to view details card.
*   **Drill-Down Model**: Opens Knowledge details drawer.
*   **Explainability Requirements**: Node details display raw document inputs.
*   **Governance / Trust Implications**: Enforces Law 9.
*   **Accessibility Requirements**: Navigable via keyboard arrow keys.
*   **Failure Risks**: Dynamic canvas updates reset collapse states.

---

# 3. Shared Visualization Interaction Patterns

## Filtering and Slicing
*   Cross-dashboard filters map across all active visualizations: **Portfolio ID**, **Objective ID**, **Milestone Track**, **Severity level**.

---

## Drill-Down and Cross-Linking
*   Clicking a visualization element (e.g., node, box, bar) opens related details drawers or modals without losing the parent screen state.

---

## Evidence and Explanation Patterns
*   Hovering or clicking on value realization scores or agent trust meters triggers slide-over drawers displaying verifying logs and calculation formulas.

---

## Alerting and Threshold Patterns
*   Critical failures (e.g., budget breaches, GPLv3 compliance risks) trigger flashing red HSL boundaries and top-level Command Center alerts.

---

## Accessibility for Data Visualization
*   Every visualization must provide alternative text descriptions or accessible HTML data tables.
*   Keyboard navigation traversals follow a logical top-to-bottom, left-to-right tab order.
*   Focus outlines implement high-contrast colors (`outline: 2px solid #818cf8` with offsets).

---

## Empty, Error, and Degraded States
*   **Empty state**: Illustrative card showing clear checkmark states ("No active exceptions pending").
*   **Error state**: Red banner with connection status and reconnect triggers.
*   **Degraded State**: Grey badges for offline components; continue loading cached snapshots.

---

# 4. Validation Review

## UX Review
*   *Strongly Supported*: Objective dependency graphs, health meters, and simulation scatter plots are verified.
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

# 5. Assumptions
*   We assume that the client application communicates with the backend HTTP server over port 8099 with connection timeouts set to 30 seconds.
*   We assume that the user's browser is modern and supports ES6 module imports and CSS custom variables natively.
*   We assume that PII masking heuristics in the DTASE engine occur on the client or in a secure gateway before sending data to Ollama.
*   We assume that the PostgreSQL audit logs and Marquez lineage records are read-only and cannot be modified by any user role.
*   We assume the C4 topology viewer renders static configuration maps generated from the system’s Docker compose layout.
