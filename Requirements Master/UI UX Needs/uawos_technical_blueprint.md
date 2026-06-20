# Universal AI Workforce Operating System (UAWOS)
# Front-End Technical Blueprint Specification (PHASE 8)

> **Workspace Context:** `rjmad1/UAWOS`  
> **Standards References:** UCA v1.0, WAAS v1.0, OPES v1.0, CIAS v1.0, GCF v1.0, PMCMS v1.0, VRMS v1.0, PRTCS v1.0, PVRS v1.0, RDMS v1.0

---

# 1. Technical Blueprint Overview

## Technical Objectives
The UAWOS Front-End Technical Blueprint establishes the implementation standard for the web-based operational control plane. The front-end must provide:
*   **Absolute Auditability**: Support for OpenLineage Marquez log tracking and PostgreSQL immutable log rendering.
*   **Non-Bypassable Compliance**: Active UI gating mapping to OpenFGA relational access tuples and OPA declarative policy outcomes.
*   **High Performance**: Render high-density grids and Neo4j node-link diagrams under continuous status updates.
*   **Operational Transparency**: Visual cues for LLM/Ollama gateway status, agent trust ratings, and execution blocker cards.

---

## Verified Constraints
*   **File-Based Single-Page Applications**: Renders standalone HTML files (`uawos_dashboard.html`, `uawos_requirement_studio.html`, etc.) inside the `apps/web/` directory.
*   **Vanilla Core Stack**: Built utilizing pure Vanilla JavaScript, CSS variables, and HTML5 without modern SPA frameworks (e.g., React, Vue).
*   **HTTP server Routing**: Served by a Python-based HTTPServer (`http.server.BaseHTTPRequestHandler`) running on port 8099.
*   **Token-Based Headers**: Authentication is enforced by passing tokens via `X-UAWOS-Token` or `Authorization: Bearer <token>` in requests.
*   **REST Polling**: Core service container status and system health are monitored via 5-second polling of `GET /api/status`.

---

## Recommended Front-End Strategy
To satisfy the verified vanilla stack constraint while supporting enterprise scalability and team growth, we recommend:
*   **Native Web Components Abstraction**: Encapsulate shared components (design tokens, buttons, data grids) as native W3C Web Components.
*   **Centralized ES6 Controller Store**: Implement unidirectional data flows within client-side state handlers, utilizing local cached snapshots.
*   **Server-Sent Events (SSE) stream client**: Transition from 5s polling to SSE channels for real-time DAG updates.

---

## Technical Gaps or Unknowns
*   **Dynamic OpenFGA Tuples modifications**: Multi-user permissions edit interfaces are undocumented in the current codebase.

---

# 2. Technology Stack

## Application Framework
*   **Verification Status**: Verified.
*   **Purpose**: Renders interfaces and scopes module execution.
*   **Details**: Pure Vanilla JS, CSS variables, HTML5. Web Components recommended for modular abstractions.
*   **Trade-off**: Requires writing manual DOM reconciliation logic but guarantees zero dependency bloat.

## Language and Typing Strategy
*   **Verification Status**: Recommended.
*   **Purpose**: Static analysis and runtime safety.
*   **Details**: TypeScript (compiled to ES6 modules for browser consumption).
*   **Trade-off**: Requires a compile step but prevents parameter typing errors across complex API payloads.

## Routing
*   **Verification Status**: Verified.
*   **Purpose**: Navigation and page mapping.
*   **Details**: Server-side Python routing (`main.py` lines 83-130). Client-side native History API routing recommended.
*   **Trade-off**: Server redirects reset page state; client-side routing preserves memory contexts.

## State and Server-State Management
*   **Verification Status**: Verified.
*   **Purpose**: Context preservation and synchronization.
*   **Details**: In-memory ES6 controller store. Fallback state files committed to server JSONs.
*   **Trade-off**: File fallbacks introduce write concurrency risks.

