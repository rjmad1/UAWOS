# Universal AI Workforce Operating System (UAWOS)
# AI-Native Experience Design Specification (PHASE 10)

> **Workspace Context:** `rjmad1/UAWOS`  
> **Standards References:** UCA v1.0, WAAS v1.0, OPES v1.0, CIAS v1.0, GCF v1.0, PMCMS v1.0, VRMS v1.0, PRTCS v1.0, PVRS v1.0, RDMS v1.0

---

# 1. AI-Native Experience Overview

## Human + Agent Operating Model
UAWOS represents a governed, human-in-the-loop AI workforce operating model. Humans and AI agents coexist as unified workforce entities under a single system of execution. 
*   **Humans** remain accountable, providing strategic direction, budget limits, exception overrides, and validation checkpoints.
*   **AI Agents** execute the operational planning, orchestration, tool operations, and compliance checks under governance.

This objective-centric model shifts the user experience from manual task and ticket management to high-level objective tracking, where plans, workflows, and task execution logs are synthesized and run automatically.

---

## Core Experience Principles
*   **Trust Through Explainability**: Every recommendation, planning decision, or status shift must render clear, evidence-grounded logic.
*   **Governance Supremacy**: Agent autonomy is governed; compliance status must be visible in real-time, preventing opaque execution.
*   **Actionable Lineage**: Clickable UI anchors must trace outcomes back to requirements.

---

## Verified AI Interaction Constraints
*   **PII Masking**: Ingestion data must mask PII names and entities before processing by Ollama.
*   **GPLv3 Isolation**: Direct package imports of copyleft dependencies (Marker) are blocked; document parsing runs in sandboxed environments.
*   **OPA Policy Validation**: Every execution step pre-checks OPA Rego rules.
*   **FGA Gating**: separation of duties (owner != approver) is validated.
*   **Automatic Agent Suspension**: SREs can manually suspend agents; trust score drops below 70 trigger automatic suspension.

---

## AI-Native Experience Gaps or Unknowns
*   **Agent Council UX**: Visual interfaces showing multi-agent council debates or consensus decisions are undocumented.

---

# 2. Human ↔ Agent Collaboration

## Collaboration Model
Collaboration operates under four modes defined in the WAAS standard: Human-Led, Agent-Assisted, Agent-Led, and Governed Autonomous.

---

## Roles and Responsibilities
*   **PM $\leftrightarrow$ Planner / Challenger / Simulation Agent**: Ingests requirements, simulates plans, and prioritizes roadmaps. PM approves plan and budget.
*   **SRE $\leftrightarrow$ Resource Manager / Governor Agent**: Monitors capacity and service health. SRE overrides and suspends agents.
*   **Developer $\leftrightarrow$ Executor / Reviewer Agent**: Synthesizes artifacts, reviews code, and approves sandboxed tool executions (HITL).
*   **Compliance Officer $\leftrightarrow$ Governor / Knowledge Manager Agent**: Audits policies, reviews waivers, and traces Marquez lineage.

---

## Shared Workspace Patterns
*   **Critique split-screen view**: Side-by-side display mapping raw inputs on the left to Challenger critiques on the right.
*   **Stateful DAG Visualizer**: Flowchart canvas mapping active LangGraph workflow nodes, highlights node status.

---

## Hand-off and Escalation Rules
*   **HITL Gates**: Irreversible actions (git commits, payments, parameter overrides) block workflow progression, transition node to pending, and alert the human.
*   **Task Failure**: Execution timeouts trigger replanning requests, presenting Plan B options to the PM.

---

## Trust and Autonomy Visibility
*   Task panels display active autonomy level badges (L0-L4) alongside the agent's trust score.

---

## Failure and Recovery Patterns
*   Agent loops or budget breaches trigger a visual blocker card, freeze the DAG, and display a "Resolve Blocker" button linking to exception waiver requests.

---

# 3. Agent Transparency

## What Users Must See
Before authorizing an agent, users must see its registered Agent Class, status badge (Active/Suspended), active trust score (0.00-1.00), and specific capabilities (e.g., `git_commit`, `code_execution`).

---

## Agent Identity and Role Surfaces
Agent profiles display in the Agent Directory, using standard class taxonomy designations (Planner, Orchestrator, Executor, Reviewer, Governor, Learner, Knowledge Manager).

