# Universal AI Workforce Operating System (UAWOS)
# Design System Specification (PHASE 4)

> **Prepared by:** Principal UX Architect & Design Systems Lead  
> **Workspace Context:** `rjmad1/UAWOS`  
> **Standards References:** UCA v1.0, WAAS v1.0, OPES v1.0, CIAS v1.0, GCF v1.0, PMCMS v1.0, VRMS v1.0, PRTCS v1.0, PVRS v1.0, RDMS v1.0

---

# 1. Design Philosophy

## Design System Purpose
The UAWOS Design System exists to establish a visual control plane that enables humans to govern, orchestrate, and audit a combined human-AI workforce. Its primary purpose is to convert complex execution data, model reasoning patterns, and stateless compliance logs into clear, actionable visual states.

By doing so, the design system aims to:
*   **Prevent Autonomy Opaque states**: Ensure no agent executes a task without exposing its trust score, parameters, and outputs.
*   **Enforce Policy Visibility**: Render stateless OPA policy evaluations and OpenFGA permissions check verdicts directly within operational workflows.
*   **Eliminate Coordination Ambiguity**: Structure workspace layouts to prioritize objective success metrics and outcome realization logs over simple task boards.
*   **Guarantee Compliance Safety**: Prevent compliance decay and supply-chain risk (e.g., GPLv3 license contamination) through visual block signaling and sandboxed CLI displays.

## Design Principles
*   **Objective Supremacy**: The primary structural element of any view is the Objective. The user must always interact with objectives and success metrics first; plan decompositions, workflow DAGs, and task details are progressively disclosed.
    *   *Why it matters*: Prevents the system from degrading into a generic task management board.
    *   *UI Implications*: All navigation paths, search indexing, and graph nodes root to an Objective ID.
    *   *Failure Mode*: Organizing screens around team backlogs, losing the connection to strategic business value.
*   **Fail-Secure Visibility**: Security and governance verdicts are supreme and non-bypassable. If an action is blocked by OPA or FGA, the system must expose *why* and present clear escalation pathways.
    *   *Why it matters*: Guarantees that users cannot accidentally bypass compliance rules and understand the exact reasons for execution halts.
    *   *UI Implications*: Action buttons automatically disable, and red HSL banners display the blocked policy clause alongside waiver request fields.
    *   *Failure Mode*: Silently failing an action or displaying a generic "Error 500" code without explaining the rule violation.
*   **Immutable Traceability**: Every outcome, artifact, and dollar spent must trace back to the originating requirement through visible data provenance paths.
    *   *Why it matters*: Simplifies enterprise audits (SOC2 compliance) and validates the value realization ledger.
    *   *UI Implications*: Clicking on an outcome or value metric opens a slide-over panel displaying formulas and Marquez lineage trees.
    *   *Failure Mode*: Presenting ROI data without links to primary execution evidence or token logs.

## Human-AI Experience Principles
*   **Dynamic Autonomy Gates**: The interface must adjust active control displays based on the agent's autonomy level (L0-L4) and trust score.
    *   *Why it matters*: Reduces approval fatigue on low-risk tasks while forcing strict human sign-off on irreversible actions.
    *   *UI Implications*: L4 agents display simple status pills; L2/L3 agents render task consoles with confirmation prompts ("Authorize Tool Execution").
    *   *Failure Mode*: Allowing AI agents to commit code or adjust budgets without human validation.
*   **Explainable Re-Planning**: When an active workflow DAG halts or fails, the interface must detail the failure root cause and present simulation-backed alternative paths.
    *   *Why it matters*: Prevents SRE abandonment and keeps operators in control during API timeouts or resource blocks.
    *   *UI Implications*: Re-planning cards display a side-by-side comparison of Plan A (failed) vs. Plan B (suggested), showing the cost and time variance.
    *   *Failure Mode*: Silently changing workflow execution paths behind the scenes without user notification.