## Component and Design System Tooling
*   **Verification Status**: Verified.
*   **Purpose**: Standardized UI rendering.
*   **Details**: Native CSS custom properties, Outfit/Inter typography, and glassmorphic variables.
*   **Trade-off**: Web Components are styled individually via Shadow DOM.

## Data Visualization Stack
*   **Verification Status**: Verified.
*   **Purpose**: Node-link diagram and KPI progress rendering.
*   **Details**: D3.js and SVG circles are verified in the codebase.
*   **Trade-off**: Requires high-performance canvas optimization.

## Forms and Validation
*   **Verification Status**: Recommended.
*   **Purpose**: Form verification prior to REST submission.
*   **Details**: Native HTML5 validation attributes (`pattern`, `required`) coupled with custom JS schemas.
*   **Trade-off**: Simple; lacks complex schema-validation frameworks.

## Accessibility Tooling
*   **Verification Status**: Recommended.
*   **Purpose**: Automated compliance checks.
*   **Details**: Axe-core CI/CD integration.
*   **Trade-off**: Catches structural errors but does not verify screen-reader usability.

## Observability and Monitoring
*   **Verification Status**: Recommended.
*   **Purpose**: Client runtime logs collection.
*   **Details**: OpenTelemetry Web SDK.
*   **Trade-off**: Overhead of telemetry payloads; resolves frontend performance diagnostics.

## Testing Stack
*   **Verification Status**: Recommended.
*   **Purpose**: Validation of module components.
*   **Details**: Playwright for end-to-end integration; Vitest for TypeScript unit tests.
*   **Trade-off**: High pipeline running times.

## Build and Delivery Tooling
*   **Verification Status**: Recommended.
*   **Purpose**: Compiling TypeScript and CSS modules.
*   **Details**: Vite (non-bundling mode during local runs, optimized single-JS output for production runs).
*   **Trade-off**: Introduces build configurations.

## Security and Dependency Controls
*   **Verification Status**: Verified.
*   **Purpose**: Package safety scans.
*   **Details**: Semgrep, Gitleaks, Trivy scanner, Dependency-Track SBOM analysis.
*   **Trade-off**: Restricts adoption of open-source libraries.

---

# 3. Folder Structure

## Proposed Monorepo Structure (Recommended)
```
[apps/web/]
  ├── src/
  │    ├── components/         # Shared Web Components (Design System)
  │    ├── modules/            # Domain Modules
  │    │    ├── executive/     # Portfolio Value and Ledger
  │    │    ├── product/       # Requirement Ingestion and Roadmaps
  │    │    ├── operations/    # Command Center and Agent registry
  │    │    ├── engineering/   # Task execution and Traceability
  │    │    └── compliance/    # OPA editor and Marquez Lineage
  │    ├── services/           # Shared APIs and Event layers
  │    ├── store/              # ES6 central state controllers
  │    └── index.ts            # SPA App Entry shell
  ├── uawos_dashboard.html
  ├── uawos_requirement_studio.html
  ├── uawos_roadmap.html
  ├── uawos_architecture.html
  ├── uawos_delivery.html
  └── package.json
```

---

## Domain Module Layout (Recommended)
Every domain module (e.g., `modules/operations/`) is organized as a self-contained module:
*   `operations.controller.ts` (API handlers, state mapping).
*   `operations.view.ts` (Dashboard template layouts).
*   `components/` (Operations-specific UI widgets).

---

## Shared Library Layout (Recommended)
`src/services/` holds shared services:
*   `api.client.ts` (REST client wrapper with token injection).
*   `event.bus.ts` (Internal message system).
*   `lineage.trace.ts` (Lineage correlation handler).

---

## Design System Layout (Recommended)
`src/components/` holds shared visual elements:
*   `tokens/` (CSS variables defining color, font, spacing, and radius).
*   `button/`, `card/`, `grid/` (Web Component templates).

---

# 4. Component Architecture

## Composition Model (Recommended)
Components are structured hierarchically:
```
Workspace Shell (Page container, gates, routing context)
   └── Container Component (Controller, API subscriber, State mapper)
         └── Presentational Component (Web Component, Design tokens)
```

