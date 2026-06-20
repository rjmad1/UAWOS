# Universal AI Workforce Operating System (UAWOS)
# Engineering Deliverables Specification (PHASE 9)

> **Workspace Context:** `rjmad1/UAWOS`  
> **Standards References:** UCA v1.0, WAAS v1.0, OPES v1.0, CIAS v1.0, GCF v1.0, PMCMS v1.0, VRMS v1.0, PRTCS v1.0, PVRS v1.0, RDMS v1.0

---

# 1. Deliverables Overview

## Delivery Objectives
This document establishes the delivery requirements, functional specifications, and release sequencing maps for the UAWOS front end. These deliverables are designed to:
*   Standardize front-end development requirements across multiple team workspaces.
*   Enforce non-bypassable compliance, access authorization, and security checks at the UI level.
*   Coordinate the phased release of primary user journeys based on documented priority maps (P1 vs. P2).
*   Align component design standards to strict WCAG 2.1 AA accessibility guidelines.

---

## Verified Delivery Inputs
*   **Target Journeys**: Ingestion Studio, Command Center monitoring, and exception override waiver queues are verified as P1 priorities. Plan simulations and value ROI ledgers are P2.
*   **Infrastructure**: Python REST API endpoints and PostgreSQL transactional databases are operational.
*   **Branding Limits**: Brand assets, color palettes, and visual styles are unverified in the current codebase.

---

## Delivery Gaps or Unknowns
*   **Multi-tenant Deployments**: Release guidelines for multi-tenant workspace isolation boundaries are not specified.

---

# 2. Front-End PRD

## Product Summary
The UAWOS front end is a governed, outcome-centric, dark-mode glassmorphic control plane designed to coordinate human operators and AI agent workforces. The application replaces standard task-based tickets with interactive objective dependency networks, enabling real-time status monitoring, plan simulations, OPA policy authoring, and value realization tracking.

---

## Problem Statement
Traditional enterprise project management tools are task-centric, tracking outputs (tickets completed) rather than realized business outcomes (ROI). Furthermore, the rapid growth of autonomous agents (**agent sprawl**) creates severe security, cost, and copyleft licensing risks that cannot be audited or controlled through traditional software portals.

---

## Goals and Non-Goals
*   **Goals**:
    *   Ingest unstructured PRD/voice requirements and verify measurability checklist status (Law 1).
    *   Compare plan candidates using Monte Carlo cost-duration simulations.
    *   Monitor core container uptime and execute manual agent Kill Switches.
    *   Audit execution lineage using OpenLineage Marquez log graphs.
    *   Approve temporary policy exception waivers under strict separation of duties.
*   **Non-Goals**:
    *   Creating a generic code editor or IDE.
    *   Building a custom LLM model training portal.
    *   Integrating consumer-focused, un-governed chat assistants.

---

## Users and Personas
*   *Economic Buyer (Executive / CEO)*: Approves waivers, audits portfolio spent.
*   *Objective Owner (Product Manager)*: Ingests requirements, publishes roadmaps.
*   *Operational Controller (SRE)*: Monitors system uptime, suspends loops.
*   *Task Owner (Developer / Engineer)*: Completes task workspaces, authorizes tools (HITL).
*   *Auditor (Compliance Officer)*: Audits access tuples, drafts Rego rules.

---

## Core Use Cases
*   **Ingesting Raw Intent**: PM pastes text $\rightarrow$ DTASE parses PII $\rightarrow$ PM resolves completeness critique $\rightarrow$ publishes objective.
*   **Simulating Plan Candidates**: PM published objective $\rightarrow$ Simulation Agent runs Monte Carlo forecasts $\rightarrow$ PM compares cards $\rightarrow$ PM approves budget.
*   **Troubleshooting Blocker Alerts**: SRE monitors dashboard $\rightarrow$ GPLv3 risk card highlights copyleft alert $\rightarrow$ SRE clicks Kill Switch.
*   **Authorizing Policy Waiver**: Agent tool call blocked $\rightarrow$ EXC-xxx request escalated $\rightarrow$ Executive inputs token signature $\rightarrow$ DAG resumes.

---