## Governance and Trust Design Principles
*   **Separation of Duties (SoD)**: The interface must separate the actor proposing an action from the approver of that action.
    *   *Why it matters*: Prevents fraudulent authorizations and complies with financial controls.
    *   *UI Implications*: If `user_id == objective_owner`, the "Approve Override" button is hidden.
    *   *Failure Mode*: Allowing the same user account to request and approve a budget override.
*   **Calculated Trust**: Trust must be computed continuously and displayed as a system metric, never assigned manually.
    *   *Why it matters*: Prevents operator bias and enforces agent accountability.
    *   *UI Implications*: Agent cards display trust ratings (0.00-1.00) based on historical accuracy and compliance metrics.
    *   *Failure Mode*: Allowing administrators to override or hardcode trust ratings.

## Enterprise Accessibility Principles
*   **Keyboard Operability (WCAG 2.1 AA)**: Every interactive element, including dynamic graph nodes and layout drawers, must be keyboard-accessible.
    *   *Why it matters*: Ensures compliance and increases SRE operational speed.
    *   *UI Implications*: Focusable elements display a clear outline (`outline: 2px solid #818cf8` with offsets).
    *   *Failure Mode*: Visual Neo4j node graphs that can only be navigated using a mouse.
*   **Multi-Modal Status Indicators**: Status indicators must not rely on color alone to communicate system state.
    *   *Why it matters*: Prevents information loss for colorblind or low-vision users.
    *   *UI Implications*: Badges combine HSL color tokens with unique symbols (e.g., checkmark, warning icon, error cross).
    *   *Failure Mode*: Using only red or green text on dark slate backgrounds to show system health.

## Design Philosophy Gaps or Unknowns
*   **Agent Council consensus UX**: The visual interface and collaboration patterns for agent councils (resolving conflicts or design choices) are undocumented.

---

# 2. Visual Language

## Visual Character
*   **Governance-Heavy Slate Glassmorphism** (Recommended pattern): UAWOS implements a premium, high-density dark UI to support continuous, low-fatigue monitoring. 
*   **Materiality**: The interface uses a dark slate base (`#080a10`) with semi-transparent cards (`rgba(18, 22, 35, 0.5)` with `backdrop-filter: blur(12px)`) and thin borders (`rgba(255, 255, 255, 0.06)`) to establish visual depth.
*   **Typography Accent**: Uses `'Outfit'` for KPIs, metric values, and primary headers to create a precise appearance, while `'Inter'` handles data-heavy tables and body text to maximize readability.

## Information Density Strategy
*   **High-Density Grid Layouts**: Dashboard, Delivery Traceability, and Governance views use high-density, low-padding CSS Grid layouts to fit maximum operational data on screen.
*   **Progressive Disclosure**: Detailed OPA Rego blocks, Cypher query inputs, and Marquez tracing logs are hidden by default, accessible only via slide-out drawers or expand triggers.
*   **Monospace Metadata**: Technical parameters, token logs, container names, and UUIDs are formatted in monospace fonts (`SFMono-Regular`, `Courier New`) to separate system data from natural language strings.

## Hierarchy Strategy
*   **Level 1: Strategic Intent**: Portfolio, Objectives, and Value outcomes. Rendered with large Outfit headers and circular progress meters.
*   **Level 2: Plan Candidates**: Simulations and risk analyses. Rendered in a side-by-side, comparative card grid.
*   **Level 3: Execution**: Workflow DAGs, active tasks, and sandboxed consoles. Rendered as interactive flow nodes and console outputs.
*   **Level 4: Traceability & Audit**: Marquez logs, Postgres ledger tables, and OPA policy Rego rule bodies. Rendered in monospace code blocks and timeline lists.

## Status and Risk Signaling
*   **HSL Signaling Rules**:
    *   *Healthy / Approved*: `hsl(142, 70%, 45%)` (Green).
    *   *Warning / Exception Requested*: `hsl(45, 90%, 50%)` (Yellow).
    *   *Blocked / Compliance Risk*: `hsl(0, 85%, 50%)` (Red | Includes an infinite CSS pulse/flash animation).
    *   *Offline / Inactive*: `hsl(215, 15%, 50%)` (Grey).