---

## Domain Components vs Shared Components
*   **Domain Components**: Contain business logic (e.g., `WaiverForm` queries OPA and displays specific justification inputs; `AgentCard` triggers agent Kill Switch).
*   **Shared Components**: Agnostic to business logic (e.g., `GlassCard` handles backdrop blur; `StatusPill` renders HSL classes).

---

## Workspace Patterns
Workspaces utilize a standard split layout: a sticky sidebar on the left for strategic controls (4 columns) and a scrolling content region on the right (8 columns) for consoles and charts.

---

## Evidence and Governance UI Primitives
*   **Evidence link tag**: `<evidence-link hash="UUID">` renders an inline link opening the trace drawer.
*   **Policy Verdict Banner**: `<policy-verdict status="blocked">` displays red HSL text and justification forms.

---

## Error Boundary Strategy (Recommended)
To prevent runtime errors from bricking the dashboard, container views wrap sub-components in custom try-catch blocks, rendering an error card widget if a component fails:
```typescript
try {
  this.renderSubComponent();
} catch (e) {
  this.renderErrorCard("Component failed to load: " + e.message);
}
```

---

# 5. State Architecture

## Global State
Managed in-memory using a central ES6 Store, tracking: active User ID, current role (derived from JWT), active Portfolio ID, and active Workspace ID.

---

## Server State
Synchronized asynchronously via fetch calls, caching values inside the ES6 store scopes. Writing to server state triggers backend PostgreSQL transaction updates.

---

## Local State
Component-scoped states (e.g., accordion toggle states, text input values) are kept inside the Web Component element scopes.

---

## Long-Running Workflow State
Workflow DAG execution progress is tracked via continuous checkpoint updates. The state records the active node ID and execution status (pending, executing, blocked).

---

## Real-Time and Polling State
Maintains component health records. Updates every 5 seconds via `GET /api/status` polling.

---

## Permission and Policy State
Stores OPA verdicts and OpenFGA access checks. When an action is blocked, this state registers the justification and target policy ID.

---

## View State Persistence
To support SRE navigation, active filters, search inputs, and visual scroll positions are cached in SessionStorage.

---

## State Architecture Risks
*   **Concurrency Write Locks**: Simultaneous user updates on local JSON state files cause write collisions.
    *   *Mitigation*: Restrict client mutations to PostgreSQL transactions; use JSON storage for read-only default configurations.

---

# 6. API Layer Design

## BFF Integration Strategy
The BFF acts as a single gateway, transforming backend PostgreSQL schemas and Marquez logs into optimized JSON payloads for UI rendering.

---

## API Client Structure
The client wrapper dynamically injects secure tokens and correlation IDs:
```typescript
class APIClient {
  async fetch(url: string, options: RequestInit = {}) {
    const headers = new Headers(options.headers);
    headers.set("X-UAWOS-Token", this.getToken());
    headers.set("X-Correlation-ID", this.generateUUID());
    return fetch(url, { ...options, headers });
  }
}
```

---

## Error Handling Model
REST errors must return a normalized structure: `{"error": "message", "code": "STATUS_CODE", "diagnostics": {}}`. The UI parses the code to render component error cards.

---

## Retry and Idempotency Strategy
*   **Idempotency Header**: POST mutations attach an `Idempotency-Key` header.
*   **Retry throttle**: API timeouts trigger exponential backoff retries (maximum 3 attempts).

---

## Long-Running Operations Model
Intake critiques and simulation runs return a `202 Accepted` status along with a job status URL. The client polls the status URL until compilation completes.

---

## Policy Pre-Check vs Authoritative Enforcement
*   **Client Pre-Check**: The UI runs a local OPA policy check before submission.
*   **Server Enforcement**: The server executes the authoritative Rego policy run. The client intercepts server rejections and displays policy warning cards.

---

## Traceability and Correlation IDs
Every action triggered by the UI appends a unique `X-Correlation-ID` header. This ID traces the UI click to OPA policy runs, Marquez lineage logs, and PostgreSQL ledger entries.