## Functional Requirements
*   *FR-001 (Ingestion Studio)*: Text paste panel with character count limits and drag-and-drop PDF parser trigger.
*   *FR-002 (Critique Accordion)*: Visual critique checklist checking outcomes and success metrics.
*   *FR-003 (Plan Cards)*: Comparative grid showing cost, time, and success probability variables.
*   *FR-004 (strict health Ring)*: Circular progress ring updating dynamically via status APIs.
*   *FR-005 (Active Blocker Cards)*: High-priority alerts displaying error strings and action bypasses.
*   *FR-006 (Waiver Approval Panel)*: Signature inputs and justification forms.
*   *FR-007 (Traceability Board)*: Matrix mapping requirements to task logs.

---

## Non-Functional Requirements
*   *NFR-001 (Performance)*: Dashboard initial load time budget: $<1.5$ seconds.
*   *NFR-002 (Uptime)*: Real-time telemetry widgets update latency: $<5$ seconds.
*   *NFR-003 (Accessibility)*: $100\%$ compliance with WCAG 2.1 AA parameters.
*   *NFR-004 (Auditability)*: Every UI action creates an immutable log containing a correlation ID.

---

## Governance and Compliance Requirements
*   *Enforces Separation of Duties*: Requesting actor cannot approve exceptions.
*   *License Compliance*: Direct copyleft dependencies (Marker) must remain sandboxed.
*   *Stateless Policy Engine*: Every API call pre-checks OPA Rego rules.

---

## Success Metrics
*   Objective Success Rate ($>90\%$), Policy Compliance Rate ($100\%$), MTTR for active SRE blockers ($<1$ minute), and Ingestion completeness speed ($<5$ minutes).

---

## Risks and Dependencies
*   *Inference Latency*: Local LLM gateway lags cause UI timeouts.
*   *JSON File Lockout*: Concurrent client writes on local JSON state files cause collisions.

---

# 3. UX Requirements Specification

## UX Objectives
The UAWOS interface must feel like an outcome control plane. It must reduce ambiguity, expose agent reasoning, and prioritize policy controls.

---

## Journey Requirements
*   **Ingestion Journey**: Progressive skeletons during PDF parse $\rightarrow$ split-screen critique questionnaire.
*   **Waiver Journey**: Non-closable override modals $\rightarrow$ mandatory justification fields $\rightarrow$ validation checkers.
*   **Command Center Journey**: Dashboard traffic lights $\rightarrow$ active blocker banners $\rightarrow$ manual Kill Switch confirmation modals.

---

## Interaction Requirements
*   Milestone timeline re-sequencing utilizes drag-and-drop controls, checked by cycle conflict APIs.
*   Clicking a realized value score opens the progressive disclosure Marquez lineage drawer.

---

## Explainability Requirements
*   Blocked tasks display monospace OPA Rego rule code.
*   Plan cards display Challenger agent contrarian reports.
*   Suspended agent cards display performance history radar charts.

---

## Accessibility Requirements
*   Target size: $>44\times44\text{px}$.
*   Focus outlines meet $4.5:1$ contrast parameters.
*   Status badges combine colors with symbols.

---

## State and Feedback Requirements
*   Displays progressive skeletons during loading states.
*   Degraded mode displays grey status badges for offline engines.

---

## Role and Permission Requirements
*   Buttons disable and display lock indicators if FGA permission tuples are missing.

---

# 4. UI Architecture Specification

## Application Areas
`uawos_dashboard.html` (Command Center) $\rightarrow$ `uawos_requirement_studio.html` (Ingestion) $\rightarrow$ `uawos_roadmap.html` (Roadmap Gantt) $\rightarrow$ `uawos_delivery.html` (Traceability matrix) $\rightarrow$ `uawos_architecture.html` (C4 Topology).

---

## Navigation and Object Model
Landmark navigation panel on the left. The hierarchy maps: `Portfolio` $\rightarrow$ `Objective` $\rightarrow$ `Plan` $\rightarrow$ `Workflow` $\rightarrow$ `Task` $\rightarrow$ `Artifact` $\rightarrow$ `Value Realization`.

---

## Module and Screen Boundaries
Modules are compiled as self-contained folder structures (`modules/`) under a single client repository shell.

---

## Shared Interaction Patterns
Slide-over drawers for Marquez lineage traces, action confirmation modals for budget overrides, and notification toasts.

---

## Design System Dependencies
Variables are imported from the `@uawos/design-system` package.

---

## Visualization Dependencies
Interactive canvases utilize D3.js and Neo4j Cypher queries.

---