*   **Overlay Alerts**: Flashing red borders and active blocker cards render at the top of the Operational Command Center for critical failures (e.g., GPLv3 license warnings).

## Explainability and Auditability Cues
*   **Evidence Drawer Triggers**: Interactive outcome metrics contain inline link icons that open drawers displaying evidence hashes and transaction logs.
*   **Lineage Breadcrumbs**: Artifact cards display horizontal tree traces mapping the file back to the compiling task, parent workflow, plan, and requirement source.
*   **Decision Chips**: Planning cards display small, expandable chips detailing the Planner agent's reasoning.

## Motion and Interaction Tone
*   **Functional Transitions**: Motion must serve clarity, not decoration. Transitions use fast, linear-ease curves (150ms-200ms) for drawer slides and modal reveals.
*   **Pulsing Live Dot**: A single `.live-dot` component uses an infinite scale pulse (`transform: scale(1.1)`) at 2-second intervals to verify active connection to the backend BFF.

## Visual Language Gaps or Unknowns
*   The exact branding guidelines, logo assets, and corporate color schemes are not verified.

---

# 3. Design Tokens

## Token Strategy
*   **Standard CSS Custom Properties**: Design tokens are implemented as standard CSS variables declared in a `:root` scope to enable light/dark theme toggles.
*   **Semantic Token Naming**: Tokens map to functional roles (e.g., `--color-status-error`) rather than color hues.

## Color System
*   **Verified HSL Semantic Status Tokens**:
    ```css
    :root {
      --color-status-success: hsl(142, 70%, 45%);
      --color-status-warning: hsl(45, 90%, 50%);
      --color-status-error: hsl(0, 85%, 50%);
      --color-status-offline: hsl(215, 15%, 50%);
      --color-bg-base: #080a10;
      --color-bg-card: rgba(18, 22, 35, 0.5);
      --color-border-glass: rgba(255, 255, 255, 0.06);
    }
    ```
*   **Inferred Semantic Tokens**:
    *   *Text Primary*: `rgba(255, 255, 255, 0.95)` (High contrast readability).
    *   *Text Secondary*: `rgba(255, 255, 255, 0.60)` (Metadata, secondary headers).
    *   *Primary Action / Focus*: `#818cf8` (Indigo-400 | contrast ratio of 4.5:1).
    *   *Governance / Compliance*: `#10b981` (Emerald | OPA approved elements).
    *   *Audit / Lineage Highlight*: `#a78bfa` (Purple-400 | Marquez trace elements).

## Typography System
*   **Primary Fonts (Verified)**:
    *   Body/Tables/Lists: `'Inter', sans-serif`
    *   Headers/Title blocks/KPI metrics: `'Outfit', sans-serif`
*   **Monospace Font**: `'SFMono-Regular', Consolas, Monaco, monospace` (For logs, hashes, Rego rules, and Cypher inputs).
*   **Font Weights**:
    *   Regular: `400`
    *   Medium: `500`
    *   Bold: `700`
*   **Size Hierarchy (Recommended)**:
    *   `--font-size-xs`: `0.75rem` (12px | Metadata, inline hashes).
    *   `--font-size-sm`: `0.875rem` (14px | Table contents, body strings).
    *   `--font-size-base`: `1rem` (16px | Section descriptions, input labels).
    *   `--font-size-lg`: `1.25rem` (20px | Card headers).
    *   `--font-size-xl`: `1.75rem` (28px | Page titles).
    *   `--font-size-display`: `2.5rem` (40px | KPI value metrics).

## Elevation System
*   **Verified Glassmorphism Layers**:
    *   *Layer 0 (Base)*: `--color-bg-base` (`#080a10`).
    *   *Layer 1 (Card)*: `--color-bg-card` with `backdrop-filter: blur(12px)`.
    *   *Layer 2 (Drawer/Modal)*: `rgba(25, 30, 48, 0.85)` with `backdrop-filter: blur(24px)`.