---

## Status, Capability, and Scope Visibility
Cards map agent status dynamically using HSL status pills. Clicking an agent card opens a drawer detailing its assigned tools, allowed OPA namespaces, and historical execution success rates.

---

## Cost and Resource Transparency
*   **Token Velocity Chart**: Real-time line graph plotting cumulative token cost against percentage of objective outcomes achieved.
*   **Capacity Indicators**: Utilizations timelines display active compute usage.

---

## Evidence and Provenance Visibility
Audit logs display the exact agent ID and model gateway (e.g., TinyLlama via LiteLLM) that executed every task, linking to Marquez OpenLineage logs.

---

# 4. Explainability

## Decision Explainability Model
Explainability is action-oriented. Clicking any automated decision renders a slide-over panel displaying the inputs, OPA policy evaluation logs, and verifying evidence hashes.

---

## Plan and Recommendation Explainability
Plan candidate cards display Challenger Agent contrarian reports, showing cost, time, and success probability variables.

---

## Policy Decision Explainability
When OPA blocks an action, the UI renders the OPA status JSON showing the violating Rego rule block.

---

## Outcome and Value Explainability
Outcome metric cards contain inline link icons that open drawers displaying calculation formulas and Marquez lineage trees.

---

## Contrarian and Challenger Views
Planning interfaces contain "Challenger Review" tabs displaying contrarian risk calculations and assumption lists.

---

# 5. Governance Visibility

## Policy-State Awareness
Every plan, workflow, and action displays its current compliance state (Green: Approved, Red: Blocked).

---

## Approval-State Awareness
Approval views display the approval state, signature hashes, and the FGA relation mappings.

---

## Exception and Waiver Visibility
Active exception requests (EXC-xxx) display in a centralized queue showing justification texts, requestors, and waiver expiration dates.

---

## Auditability by Design
Postgres audit log tables are read-only and un-editable; Marquez lineage trees render data flows from requirements to commits.

---

## Separation-of-Duties Visibility
The system hides approval actions from the user if FGA checks return `owner == requestor`.

---

# 6. Approval Workflows

## Approval Types
*   **Plan Approval**: Triggered on plan selection. PM approves. Requires cost/duration forecast distributions.
*   **Budget Override**: Triggered on budget limit breach. Executive approves. Requires justification.
*   **Exception Waiver**: Triggered on OPA policy block. Executive approves. Requires signed signature token and justification.
*   **HITL Tool Execution**: Triggered on execution of irreversible tool command. Developer approves. Requires code diff.

---

## Human-in-the-Loop Patterns
HITL approvals trap focus and display confirmation prompts with side-by-side parameter comparisons.

---

## Approval UX States
Renders `submitted` $\rightarrow$ `under_review` $\rightarrow$ `approved` (generates signature hashes) / `rejected` (halts DAG).

---

## Delegation, Expiry, and Escalation Rules
*   Exceptions include a mandatory expiration date selector. Once expired, OPA automatically reinstates blocks.

---

## Governance Risks and Safeguards
Approval forms implement client-side type checking, preventing negative or empty values.

---

# 7. Risk Escalations

## Escalation Triggers
Escalations trigger on **Budget Limit Breached**, **Compliance Risk (GPLv3)**, **Low Agent Trust Score (<70)**, **Dependency Cycle Conflicts**, and **Component Database Failures**.

---

## Severity and Routing Model
*   *Critical (Red)*: GPLv3 warnings and DB failures. Routes to SRE Command Center.
*   *High (Yellow)*: Exception requests. Routes to Executive Waiver queue.
*   *Medium (Orange)*: Ingestion critiques. Routes to PM Studio.

---

## Escalation UX Patterns
Flashing red border alerts and active blocker cards render at the top of the Operational Command Center.

---

## Evidence Requirements
Escalation warnings display the diagnostic component, latencies, and error codes.

---

## Resolution Feedback Loops
Alerts include direct action links ("Execute Kill Switch", "Approve Waiver").

---

# 8. AI Recommendations

## Recommendation Surfaces
*   *Requirement Ingestion*: Critique checklists and completeness rankings.
*   *Planning*: Simulation-ranked candidate plans.
*   *Operations*: Capacity re-allocations and re-planning suggestions.

---