# 5. Front-End Technical Design Document

## Architecture Summary
Standalone SPA files served via Python routing on port 8099. We recommend TypeScript compilation and Web Component packaging.

---

## Technical Constraints
*   Synchronous string parsing in Python routing rules.
*   In-memory ES6 controller store with server JSON fallbacks.

---

## Front-End Patterns
Unidirectional data flow stores with SessionStorage caches to persist workspace filters.

---

## API and State Considerations
BFF requests inject secure JWT tokens, correlation IDs, and idempotency headers.

---

## Performance and Scalability Requirements
Virtualized list rendering for large ledgers, SVG force-simulation limits for node canvases, and brotli Compression on asset delivery.

---

## Observability and Auditability Requirements
OpenTelemetry client instrumentation maps browser errors directly to Postgres audit logs.

---

## Security and Access-Control Requirements
Client-side mock-OPA pre-flight checks match backend declarative validation rules.

---

## Testing Requirements
Vitest unit tests, Playwright end-to-end integration tests, and axe-core accessibility gates.

---

# 6. Component Inventory

| Component Name | Purpose | Verification | Dependency | Priority |
| :--- | :--- | :--- | :--- | :--- |
| **health progress ring** | Displays strict health score | Verified | None | MVP |
| **live indicator dot** | Pulsing connection status | Verified | Status API | MVP |
| **active blocker card** | Flashing alarm card | Verified | None | MVP |
| **Component list table** | Displays container states | Verified | Status API | MVP |
| **Kill Switch button** | Suspends runaway agent loops | Verified | Agent API | MVP |
| **Critique Checklist** | Displays PRD completeness checks | Verified | DTASE | MVP |
| **Plan candidate cards** | Compares simulation results | Verified | Planner API | MVP |
| **Waiver override modal** | Signoff interface for exceptions | Verified | OPA/FGA | MVP |
| **Rego Policy Editor** | Authors declarative policies | Inferred | OPA | Phase 2 |
| **Marquez lineage drawer** | Traces data flow and artifacts | Verified | Marquez API | Phase 2 |
| **FGA Tuple diagram** | Renders user-role relationship links | Inferred | FGA API | Phase 2 |
| **Neo4j graph canvas** | Visualizes semantic knowledge nodes | Inferred | Neo4j API | Phase 2 |
| **PMCMS score card** | Displays maturity ratings | Inferred | PMCMS API | Phase 2 |

---

# 7. Design System Specification

*   **Foundations**: Standardizes slate glassmorphism tokens, Outfit/Inter typography, and grid spacings.
*   **Component Standards**: Requires native Web Component packaging with isolated Shadow DOM styling.
*   **Accessibility Gates**: Mandates automated axe-core compilation checks.
*   **Governance UI Standards**: Enforces separation of duties boundaries on approvals.
*   **Data Visualization Standards**: Chart colors must match semantic status tokens.

---

# 8. Accessibility Compliance Specification

*   **Keyboard Behavior**: Focus indicators display a high-contrast Indigo outline with offsets; tab index covers all active nodes.
*   **Form Accessibility**: Inputs include explicit labels and link to error logs via `aria-describedby`.
*   **Dense Data Accessibility**: Tables define scopes on headers and include caption descriptions.
*   **Visualization Accessibility**: SVG charts must provide text-equivalent alt data tables.
*   **Verification Rules**: axe-core scans must return zero accessibility violations in the build pipeline.

---

# 9. Front-End Roadmap

## Delivery Phases
*   **Phase 1 (MVP Foundation)**: Scope: Ingestion Studio, Command Center monitoring, Exception approvals modals, and Design System tokens.
*   **Phase 2 (Observability Expansion)**: Scope: Marquez lineage drawer, Rego Policy Editor, and FGA Tuple visualizer.
*   **Phase 3 (Adaptive Optimization)**: Scope: Neo4j Knowledge Graph canvas and PMCMS score cards.

---

## Dependency Logic
Phase 1 builds the core design system and validation forms. Phase 2 integrates auditability, and Phase 3 adds advanced semantic views.

---

## Team Considerations
Decoupling the `@uawos/design-system` package from modules allows designers and developers to work in parallel.

---

## Risks by Phase
*   *Phase 1*: Timeout lags on local Ollama DTASE parsing.
*   *Phase 2*: Concurrency locks on state file writes.

---

# 10. MVP Definition