*   **Shadows**:
    *   *Shadow Flat*: `0 4px 6px -1px rgba(0, 0, 0, 0.1)`.
    *   *Shadow Raised (Modal)*: `0 20px 25px -5px rgba(0, 0, 0, 0.3)`.

## Radius System
*   `--radius-sm`: `4px` (Inputs, status pills, small buttons).
*   `--radius-md`: `8px` (Standard buttons, workflow nodes).
*   `--radius-lg`: `12px` (Glass cards, charts, modals).

## Spacing System
*   `--spacing-2xs`: `0.25rem` (4px).
*   `--spacing-xs`: `0.5rem` (8px).
*   `--spacing-sm`: `0.75rem` (12px).
*   `--spacing-md`: `1rem` (16px).
*   `--spacing-lg`: `1.5rem` (24px).
*   `--spacing-xl`: `2rem` (32px).

## Motion System
*   `--motion-duration-fast`: `150ms`.
*   `--motion-duration-normal`: `250ms`.
*   `--motion-curve-linear`: `cubic-bezier(0, 0, 1, 1)`.
*   `--motion-curve-ease-out`: `cubic-bezier(0.16, 1, 0.3, 1)`.

## Grid System
*   **Dashboard Layout**: 12-column CSS grid with a standard gap of `--spacing-lg`.
*   **Workspace Columns**: Split-screen view mapping static controls (left panel, 4 columns) to dynamic logs (right panel, 8 columns).

## Breakpoints
*   `--breakpoint-md`: `768px` (Tablet layouts).
*   `--breakpoint-lg`: `1024px` (Desktop layouts).
*   `--breakpoint-xl`: `1440px` (Dense Command Center monitors).

## Data Visualization Token Rules
*   Colors used in charts must match semantic tokens (e.g., actual spent vs. forecast spent curves must map to red and grey tokens respectively).
*   Aria-labels must programmatically announce SVG chart labels.

## Token Governance Rules
*   Any new design token must undergo Strategy Council and Architecture Council review before modification.
*   Token overrides inside custom packs (Domain, Industry, Organization) cannot modify core HSL status indicators.

## Token Gaps or Unknowns
*   Dark-to-Light theme color maps are undefined; tokens currently support dark-mode execution environments only.

---

# 4. Component Library

## Foundations
*   **Why Needed**: Establishes the core visual token variables and HTML reset rules.
*   **Use Cases**: Base page structures, grid spacing configurations.
*   **Accessibility**: Implements the standard WCAG AA focus rings.
*   **Governance**: Centralizes style imports, preventing inline overrides.

## Inputs and Forms
*   **Why Needed**: Gathers user input for requirement studio, exception details, and budget parameters.
*   **Use Cases**: Pasting PRDs, inputting waiver overrides, adjusting budget ceilings.
*   **Accessibility**: Labels map explicitly to inputs via `for` attributes; inputs implement aria-describedby for errors.
*   **Governance**: Prevents execution of empty or invalid fields at the client level.

## Navigation
*   **Why Needed**: Switches between views while maintaining active context.
*   **Use Cases**: Sidebars, layout headers, deep link mappings.
*   **Accessibility**: Implements landmark wrappers (`<nav>`).
*   **Governance**: Access-denied states hide navigation paths based on OpenFGA constraints.

## Data Display
*   **Why Needed**: Renders dense database ledgers, parameters, and audit lists.
*   **Use Cases**: Traceability tables, active blocker lists, Postgres audit logs.
*   **Accessibility**: Tables must use semantic header tags (`<th>`) and scope designations.
*   **Governance**: Audit lists are read-only; no inline editing is allowed.

## Workflow and Process
*   **Why Needed**: Coordinates human-agent loops and execution task states.
*   **Use Cases**: LangGraph DAG visualizers, re-planning wizards.
*   **Accessibility**: Keyboard focus allows operators to select and query individual task nodes.
*   **Governance**: Visualizes dynamic autonomy limits.