## Recommendation Confidence and Uncertainty
Simulation outputs display confidence bounds ($90\%$ intervals) and success probabilities.

---

## Acceptance, Rejection, and Revision Patterns
PMs can click "Approve and Dispatch", "Reject Plan", or edit parameters to run new simulations.

---

## Recommendation Traceability
Recommendations display the Challenger agent's analysis and link back to vector search origins.

---

## Misuse Risks and Safeguards
Restricts plan dispatch to verified requirements with completeness scores $>50\%$.

---

# 9. Human Overrides

## Override Scenarios
*   *Agent Suspension*: SRE clicks Kill Switch to stop executor container.
*   *Budget override*: Executive adjusts limit.
*   *Waiver approval*: Executive overrides policy block.

---

## Override Permissions
Restricted to Executive and SRE roles using FGA access tuples.

---

## Justification Requirements
Waivers and overrides require an input form for justification and an expiration date.

---

## Audit and Reversal Requirements
All manual overrides write an audit trail to PostgreSQL. Reversals require manual override resets.

---

## UX Friction Rules for High-Risk Actions
Destructive buttons (Kill Switch, Policy Waiver) render in HSL Red and require confirmation check box selections on modal prompts.

---

# 10. Simulation Review

## Simulation-to-Decision Experience
PM pastes requirement $\rightarrow$ DTASE parses $\rightarrow$ Simulation Agent runs Monte Carlo forecasts $\rightarrow$ PM compares candidate plans on card grids $\rightarrow$ PM approves plan and budget limit.

---

## Comparing Candidate Plans
Plan candidates display in side-by-side cards comparing cost, duration, and success probability metrics.

---

## Uncertainty Communication
Displays probability distributions using Monte Carlo scatter plots.

---

## Challenger Review Patterns
PMs click the "Challenger Analysis" tab inside plan cards to inspect contrarian risk evaluations.

---

## Approval and Commit Patterns
Confirming a plan generates the stateful DAG and dispatches the workflow.

---

# 11. Value Realization Tracking

## Value Visibility Model
Concentric progress gauges display realized outcomes and ROI metrics.

---

## Outcome Verification Patterns
Clicking ROI values opens slide-over drawers displaying evidence logs.

---

## Spend vs Value Transparency
Scatter plots compare forecast values against actual token costs.

---

## Objective Completion and Benefit Evidence
Complete objectives log realized outcomes, spend, and learning assets to the central database.

---

## Learning and Postmortem Integration
Completion states trigger the Learner Agent to extract postmortem records and update planning templates.

---

# 12. Validation Review

## UX Review
*   *Strongly Supported*: Critique split-screens, active blocker cards, and health ring animations are verified.
*   *Inferred*: Detailed layouts for the Challenger risk panels.
*   *Confirmation Required*: Icon libraries for agent classes.

## Accessibility Review
*   *Strongly Supported*: Contrast requirements and multi-modal status indicators are verified.
*   *Recommended*: Keyboard traversals on DAG canvases.
*   *Confirmation Required*: Screen-reader templates for health rings.

## Governance Review
*   *Strongly Supported*: SoD forms, OPA policy blocks, and OpenFGA tuples visualizers are verified.
*   *Recommended*: Local OPA pre-checks in controllers.
*   *Confirmation Required*: Standard templates for compliance rule versions.

## Scalability Review
*   *Strongly Supported*: Database isolation boundaries are verified.
*   *Recommended*: SessionStorage caching for SRE filter settings.
*   *Confirmation Required*: Relational database migration plans.

## Implementation Readiness Review
*   *Strongly Supported*: Backend REST APIs are functional and operational.
*   *Recommended*: Vite compilation and Playwright end-to-end testing stacks.
*   *Confirmation Required*: Shared CSS token file compilation pipelines.

---

# 13. Assumptions
*   We assume that the client application communicates with the backend HTTP server over port 8099 with connection timeouts set to 30 seconds.
*   We assume that the user's browser is modern and supports ES6 module imports and CSS custom variables natively.
*   We assume that PII masking heuristics in the DTASE engine occur on the client or in a secure gateway before sending data to Ollama.
*   We assume that the PostgreSQL audit logs and Marquez lineage records are read-only and cannot be modified by any user role.
*   We assume the C4 topology viewer renders static configuration maps generated from the system’s Docker compose layout.