## MVP Scope
*   Requirement Ingestion Studio (PRD paste inputs, completeness checklists).
*   Command Center monitoring (health rings, component status badges).
*   Exception approvals modal (waiver signature override form).
*   Design System token CSS variables.

---

## Excluded Scope
*   Rego Policy Editor (policies edited via backend configs).
*   Marquez OpenLineage drawer (logs checked via CLI).
*   Neo4j Knowledge Graph visualizer.

---

## MVP User Journeys
*   *PM Ingests Requirement*: Pastes PRD text $\rightarrow$ critiques completeness.
*   *SRE Monitors System*: Reviews health indicators $\rightarrow$ triggers Kill Switch.
*   *Executive Authorizes Waiver*: Receives exception alert $\rightarrow$ signs waiver.

---

## MVP Success Criteria
*   Completeness checklists load in under 1 second.
*   Command Center health score updates in real-time.
*   Waiver signoff token overrides are verified by FGA.

---

## MVP Risks
*   Inefficient local LLM execution blocks ingestion studio performance.

---

# 11. Release Strategy

## Release Principles
1.  **Fail-Secure**: Release pipelines block deployments if compilation checks or compliance tests fail.
2.  **Zero-Downtime Telemetry**: Command Center views must continue loading cached snapshots during rollout.

---

## Release Sequence
1.  *Stage 1 (Internal Beta)*: Ops and PM teams test MVP components.
2.  *Stage 2 (Department Rollout)*: Scopes to selected business unit portfolios.
3.  *Stage 3 (Enterprise Release)*: Full rollout across workspaces.

---

## Rollout Risk Controls
Automatic rollbacks if API response errors or OPA latency checks exceed 500ms bounds.

---

## Validation Gates
*   axe-core accessibility pass.
*   OpenFGA authorization boundary check.
*   Trivy container security scan.

---

## Post-Release Monitoring
Telemetry checks monitor token consumption velocities and SRE Kill Switch overrides.

---

# 12. Validation Review

## Architecture Review
*   *Verified*: Standalone SPA files and Python routing structures are verified.
*   *Recommended*: TypeScript compilation and Web Component packaging.
*   *Blocker*: BaseHTTPRequestHandler routing is synchronous and blocks concurrent operations.
*   *Confirmation Required*: The migration timeline to FastAPI.

## UX Review
*   *Verified*: High-density dashboard widgets and health progress rings are verified.
*   *Recommended*: Progressive skeletons and split-screen workspaces.
*   *Blocker*: Lack of visual design specifications for plan critique details.
*   *Confirmation Required*: Icon library parameters.

## Accessibility Review
*   *Verified*: Contrast requirements and multi-modal status indicators are verified.
*   *Recommended*: Custom keyboard pan/zoom canvas controls.
*   *Blocker*: WCAG AA violations on circular SVGs (lack of screen-reader support).
*   *Confirmation Required*: Screen-reader text templates for health rings.

## Governance Review
*   *Verified*: OPA and OpenFGA permissions check integrations are verified.
*   *Recommended*: Local OPA pre-flight checks in client-side controllers.
*   *Blocker*: None.
*   *Confirmation Required*: Standard templates for compliance rule versions.

## Scalability Review
*   *Verified*: Relational, Vector, and Graph database structures are supported.
*   *Recommended*: SessionStorage caching for SRE filter settings.
*   *Blocker*: Concurrency issues will cause file write locks on local JSON state stores.
*   *Confirmation Required*: Relational database migration plans.

## Implementation Readiness Review
*   *Verified*: Backend REST APIs are functional and operational.
*   *Recommended*: Vite compilation and Playwright end-to-end testing stacks.
*   *Blocker*: Inline styling duplication across standalone HTML files.
*   *Confirmation Required*: Shared CSS token file compilation pipelines.

---

# 13. Assumptions
*   We assume that the client application communicates with the backend HTTP server over port 8099 with connection timeouts set to 30 seconds.
*   We assume that the user's browser is modern and supports ES6 module imports and CSS custom variables natively.
*   We assume that PII masking heuristics in the DTASE engine occur on the client or in a secure gateway before sending data to Ollama.
*   We assume that the PostgreSQL audit logs and Marquez lineage records are read-only and cannot be modified by any user role.
*   We assume the C4 topology viewer renders static configuration maps generated from the system’s Docker compose layout.