## Governance and Compliance
*   **Why Needed**: Visualizes and edits access boundaries, Rego policies, and exception waivers.
*   **Use Cases**: OPA policy lists, OpenFGA visualizers.
*   **Accessibility**: Textareas for Rego rules implement syntax checking and error readouts.
*   **Governance**: Sovereign module control.

## Human-AI Collaboration
*   **Why Needed**: Interface checkpoints for agent prompts, critiques, and reviews.
*   **Use Cases**: Ingestion Studio critique cards, verification consoles.
*   **Accessibility**: Monospace terminal displays must support high contrast text.
*   **Governance**: Enforces Law 11 (Action verification).

## Feedback and System States
*   **Why Needed**: Updates operators on service health, connections, and progress.
*   **Use Cases**: strict health progress rings, connection dots, warning cards.
*   **Accessibility**: Loading skeleton states announce status text.
*   **Governance**: Surfaces loop alerts.

## Layout and Containers
*   **Why Needed**: Shell structures that isolate workspaces.
*   **Use Cases**: Glass cards, slide-over panels, modals.
*   **Accessibility**: Modals trap focus and close on `Esc` keypress.
*   **Governance**: Separation of duties boundaries.

## Accessibility Requirements Across Components
*   Focus targets must be at least 44x44px.
*   All active controls must contain text or explicit aria-label parameters.

---

# 5. Component Specifications

## Buttons
*   **Verification Status**: Verified.
*   **Purpose**: Trigger actions or state changes.
*   **Primary Use Cases**: Plan selection, budget approval, waiver overrides.
*   **Variants**: Primary (solid Indigo), Secondary (glass bordered), Destructive (solid HSL Red), Disabled.
*   **States**: Default, Hover (subtle border highlight), Focus (Indigo outline), Active (pressed scale 0.98), Disabled (grey border, cursor not-allowed).
*   **Density**: Standard (`padding: 12px 24px`), Dense (`padding: 8px 16px` for tables).
*   **Accessibility**: Target size `>44px`. Focus states trap focus.
*   **Interaction Behaviors**: Transitions occur within `--motion-duration-fast`.
*   **Governance and Trust**: If an action violates OPA check on load, the button transitions to Disabled with tooltip explanation.
*   **Explainability**: Tooltips display exact FGA or OPA rule that blocked the action.
*   **Failure States**: Displays inline spinner during REST dispatch.
*   **Anti-Patterns**: Bypassing OPA limits using un-gated buttons.

## Inputs
*   **Verification Status**: Verified.
*   **Purpose**: Ingest natural text or budget integers.
*   **Primary Use Cases**: Paste requirements, write exception justifications.
*   **Variants**: Text Area (for PRDs), Text Input (for fields), Number Input (for budgets).
*   **States**: Default, Hover, Focus (Indigo outline), Error (HSL Red border), Disabled.
*   **Density**: Standard (`font-size-sm`).
*   **Accessibility**: Aria-describedby links to error descriptions.
*   **Interaction Behaviors**: Real-time validation occurs on focus-out.
*   **Governance and Trust**: Budget inputs block negative numbers.
*   **Explainability**: Validation alerts display exact validation rule violated.
*   **Failure States**: Displays red validation banner on error.
*   **Anti-Patterns**: Allowing budget input submission without client-side type checks.

## Tables
*   **Verification Status**: Verified.
*   **Purpose**: Displays dense operational parameters.
*   **Primary Use Cases**: Traceability tables, Postgres audit log timelines.
*   **Variants**: Standard table, Dense table.
*   **States**: Default, Hover row state.
*   **Density**: Dense row layouts (`padding: 8px`).
*   **Accessibility**: Navigable by arrow keys, scopes defined on headers.
*   **Interaction Behaviors**: Clicking header toggles sort keys.
*   **Governance and Trust**: Postgres audit log cells are read-only and un-editable.
*   **Explainability**: Cells contain provenance tags linking to raw requirement segments.
*   **Failure States**: Empty state renders a card: "No records found."
*   **Anti-Patterns**: Standard database grid inline edits without Postgres audit logging.