---

# 7. Event Architecture

## Polling Model
Core component health and active incident count are queried via 5-second polling of `GET /api/status`.

---

## Real-Time Update Strategy (Recommended)
For active workflow execution, we recommend Server-Sent Events (SSE) `/api/status/stream`. The client binds to events:
```typescript
const eventSource = new EventSource("/api/status/stream");
eventSource.addEventListener("WorkflowProgress", (e) => {
  this.updateDAGVisualizer(JSON.parse(e.data));
});
```

---

## Event Failure Handling
SSE timeouts trigger automatic reconnect attempts. The UI displays a warning indicator ("Re-connecting to stream...") during offline states.

---

# 8. Design System Architecture

## Token Architecture
Design tokens are declared in a shared CSS file, mapping colors, typography, radius, and spacing to CSS variables.

---

## Component Packaging Strategy
Design system components are packaged as a shared internal library (`@uawos/design-system`), allowing all standalone SPA apps to import identical assets.

---

## Theming Strategy
Theming is handled natively via variable swaps in the CSS root selector:
```css
:root[theme="dark"] {
  --color-bg-base: #080a10;
}
```

---

## Accessibility Enforcement Strategy
CI/CD testing runs automated axe-core accessibility checks on design system component templates.

---

# 9. Micro-Frontend Considerations

## Applicability Assessment
We do **not** recommend micro-frontend frameworks for UAWOS in Phase 1.
*   *Why*: The application is currently optimized for a single-tenant environment with a small developer team. Introducing micro-frontend tooling would increase build complexity and interface latency.

---

## Integration Constraints
If micro-frontends become necessary due to team scaling, we recommend using native iframe boundaries with secure PostMessage interfaces to isolate workspaces.

---

# 10. Scalability Strategy

*   **Module Scalability**: New features are added as self-contained directories under `modules/`.
*   **Team Scalability**: Decoupling the shared design system package (`@uawos/design-system`) from domain modules allows independent UI updates.
*   **Data Scalability**: Renders large audit ledgers and logs using virtualized list rendering.
*   **Access Control Scalability**: The UI queries OpenFGA dynamic permissions on mount, preventing complex hardcoded checks.

---

# 11. Performance Strategy

*   **Initial Load**: Standalone HTML files are lightweight; assets are served compressed (gzip/brotli) from the Python gateway.
*   **Data Grid Performance**: Employs virtual scrolling for PostgreSQL audit log timelines.
*   **Graph Performance**: Neo4j and Marquez canvas canvases limit force-simulation ticks to 100 on load.
*   **Performance Budgets**: Page weight limit: $<500\text{KB}$; initial load time budget: $<1.5$ seconds.

---

# 12. Validation Review

## Architecture Review
*   *Verified*: Standalone SPA files and Python BFF integrations are well-supported.
*   *Recommended*: TypeScript compilation and Web Component packaging.
*   *Blocker*: BaseHTTPRequestHandler routing is synchronous and blocks concurrent operations.
*   *Confirmation Required*: The migration roadmap to FastAPI.

## Governance Review
*   *Verified*: OPA and OpenFGA policy evaluation endpoints are verified.
*   *Recommended*: Local OPA pre-flight checks in client-side controllers.
*   *Blocker*: None.
*   *Confirmation Required*: Standard templates for compliance rule versions.

## Scalability Review
*   *Verified*: Relational, Vector, and Graph database structures are supported.
*   *Recommended*: SessionStorage caching for SRE filter settings.
*   *Blocker*: Concurrency issues will cause file write locks on local JSON state stores.
*   *Confirmation Required*: Relational database migration plans.

## UX Review
*   *Verified*: Dark glassmorphic tokens, Outfit/Inter typography, and health ring animations are verified.
*   *Recommended*: Aria-live regions and custom keyboard pan/zoom graph controls.
*   *Blocker*: WCAG AA violations on circular SVGs (lack of screen-reader support).
*   *Confirmation Required*: Graphic assets and exact icon system mappings.

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