## Data Grids
*   **Verification Status**: Verified.
*   **Purpose**: Multi-column dashboard summaries.
*   **Primary Use Cases**: Agent registries, Active Blocker lists.
*   **Variants**: Grid of cards.
*   **States**: Default, hover (border shine).
*   **Density**: 12-column layouts.
*   **Accessibility**: Tab index targets individual grid items.
*   **Interaction Behaviors**: Responsive reorganization based on breakpoints.
*   **Governance and Trust**: Cards display security scan status.
*   **Explainability**: Displays trust scores.
*   **Failure States**: Loading skeleton cards map grid footprint.
*   **Anti-Patterns**: Dynamic grids that shift content dynamically without layout warnings.

## Cards
*   **Verification Status**: Verified.
*   **Purpose**: Context container.
*   **Primary Use Cases**: Operational health display, active blocker, plan candidate.
*   **Variants**: Glass Card (Standard), Highlight Card (OPA blocked).
*   **States**: Default, Hover (border highlight & shadow rise).
*   **Density**: Standard `--spacing-md` padding.
*   **Accessibility**: Trapped navigation anchors.
*   **Interaction Behaviors**: Expands on click.
*   **Governance and Trust**: Highlight cards render HSL status borders.
*   **Explainability**: Detail panel explains contains data provenance.
*   **Failure States**: Empty states render grey placeholder cards.
*   **Anti-Patterns**: Using non-glass cards that violate the slate glassmorphic token rules.

## Modals
*   **Verification Status**: Verified.
*   **Purpose**: Focus user attention on critical approvals.
*   **Primary Use Cases**: HITL confirmations, budget overrides.
*   **Variants**: Standard Modal, Alert Modal.
*   **States**: Reveal, Close.
*   **Density**: Spacious padding (`--spacing-lg`).
*   **Accessibility**: Focus trap, closes on `Esc` key, focus returns to trigger element.
*   **Interaction Behaviors**: Slides down from top with `--motion-duration-normal` ease-out.
*   **Governance and Trust**: Modals prevent background interaction until closed.
*   **Explainability**: Display side-by-side parameter diffs.
*   **Failure States**: Display error banner inside header if action fails.
*   **Anti-Patterns**: Modals that do not trap focus.

## Drawers
*   **Verification Status**: Verified.
*   **Purpose**: Slide-over context panel for progressive disclosure.
*   **Primary Use Cases**: Evidence tracing, Marquez lineage logs review.
*   **Variants**: Right-side drawer.
*   **States**: Open, Closed.
*   **Density**: Standard width (33vw).
*   **Accessibility**: Screen readers announce drawer opening.
*   **Interaction Behaviors**: Slides out from right boundary.
*   **Governance and Trust**: Allows review without losing active workspace page state.
*   **Explainability**: High density display of formulas and raw text links.
*   **Failure States**: Displays connection error if API retrieval fails.
*   **Anti-Patterns**: Drawers that overlap critical command center status indicators.

## Trees
*   **Verification Status**: Verified.
*   **Purpose**: Visualizes file directory hierarchies.
*   **Primary Use Cases**: Front-end module directories (`apps/web/`).
*   **Variants**: Collapsible nested list.
*   **States**: Expanded, Collapsed.
*   **Density**: Minimal padding (`padding-left: 12px`).
*   **Accessibility**: Navigable via up/down arrows.
*   **Interaction Behaviors**: Clicking folder icon toggles collapse.
*   **Governance and Trust**: Identifies sandboxed folders (Marker) with border outlines.
*   **Explainability**: None.
*   **Failure States**: Empty folders render grey text placeholders.
*   **Anti-Patterns**: Dynamic tree updates that reset collapse states.

## Graphs
*   **Verification Status**: Verified.
*   **Purpose**: Visualizes node-link relationships.
*   **Primary Use Cases**: Objective dependency graphs, OpenFGA tuple mappings, OpenLineage trace flows.
*   **Variants**: Interactive Canvas.
*   **States**: Zoom, Pan, Select Node.
*   **Density**: Canvas fills active container.
*   **Accessibility**: Focus outline maps to active node. Nodes navigable via keyboard.
*   **Interaction Behaviors**: Dragging pan controls, clicking node details slide-over.
*   **Governance and Trust**: Identifies cycle conflicts (blocked path).
*   **Explainability**: Nodes link to audit logs.
*   **Failure States**: Canvas failure renders warning card: "Graph load failed."
*   **Anti-Patterns**: Canvas graph interfaces that lack mouse-free pan/zoom controls.

## Timelines
*   **Verification Status**: Verified.
*   **Purpose**: Displays sequential milestones.
*   **Primary Use Cases**: Roadmaps (`RD-01` to `RD-04`).
*   **Variants**: Horizontal roadmaps.
*   **States**: Default, Hover node.
*   **Density**: High-density horizontal track layout.
*   **Accessibility**: Interactive milestones are focusable.
*   **Interaction Behaviors**: Drag-and-drop to re-sequence.
*   **Governance and Trust**: Prevents manual re-sequencing of blocked objectives.
*   **Explainability**: Milestones display parent objectives.
*   **Failure States**: Displays alert when milestones overlap.
*   **Anti-Patterns**: Timelines that allow drag changes without OPA validation.

## Dashboards
*   **Verification Status**: Verified.
*   **Purpose**: Central hub for system monitoring.
*   **Primary Use Cases**: Operational Command Center, Governance Console.
*   **Variants**: Multi-column grids.
*   **States**: Default, Alert State.
*   **Density**: High-density layouts.
*   **Accessibility**: Global landmark regions defined.
*   **Interaction Behaviors**: Real-time widgets update via polling.
*   **Governance and Trust**: Displays strict health score indicators.
*   **Explainability**: Tooltips display metric definitions.
*   **Failure States**: Displays central offline connection banner.
*   **Anti-Patterns**: Dashboards that lack active blocker notifications.

## KPI Widgets
*   **Verification Status**: Verified.
*   **Purpose**: Displays high-level status metrics.
*   **Primary Use Cases**: strict health, policy compliance, portfolio spent.
*   **Variants**: Circular progress rings, stat blocks.
*   **States**: Normal, Warning (Yellow), Alert (Red).
*   **Density**: Large display typography.
*   **Accessibility**: Text-equivalent labels accompany all visual elements.
*   **Interaction Behaviors**: Clicking widget opens related drawer.
*   **Governance and Trust**: strict health calculation enforces Law 1.
*   **Explainability**: Displays formula.
*   **Failure States**: Renders `--` on connection failure.
*   **Anti-Patterns**: Hiding calculation inputs from executive users.

## Agent Panels
*   **Verification Status**: Verified.
*   **Purpose**: Displays agent capabilities and trust metrics.
*   **Primary Use Cases**: Agent Registry cards.
*   **Variants**: Detailed panel.
*   **States**: Active, Suspended (trust < 70).
*   **Density**: Standard grid card.
*   **Accessibility**: Decommission buttons are accessible.
*   **Interaction Behaviors**: Triggering manual override to suspend agent.
*   **Governance and Trust**: Automatically handles trust drop escalations.
*   **Explainability**: Displays performance history.
*   **Failure States**: Displays loop warning indicators.
*   **Anti-Patterns**: Modifying agent trust scores without auditable logs.

## Workflow Visualizers
*   **Verification Status**: Verified.
*   **Purpose**: Tracks stateful task DAG execution.
*   **Primary Use Cases**: LangGraph DAG progress.
*   **Variants**: Flowchart canvas.
*   **States**: Pending node, Executing node, Completed node, Blocked node (HITL).
*   **Density**: High density flow graph.
*   **Accessibility**: Aria-live zones announce node state changes.
*   **Interaction Behaviors**: Clicking active node opens terminal log logs.
*   **Governance and Trust**: Pauses execution at HITL gates.
*   **Explainability**: Lines show execution lineage.
*   **Failure States**: Node outlines turn flashing Red on task failure.
*   **Anti-Patterns**: Resuming workflows without valid human validation.

## Audit Views
*   **Verification Status**: Verified.
*   **Purpose**: Displays Marquez lineage traces and Postgres audit logs.
*   **Primary Users**: Compliance Officer.
*   **Core Screens**: Marquez logs explorer, audit ledger screen.
*   **Governance Implications**: Sovereign module control.
*   **Cross-Links**: Governance Center, Knowledge Graph Explorer.
*   **Anti-Patterns**: Modifying database records.

---

# 6. Design System Governance

## Component Versioning
*   The design system is versioned using Semantic Versioning (`Major.Minor.Patch`).
*   Component version changes are logged to the central changelog file.

## Contribution Rules
*   New components must satisfy three criteria before publication:
    1.  **Architecture Council Approval**: API and dependency audit.
    2.  **Governance Council Approval**: compliance and access audit.
    3.  **Accessibility Verification**: WCAG 2.1 AA validation check.

## Accessibility Gates
*   All design system builds must compile with zero accessibility errors using axe-core checking.

## Usage Rules
*   Action buttons triggering budget overrides or exception approvals must use the specific `.btn-destructive` or `.btn-primary` tokens; no custom styling overrides are permitted on execution controls.

## Enterprise Consistency Controls
*   Components import semantic CSS variables exclusively; local styling files are scanned for hardcoded colors or spacing parameters during CI/CD pipelines.

---

# 7. Validation Review

## UX Review
*   *Strongly Supported*: Slate glassmorphism base tokens, Inter/Outfit typography, strict vs. weighted health progress indicators, and active blocker cards are well-supported.
*   *Design Decisions Needed*: Exact icons library and visual representation rules for agent councils consensus sequences need design definition.
*   *Clarification Required*: Standard visual designs for displaying critique text changes.

## Accessibility Review
*   *Strongly Supported*: Contrast requirements and HSL color indicators accompanied by text labels are supported.
*   *Design Decisions Needed*: Keyboard routing rules when traversing complex Neo4j node links.
*   *Clarification Required*: Screen reader text templates for circular SVG progress rings.

## Governance Review
*   *Strongly Supported*: OPA and OpenFGA policy block signals, SoD guards, and audit trail integrations are verified.
*   *Design Decisions Needed*: Visual builders for OPA policies to avoid writing raw Rego text.
*   *Clarification Required*: Default policy templates for enterprise compliance.

## Scalability Review
*   *Strongly Supported*: Federated database structures (Postgres, Qdrant, Neo4j) are supported.
*   *Design Decisions Needed*: Concurrency alerts for client browsers when database state writes encounter file-locks.
*   *Clarification Required*: Database migration roadmap details.

## Implementation Readiness Review
*   *Strongly Supported*: BFF REST endpoints and docker network configurations are active.
*   *Design Decisions Needed*: Central tokens css file compilation pipeline.
*   *Clarification Required*: Heuristic fallback parser configurations for local LLM gateways.

---

# 8. Assumptions
*   We assume that the client application communicates with the backend HTTP server over port 8099 with connection timeouts set to 30 seconds.
*   We assume that the user's browser is modern and supports ES6 module imports and CSS custom variables natively.
*   We assume that PII masking heuristics in the DTASE engine occur on the client or in a secure gateway before sending data to Ollama.
*   We assume that the PostgreSQL audit logs and Marquez lineage records are read-only and cannot be modified by any user role.
*   We assume the C4 topology viewer renders static configuration maps generated from the system’s Docker compose layout.
