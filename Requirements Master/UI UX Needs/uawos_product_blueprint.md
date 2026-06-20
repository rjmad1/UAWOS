# Universal AI Workforce Operating System (UAWOS)
# Comprehensive Product Definition, UX Strategy, & Application Architecture Blueprint

> **Standards References:** UCA v1.0, WAAS v1.0, OPES v1.0, CIAS v1.0, GCF v1.0, PMCMS v1.0, VRMS v1.0, PRTCS v1.0, PVRS v1.0, RDMS v1.0, DTASE v1.0

---

# PART 1 — PRODUCT UNDERSTANDING (PHASE 1)

## 1. Executive Product Definition

### Product Vision
To establish a world where organizations operate through intent and outcomes rather than disconnected tools. UAWOS (Universal AI Workforce Operating System) transforms strategic intent into a unified, governed, and objective-centric execution fabric. It coordinates humans, AI agents, knowledge, resources, and compliance frameworks into a single organizational control plane, ensuring that every operational activity traces directly to measurable business value.

### Product Mission
Transform any organizational objective into measurable value through a unified, governed, and explainable human-AI workforce operating system, enabling enterprises to execute with speed, safety, and continuous learning.

### Product Positioning
*   **Category**: UAWOS creates a new software category: the **AI Workforce Operating System** (also defined as an *Objective Operating System* or *Autonomous Enterprise Operating System*). It acts as a **System of Execution** that sits above traditional systems of record, engagement, and intelligence.
*   **Problem Category**: Solves enterprise execution fragmentation (context loss across emails, chats, and documents), operational coordination overhead, and **agent sprawl** (the uncontrolled creation of autonomous agents without tracking, governance, or ROI metrics).
*   **Differentiator from Project Management**: Project management tools (e.g., Jira, Asana, Monday) manage task lists, tickets, and timelines. They track *outputs*, not *outcomes*. UAWOS is objective-centric; it decomposes goals, models outcomes, and orchestrates workforce entities dynamically without manual ticket creation.
*   **Differentiator from Workflow Automation**: Workflow automation systems (e.g., ServiceNow, RPA) automate rigid, static processes. They do not understand objectives, simulate plan trade-offs, or automatically replan when execution paths fail.
*   **Differentiator from Copilots/AI Assistants**: Assistants (e.g., Microsoft Copilot) provide conversational support to individual users. They do not own execution, run simulations, coordinate teams, or operate under stateless enterprise-wide governance.
*   **Differentiator from Agent Platforms/Sandboxes**: Agent platforms (e.g., LangChain ecosystem) focus on building individual agents. They lack an enterprise operating model, fine-grained relationship-based access control (ReBAC), stateless policy engines (OPA), and organizational learning repositories.

### Strategic Differentiators
1.  **Objective-Centric Abstraction**: All activities originate from an Objective. Users define *what* to achieve; the system generates, simulates, and executes the *how* (plans, workflows, and task DAGs).
2.  **Stateless Native Governance**: Policy enforcement (OPA/Rego) and relationship-based authorization (OpenFGA) are non-bypassable architectural invariants. Governance constraints supersede autonomous execution.
3.  **Federated Knowledge & Memory Graph**: Connects domain ontologies, document metadata, and historical outcomes across a federated architecture (relational, vector, and graph databases) to act as the Enterprise Digital Twin.
4.  **Value Realization Engine**: Tracks actual token, compute, and financial costs against original value hypotheses and live metrics to calculate real-time business ROI.
5.  **Organizational Learning System**: Captures postmortem insights and learning assets automatically, feeding them back into future plan simulations to reduce variance and improve execution.

### Value Proposition Hierarchy
*   **Enterprise / C-Suite Value**: Eliminates organizational coordination overhead, guarantees legal and compliance safety (e.g., copyleft license protection, budget breaches), and exposes live portfolio ROI.
*   **Portfolio / Program Management Value**: Automates the ingestion of unstructured requirements (PDFs, voice, notes), structures cycle-free dependency graphs, runs Monte Carlo forecasts to rank plans, and provides traceability from requirements to delivery.
*   **Operations & SRE Value**: Provides a centralized Operational Command Center to monitor system health, manage capacity, decommission runaway agents via kill switches, and resolve active blockers.
*   **Knowledge Worker & Agent Value**: Supplies context-rich task workspaces, automates execution through sandboxed tools, optimizes capability mapping via SkillOpt, and logs execution lineage automatically.

---

## 2. Product Capability Map

### Core Capabilities
*   **Objective Ingestion & Critique**:
    *   *Purpose*: Ingests unstructured inputs, masks PII, and runs multi-persona critiques to evaluate requirement completeness.
    *   *Primary Actor*: Product Manager, DTASE Engine.
    *   *Trigger*: PM uploads a PRD PDF or pastes unstructured text into the Requirement Studio.
    *   *Business Value*: Drastically reduces intake analysis time and flags missing success criteria before planning.
    *   *Dependencies*: DTASE Engine, LiteLLM/Ollama Gateway.
    *   *Governance Implications*: Validates Law 1 (No Objective without measurable Outcomes) and checks checklists.
    *   *Measurable Outcome*: Completeness Score (%), Readiness Score (%).
*   **Multi-Plan Simulation & Ranking**:
    *   *Purpose*: Generates multiple execution paths and runs Monte Carlo simulations (cost, duration, risk) to rank them.
    *   *Primary Actor*: Planner Agent, Simulation Agent, Product Manager.
    *   *Trigger*: Structured objective is published.
    *   *Business Value*: Enables data-driven selection of the optimal execution path based on cost-time trade-offs.
    *   *Dependencies*: Objective Ingestion, Simulation Engine.
    *   *Governance Implications*: Evaluates plan safety and prevents expensive execution loops.
    *   *Measurable Outcome*: Success Probability (%), Forecast Duration (days), Forecast Cost ($).
*   **Workforce Orchestration & DAG Execution**:
    *   *Purpose*: Dispatches approved plan segments into sequential Task DAGs and coordinates execution across human and agent entities.
    *   *Primary Actor*: Orchestrator Agent, Executor Agent, Lead Engineer, Developer.
    *   *Trigger*: PM approves plan and allocates budget.
    *   *Business Value*: Eliminates handoff friction and automates delivery while preserving human-in-the-loop safety.
    *   *Dependencies*: Planning Engine, LangGraph, SkillOpt.
    *   *Governance Implications*: Forces human sign-off for irreversible or high-risk actions.
    *   *Measurable Outcome*: Objective Success Rate (%), Cycle Time (days).

### Supporting Capabilities
*   **Skill Registry & Capacity Management**:
    *   *Purpose*: Manages agent/human skills, execution costs, and trust scores to optimize assignment.
    *   *Primary Actor*: Operations Leader, Resource Manager Agent.
    *   *Trigger*: Onboarding workforce entities or running capability optimization.
    *   *Business Value*: Ensures tasks are assigned to the most cost-effective and reliable workforce entities.
    *   *Dependencies*: SkillOpt Integration.
    *   *Governance Implications*: Blocks unauthorized entities from executing critical capabilities.
    *   *Measurable Outcome*: Workforce Utilization (%), Capability coverage count.
*   **Requirements Traceability**:
    *   *Purpose*: Generates an interactive traceability table mapping functional requirements to roadmap milestones, epics, and code.
    *   *Primary Actor*: Product Manager, Lead Engineer, Value Analyst Agent.
    *   *Trigger*: Viewing the Delivery or Roadmap tab.
    *   *Business Value*: Ensures complete alignment between original intent and final technical artifacts.
    *   *Dependencies*: Workflow Execution.
    *   *Governance Implications*: Validates Law 11 (No External Action without Governance Evaluation) and Law 10 (No Execution without Authorization).
    *   *Measurable Outcome*: Requirements Coverage (%), Traceability Correlation Score.

### Administrative Capabilities
*   **Agent Registry & Directory**:
    *   *Purpose*: Registers, monitors, suspends, or retires agents, tracking their runtime status and performance.
    *   *Primary Actor*: Operations Leader, SRE.
    *   *Trigger*: SRE monitors active agent loops or modifies trust scores.
    *   *Business Value*: Prevents compute budget waste by identifying and suspending runaway executors.
    *   *Dependencies*: Skill Registry.
    *   *Governance Implications*: Automatically suspends agents whose trust score drops below 70.
    *   *Measurable Outcome*: Active Agent Count, MTTR for agent loops.
*   **Identity & Access Registry (OpenFGA)**:
    *   *Purpose*: Manages fine-grained relationship-based access control (ReBAC) mapping roles to actions.
    *   *Primary Actor*: CEO, Compliance Officer.
    *   *Trigger*: Onboarding users or defining system roles.
    *   *Business Value*: Restricts high-risk actions to authorized personnel and prevents privilege escalation.
    *   *Dependencies*: CIAS Standard.
    *   *Governance Implications*: Enforces Separation of Duties (owner != approver).
    *   *Measurable Outcome*: Policy-compliant access logs (100%).

### Governance Capabilities
*   **Stateless Policy Evaluation (OPA)**:
    *   *Purpose*: Evaluates execution elements against Rego policies (license checks, token budgets, sandboxing).
    *   *Primary Actor*: Compliance Officer, Governor Agent.
    *   *Trigger*: Active workflow requests a tool execution or budget allocation.
    *   *Business Value*: Automatically blocks non-compliant actions (e.g., GPLv3 code import) before they incur cost or liability.
    *   *Dependencies*: Policy Registry, Open Policy Agent.
    *   *Governance Implications*: Highest control plane gate (governance supersedes execution).
    *   *Measurable Outcome*: Policy Compliance Rate (%), OPA Latency (ms).
*   **Exception Override & Risk Management**:
    *   *Purpose*: Manages policy exception waivers (EXC-xxx) and risk acceptances.
    *   *Primary Actor*: Executive (CEO), Compliance Officer.
    *   *Trigger*: OPA blocks execution and the system triggers an override request.
    *   *Business Value*: Restores blocked workflows safely with a documented, human-accountable audit trail.
    *   *Dependencies*: OPA Policy Engine, OpenFGA.
    *   *Governance Implications*: Mandates executive approval token signatures.
    *   *Measurable Outcome*: Pending exceptions count, waiver cycle time.
*   **Immutable Audit Logging**:
    *   *Purpose*: Appends transactional execution logs showing who did what, when, and why.
    *   *Primary Actor*: Compliance Officer, Audit Agent.
    *   *Trigger*: State transition, budget change, or policy evaluation.
    *   *Business Value*: Continuous compliance readiness (SOC2) and tamper-proof history.
    *   *Dependencies*: PostgreSQL.
    *   *Governance Implications*: Enforces absolute audibility and explainability.
    *   *Measurable Outcome*: Log completeness (100% trace of state modifications).

### Intelligence Capabilities
*   **Multimodal Domain Translation**:
    *   *Purpose*: Translates raw, conversational, and multimodal inputs into structured domain specifications and professional artifacts.
    *   *Primary Actor*: Product Manager, DTASE Engine.
    *   *Trigger*: Raw input ingested into Ingestion Studio.
    *   *Business Value*: Democratizes requirement writing, translating user intents into legal briefs, medical notes, or technical specs.
    *   *Dependencies*: LiteLLM, Ollama, Marker.
    *   *Governance Implications*: Enforces strict isolation of copyleft dependencies (Marker container sandbox on port 8000).
    *   *Measurable Outcome*: Translation Accuracy (%), Ingestion time.
*   **Organizational Learning Extraction**:
    *   *Purpose*: Compiles execution lessons learned to optimize future planning rules and capability scores.
    *   *Primary Actor*: Learner Agent, Product Manager.
    *   *Trigger*: Objective completes or fails.
    *   *Business Value*: Continuously refines Planning Engine templates and reduces forecast variance.
    *   *Dependencies*: Knowledge Graph, Value Realization.
    *   *Governance Implications*: Enforces Law 8 (No Learning without Governance).
    *   *Measurable Outcome*: Knowledge Reuse Rate (%), Planning variance reduction (%).
*   **Semantic Graph Search & Neo4j Explorer**:
    *   *Purpose*: Executes dense vector and graph queries across vector space and relational ontologies.
    *   *Primary Actor*: Product Manager, SRE, Knowledge Manager Agent.
    *   *Trigger*: Tracing historical context or querying knowledge assets.
    *   *Business Value*: Facilitates direct access to organizational memory, resolving duplicate effort.
    *   *Dependencies*: Qdrant, Neo4j.
    *   *Governance Implications*: Enforces Law 9 (No Knowledge without Provenance).
    *   *Measurable Outcome*: Query latency, search relevance.

### Capability-to-Business-Outcome Mapping

| Capability Name | Primary Target Metric | Criticality | Maturity Confidence |
| :--- | :--- | :--- | :--- |
| **Objective Ingestion & Critique** | Requirement completeness / Readiness score | Critical | Verified |
| **Multi-Plan Simulation & Ranking** | Planning and Forecast Accuracy / Success Probability | High | Verified |
| **Workforce Orchestration** | Objective Success Rate / Cycle Time reduction | Critical | Verified |
| **Skill Registry & Capacity** | Workforce Utilization Rate | Medium | Verified |
| **Requirements Traceability** | Requirements coverage (%) / Audit coverage | High | Verified |
| **Agent Registry & Directory** | Active loop suspension / Token cost control | Critical | Partially Verified |
| **Identity & Access Registry** | Zero unauthorized actions | High | Verified |
| **Stateless Policy Evaluation** | Governance Compliance Rate (100%) | Critical | Verified |
| **Exception Override & Risks** | Blocker resolution cycle time | High | Verified |
| **Immutable Audit Logging** | Tamper-proof log validation (SOC2 readiness) | Critical | Verified |
| **Multimodal Translation** | Time to compile strategic propositions | High | Verified |
| **Organizational Learning** | Knowledge reuse rate (%) / Planning variance reduction | Medium | Verified |
| **Semantic Graph Search** | Provenance mapping correlation / Context latency | Medium | Verified |

---

## 3. Domain Model

### Domain Entities
The domain model consists of 21 verified entities mapped to specific execution, governance, intelligence, value, resource, and workforce sub-systems.

### Entity Definitions

1.  **Objective**: The primary abstraction representing a defined strategic intent or goal. Primary Lifecycle: `draft` $\rightarrow$ `active` $\rightarrow$ `paused` $\rightarrow$ `completed` / `failed` / `cancelled` $\rightarrow$ `archived`. Key Attributes: `ObjectiveID` (UUID), `Title`, `Description`, `Priority` (Critical, High, Medium, Low), `OwnerID`, `HealthScore` (0.00-100.00), `Status`, `ActiveBudgetLimit`. Governance Relevance: Violations of Law 1 (No Objective without measurable Outcomes) deduct 20 points from the health score.
2.  **Portfolio**: A high-level strategic collection of objectives mapping to an organizational department or business unit. Key Attributes: `PortfolioID`, `Name`, `SponsorID`, `ActiveObjectivesLimit`, `ManagedValueCapacity` ($), `TotalAllocatedBudget`.
3.  **Task (Action)**: The smallest executable unit of work. Key Attributes: `TaskID`, `WorkflowID`, `OwnerID`, `AssignedTool`, `Status`, `StartedAt`, `CompletedAt`, `EvidenceRef`, `ArtifactsProduced`. Governance Relevance: Enforces Law 5 (No Action without ownership).
4.  **Plan**: A candidate execution strategy generated to achieve an objective. Key Attributes: `PlanID`, `ObjectiveID`, `CreatorID`, `SuccessProbability` (%), `ForecastDuration` (days), `ForecastCost` ($), `RankScore`. Governance Relevance: Validates Law 3 (No Plan without an Objective).
5.  **Workflow**: An executable orchestration (DAG) generated from an approved Plan. Key Attributes: `WorkflowID`, `PlanID`, `TaskDAG` (JSON), `CurrentNodeID`, `AutonomyLimit`. Governance Relevance: Enforces Law 4 (No Workflow without a Plan).
6.  **Agent**: An AI workforce participant representing a specialized autonomous model. Key Attributes: `AgentID`, `Name`, `AgentClass` (Planner, Orchestrator, Executor, Reviewer, Governor, Learner, Knowledge Manager, etc.), `TrustScore` (0.00-1.00), `AutonomyProfile` (L0-L4), `GovernanceStatus`, `CostPer1KTokens`. Governance Relevance: Trust score < 70 triggers automatic suspension.
7.  **Human**: A human workforce participant. Key Attributes: `WorkforceID`, `Role`, `Skills`, `Capabilities`, `Capacity`, `Availability`, `TrustProfile`, `UserGroup`. Governance Relevance: Mandatory approver for high-risk actions and waivers.
8.  **Policy**: A declarative rule (OPA Rego) governing execution behaviors. Key Attributes: `PolicyID`, `Name`, `RegoBody`, `Scope`, `RiskClassification`, `OwnerID`, `EffectiveDate`, `ExpirationDate`. Governance Relevance: Supreme control layer; cannot be bypassed.
9.  **Budget**: The governed spending authority allocated to an objective or portfolio. Key Attributes: `BudgetID`, `TargetID` (Objective/Portfolio), `AllocatedLimit` ($), `CurrentSpent` ($), `ActualTokenCost`, `ModelPriceRatios` (JSON). Governance Relevance: Budget breaches immediately pause active workflows and request overrides.
10. **Budget Approval**: Governance authorization validating a budget adjustment or override. Key Attributes: `ApprovalID`, `RequestID`, `TargetBudgetID`, `AmountRequested` ($), `Status` (Pending, Approved, Rejected), `ApproverID`, `SignatureToken`. Governance Relevance: Enforces separation of duties (owner != approver).
11. **Simulation**: A Monte Carlo forecasting run evaluating plan feasibility. Key Attributes: `SimulationID`, `PlanID`, `RunsCount`, `CostDistribution` (JSON), `DurationDistribution` (JSON), `RiskFactors`.
12. **Knowledge Asset**: Validated organizational intelligence. Key Attributes: `AssetID`, `Source`, `Provenance`, `VectorIndexID`, `CypherPath`, `ConfidenceScore`. Governance Relevance: Enforces Law 9 (No Knowledge without Provenance).
13. **Learning Asset (Learning)**: An approved improvement derived from completed runs. Key Attributes: `LearningID`, `SourceRunID`, `TargetCapabilityID`, `RootCauseAnalysis`, `TemplateUpdates` (JSON), `GovernanceApprovalToken`. Governance Relevance: Enforces Law 8 (No Learning without Governance).
14. **Evidence**: Supporting proof validating an action or outcome. Key Attributes: `EvidenceID`, `ClaimID`, `SourceType` (IMAP, Slack, Git, OCR), `DataHash`, `FilePath`. Governance Relevance: Precedes recommendation; ensures audit integrity.
15. **Claim**: A declarative statement asserting a requirement or result. Key Attributes: `ClaimID`, `StatementText`, `AuthorID`, `ConfidenceScore`, `EvidenceLinks` (JSON). Governance Relevance: Required for traceability (Law 6: No Recommendation without Evidence).
16. **Value Metric (Metric)**: The measurement mechanism defining how an outcome is quantified. Key Attributes: `MetricID`, `Name`, `Formula`, `Unit` ($, seconds, count), `Frequency`, `OwnerID`. Governance Relevance: Validates Law 2 (No Outcome without Metrics).
17. **Outcome**: A measurable success indicator linked to an objective. Key Attributes: `OutcomeID`, `ObjectiveID`, `MetricID`, `BaselineValue`, `TargetValue`, `CurrentValue`, `Weight`.
18. **Audit Log**: An immutable record of system actions and verdicts. Key Attributes: `LogID`, `Timestamp`, `ActorID`, `TargetEntityID`, `ActionType`, `Verdict` (APPROVED/REJECTED), `DetailHash`. Governance Relevance: Captures Marquez OpenLineage and OPA execution traces.
19. **Exception Request (Exception)**: A request to temporarily override a policy or budget limit. Key Attributes: `ExceptionID`, `RequestorID`, `TargetPolicyID`, `Justification`, `ExpirationDate`, `ApproverID`, `SignatureToken`. Governance Relevance: Enforces Separation of Duties.
20. **Risk Acceptance**: Documented acceptance of risk exposure. Key Attributes: `RiskAcceptanceID`, `RiskID`, `Justification`, `ApproverID` (CEO), `ExpirationDate`. Governance Relevance: Bypasses OPA locks under explicit human accountability.
21. **Artifact**: The physical output synthesized during task execution. Key Attributes: `ArtifactID`, `TaskID`, `FilePath`, `FileHash`, `LicenseVerdict` (Permitted/Blocked), `ProvenanceMetadata` (JSON). Governance Relevance: Checked for copyleft (GPLv3) and security (SAST) vulnerabilities.

### Relationship Model
Enterprise UAWOS reality emerges through the federation of specialized graphs (Objective Graph, Knowledge Graph, Resource Graph, Policy Graph, Agent Graph, Value Graph, Portfolio Graph, Context Graph), rather than a single database schema.

*   **One-to-Many Relationships**:
    *   `Portfolio` $\rightarrow$ `Objective` (One portfolio contains multiple objectives).
    *   `Objective` $\rightarrow$ `Outcome` (One objective contains multiple measurable success outcomes).
    *   `Objective` $\rightarrow$ `Plan` (One objective evaluates multiple candidate execution plans).
    *   `Plan` $\rightarrow$ `Workflow` (One plan segments into multiple executable workflow DAGs).
    *   `Workflow` $\rightarrow$ `Task` (One workflow contains multiple sequential task nodes).
    *   `Task` $\rightarrow$ `Artifact` (One task generates multiple output files/documents).
    *   `Objective` $\rightarrow$ `Budget` (One objective manages multiple token/cash budgets).
    *   `Budget` $\rightarrow$ `Budget Approval` (One budget tracks multiple override authorizations).
    *   `Claim` $\rightarrow$ `Evidence` (One claim links to multiple pieces of verifying evidence).
    *   `Metric` $\rightarrow$ `Outcome` (One metric definition applies to multiple outcomes).
*   **Many-to-One / Many-to-Many Relationships**:
    *   `Workforce Entity` $\leftrightarrow$ `Capability` (Workforce entities possess multiple skills; capabilities map to multiple agents/humans).
    *   `Task` $\rightarrow$ `Workforce Entity` (Multiple tasks assign to a single human or agent owner).
    *   `Policy` $\leftrightarrow$ `Objective` / `Workflow` (Policies govern multiple execution scopes; workflows check multiple policies).
    *   `Risk` $\rightarrow$ `Outcome` (Multiple risks threaten the realization of an outcome).
    *   `Learning` $\rightarrow$ `Capability` (Lessons learned optimize multiple registered capabilities).
*   **Control-Plane Relationships**:
    *   `Audit Log` $\rightarrow$ `Actor` & `Target Entity` (Immutable tracking mapping operations back to users and objects).
    *   `Exception Request` $\rightarrow$ `Policy` & `Objective` (Overrides specific OPA rules on active goals).
    *   `OpenLineage` trace links (Automatically records data provenance flows from raw input to final artifact).

---

## 4. Information Architecture

### Site Map
*   **Primary Areas**:
    *   **Operational Command Center (`uawos_dashboard.html`)**: The system dashboard displaying strict health rings, traffic signals, alarms, and active blocker cards.
    *   **Requirement Ingestion Studio (`uawos_requirement_studio.html`)**: The requirement intake workspace containing paste inputs, critique panels, plan simulations, and strategic proposition tools.
    *   **Timeline & Roadmaps (`uawos_roadmap.html`)**: The interactive timeline displaying milestones `RD-01` to `RD-04` and capacity re-sequencing options.
    *   **Delivery & Traceability (`uawos_delivery.html`)**: The verification matrix linking raw intake requirements to epics, execution logs, and code artifacts.
    *   **Architecture & Topology (`uawos_architecture.html`)**: The interactive C4 viewer mapping Docker containers, internal engines (OPA, Ollama), and Postgres DB connections.
*   **Secondary Areas**:
    *   **Governance Registry Console**: Under the Governance tab, contains OPA Rego rule databases and OpenFGA tuple visualizers.
    *   **Exception & Waiver Inbox**: Central panel for reviewing and signing off on pending waivers (EXC-xxx) and risk acceptances.
    *   **Knowledge Graph Workspace**: Contains semantic dense search query panels and Neo4j graph nodes.
    *   **Portfolio Value & Ledger**: Financial and token cost tracking tables displaying cumulative spent against baseline value hypotheses.
*   **Utility & System Areas**:
    *   **Agent Directory**: Tab to register, audit, or suspend agents.
    *   **System Status Terminal**: Log console displaying HTTP Status Ingestion feeds (`GET /api/status`) and Docker system alarms.
    *   **Profile & Authenticator**: Utility to refresh secure JWT tokens (`x-uawos-token`).

### Navigation Architecture

*   **Executive Users (CEO/COO/CFO)**: Access the Portfolio Value Dashboard, budget approvals inbox, risk acceptances list, and executive ROI reporting.
*   **Product/Program Users (PM/PgM)**: Access the Ingestion Studio, proposition critique checklists, interactive roadmap timelines, and requirements traceability matrices.
*   **Operations Users (Ops Leader/SRE)**: Access the Operational Command Center dashboard, circular health ring, live alarms, active blockers, and agent registries.
*   **Engineers / Developers**: Access task workspaces, artifact reviews, execution consoles, and C4 topology graphs.
*   **Compliance / Governance Officers**: Access OPA Rego policy registries, OpenFGA relationship visualizers, exception request queues, and Marquez audit trails.

### Global Taxonomy (Canonical Labels)
*   **Major Objects**: Portfolio, Objective, Plan, Workflow, Task, Artifact, Agent, Policy, Budget, Exception, Claim, Evidence, Outcome.
*   **Statuses**: Draft, Active, Blocked, Paused, Completed, Failed, Suspended, Retired, Approved, Under Review.
*   **Governance Concepts**: Separation of Duties, Rego, OpenFGA ReBAC, Waiver (EXC-xxx), Risk Acceptance.
*   **Value Concepts**: Expected Value, Realized Value, Value Variance, Value Score, ROI, Baseline, Target.
*   **Workforce Concepts**: Autonomy Level (0-4), Trust Score, Skill Registry (SkillOpt), LangGraph Workflow, Agent Council.

---

## 5. Validation Review

*   **Architecture Review**: Pure Python BaseHTTPRequestHandler server wrapper is lightweight and fast; Docker-compose defines a comprehensive federated network (Postgres, OPA, OpenFGA, Marquez, Qdrant).
    *   *Missing*: FastAPI/ASGI framework is missing (making BaseHTTPRequestHandler route matching error-prone and synchronous).
*   **Governance Review**: Integration with Open Policy Agent (OPA) and OpenFGA provides a secure, stateless authorization and compliance control plane. Strict copyleft isolation (GPLv3 Marker service sandbox) is enforced.
    *   *Missing*: Dynamic management of OpenFGA tuples (currently statically seeded). No UI builder for OPA rules, forcing users to write raw Rego code.
*   **Scalability Review**: Federated graph structure allows separate vector, relational, and graph scaling. Local-first model easily ports to AWS/Azure cloud runs.
    *   *Missing*: Concurrency handling on JSON file state fallbacks (`uawos_*_state.json`) which introduces lock-outs and race conditions.
*   **UX Review**: Curved visual graphs, dark glassmorphic design system tokens, and clear traffic signals enhance readability.
    *   *Missing*: Screen reader support, keyboard focus outlines, and Aria-labels on circular SVG graphs (WCAG AA failures). No support playbooks for agent loops.
*   **Implementation Readiness Review**: Infrastructure is 70% operational, core Python engines and REST APIs are active.
    *   *Missing*: Shared central CSS tokens stylesheet (currently ad-hoc styles in HTML files). Client-side validation on budget forms is absent.

---

## 6. Assumptions
*   We assume that the system runs on port 8099 with a mock API wrapper for testing.
*   We assume that the user's browser supports modern ES6 modules and CSS variables (no legacy browser support).
*   We assume the local LLM running on CPU is TinyLlama and can handle standard requirement formats, though latency is high.
*   We assume that the PostgreSQL database will eventually replace all JSON local file state storage.
*   We assume that the front-end C4 architecture viewer displays static topology maps compiled from Docker configuration.

---
---

# PART 2 — USER EXPERIENCE STRATEGY (PHASE 2)

## 7. Persona Framework

### Human Personas

#### 1. Executive / Founder (CEO/CPO/COO/CFO)
*   **Primary Goals**: Maximize portfolio value realization, minimize token/compute TCO (Total Cost of Ownership), ensure 100% compliance with corporate and regulatory rules, and approve high-risk exceptions to keep critical objectives moving.
*   **Motivations**: Business ROI, strategic speed, operational defense (avoiding regulatory or license lawsuits), and scaling the organization without increasing administrative headcount.
*   **Pain Points**: Opaque AI agent spending (hidden token/compute run-rates), lack of trust in autonomous actions, legal exposure (e.g., GPLv3 license contamination in core codebases), and unmeasurable AI ROI.
*   **Responsibilities**: Defines strategic themes, authorizes budgets, accepts corporate risks, reviews portfolio ROI, and signs off on exception waivers.
*   **Key Workflows**: Portfolio review, budget authorization, exception override approvals, and strategic alignment audits.
*   **KPIs or Success Signals**: Realized Portfolio Value ($), Portfolio ROI (%), Budget Variance (%), Governance Compliance Rate (100%), and average exception approval cycle time.
*   **Decision Authority**: Ultimate economic and operational authority. Holds sole power to approve budget overrides above standard thresholds and grant temporary policy waivers.
*   **Permissions**: OpenFGA relationship owner/admin. Write access to strategic themes, exception registers, and budget limits. Read-only access to execution pipelines.
*   **Governance Exposure**: Final escalation checkpoint. Personally signs off on corporate risk acceptances.
*   **Frequency of Use**: Low-to-Medium (weekly reviews, real-time push alerts for critical approvals).
*   **Trust Needs**: Explainable plan summaries, verified financial ledgers, and clear evidence tracing outcomes back to original goals.
*   **Information Needs**: Value realized vs. hypothesized dashboards, portfolio budget run-rate projections, and active exception approval queues.
*   **Collaboration Touchpoints**: 
    *   *Humans*: Product Manager (for strategic priority reviews), Compliance Officer (for audit and risk alignment).
    *   *Agents*: Portfolio Governor Agent (for budget projections), Value Analyst Agent (for ROI calculations).
*   **Failure Risks if Experience is Poor**: Blind approval of non-compliant budgets, slow manual sign-offs that stall execution DAGs, or total abandonment of the platform due to perceived opacity.

#### 2. Product or Program Manager (PM/PgM)
*   **Primary Goals**: Convert raw strategic intent into structured objectives, resolve requirement ambiguity, choose optimal execution plans, and publish prioritized roadmaps.
*   **Motivations**: Delivering features on schedule, maximizing objective success rates, and automating repetitive status reporting.
*   **Pain Points**: Ingesting vague requirements, manual roadmap re-sequencing, communication gaps in human-agent handoffs, and hidden execution blocks.
*   **Responsibilities**: Objective sponsorship/ownership, requirements intake compilation, plan selection, dependency mapping, and outcome validation.
*   **Key Workflows**: Ingest raw requirement $\rightarrow$ complete critique checklist $\rightarrow$ choose plan candidate $\rightarrow$ prioritize roadmap milestones $\rightarrow$ monitor execution DAG.
*   **KPIs or Success Signals**: Objective Success Rate (%), Ingestion Completeness (%), Planning and Forecast Accuracy (%), and requirements-to-artifact coverage (%).
*   **Decision Authority**: Objective Sponsor. Selects plan candidates, authorizes objective-level budgets, and signs off on completed outcomes.
*   **Permissions**: Read/Write access on Ingestion Studio, Objective Graph, roadmap priorities, and outcome definitions. Read-only on OPA policy registries.
*   **Governance Exposure**: Constrained by Constitutional Law 1 (health score penalty if outcomes are missing) and OPA validation limits on budget inputs.
*   **Frequency of Use**: High (multiple daily sessions for ingestion, status tracking, and roadmap edits).
*   **Trust Needs**: Trace links from plan steps back to original source texts, clarity on why a requirement completeness score is low, and explainable simulation risk factors.
*   **Information Needs**: Critique checklists, Monte Carlo success probabilities, requirements traceability tables, and live outcome progress metrics.
*   **Collaboration Touchpoints**:
    *   *Humans*: Executive (strategic alignment), Engineer (task verification), Compliance Officer (override reviews).
    *   *Agents*: Planner Agent (decompositions), Challenger Agent (contrarian risk review), Value Analyst Agent (outcome audits).
*   **Failure Risks if Experience is Poor**: Launching plans based on flawed simulations, leading to execution failures, budget overruns, or circular dependency blocks.

#### 3. Operations Leader (Ops/SRE)
*   **Primary Goals**: Maintain 100% container and service uptime, optimize workforce agent capacity, resolve active system blockers, and secure system secrets.
*   **Motivations**: Service stability, token cost efficiency, rapid incident response, and clean infrastructure topology.
*   **Pain Points**: Agent loops consuming excessive tokens, un-alerted engine crashes, API timeouts, and resource contention.
*   **Responsibilities**: Infrastructure monitoring, agent registration, skill registry management, capacity planning, and troubleshooting.
*   **Key Workflows**: Monitor Command Center dashboard $\rightarrow$ troubleshoot active blocker incidents $\rightarrow$ register agents/MCP servers $\rightarrow$ execute agent kill switches.
*   **KPIs or Success Signals**: strict health score (%), core service uptime (%), agent trust score average, and MTTR for active blockers.
*   **Decision Authority**: Operational controller. Authority to manually suspend agents, adjust compute resource allocations, and decommission MCP servers.
*   **Permissions**: Read/Write on Agent Registry, Skill Registry, container configs, and network tools. Read-only on strategic themes.
*   **Governance Exposure**: Monitors compliance alerts and evaluates security and license vulnerability scans.
*   **Frequency of Use**: Continuous (open on dashboard monitors during shifts).
*   **Trust Needs**: Component latency metrics, system error logs, real-time Docker/BFF status indicators.
*   **Information Needs**: strict vs weighted health ring, active blocker cards (GPLv3 alerts), latency line charts, system alerts log.
*   **Collaboration Touchpoints**:
    *   *Humans*: Engineer (troubleshooting code artifacts), Compliance Officer (security review).
    *   *Agents*: Resource Manager Agent (capacity tracking), Simulation Agent (run impact checks), Governor Agent (alerts).
*   **Failure Risks if Experience is Poor**: Opaque agent activities result in unchecked token consumption loops before manual override is triggered.

#### 4. Engineer / Knowledge Worker (Developer)
*   **Primary Goals**: Complete delegated task workspaces, author high-quality code and documents, provide HITL approvals for tool execution.
*   **Motivations**: High-quality artifact synthesis, clean code standards, smooth tool execution sandboxing.
*   **Pain Points**: Repetitive manual reviews, lack of execution context in task assignments, strict tool sandboxing blocking valid commands.
*   **Responsibilities**: Task execution ownership, code/artifact reviews, manual verification evidence logging.
*   **Key Workflows**: Task assignment intake $\rightarrow$ execute task actions $\rightarrow$ verify tool executions (HITL) $\rightarrow$ log task evidence.
*   **KPIs or Success Signals**: Task Success Rate (%), Artifact Quality Rate, Compliance Rate (%), Evidence Log Completeness.
*   **Decision Authority**: Task owner. Holds authority over executing specific code changes and verifying tool calls.
*   **Permissions**: Read/Write on Task Workspaces, Artifact outputs, and verification checks. Read-only on portfolios.
*   **Governance exposure**: Enforces copyleft rules and security vulnerability scans on code artifacts.
*   **Frequency of Use**: High (continuous daily coding and task execution).
*   **Trust Needs**: Task provenance, security scans details, clear parameters for tool sandboxing.
*   **Information Needs**: Task DAG state, sandboxed execution console, audit logs, artifact diff blocks.
*   **Collaboration Touchpoints**:
    *   *Humans*: Product Manager (clarifications).
    *   *Agents*: Executor Agent, Reviewer Agent (co-authoring and test runs).
*   **Failure Risks if Experience is Poor**: Slow human verification loops stall sequential task DAGs, causing project delays.

#### 5. Governance / Compliance Officer
*   **Primary Goals**: Ensure 100% compliance with policies, legal, and license constraints (preventing copyleft pollution), audit lineage paths, evaluate access tuples.
*   **Motivations**: Legal protection, security compliance, strict auditability.
*   **Pain Points**: Policy drift, lack of visibility in agent tool calls, unencrypted state file exposure, static FGA mappings.
*   **Responsibilities**: Rego policy management, tuple relationship checks, compliance audits, exception logs review.
*   **Key Workflows**: OPA policy editing $\rightarrow$ tuple auditing $\rightarrow$ lineage trace analysis $\rightarrow$ compliance drift monitoring.
*   **KPIs or Success Signals**: Policy Compliance Rate (%), OPA Latency, OpenLineage Coverage (%), Security/Vulnerability Scan Status.
*   **Decision Authority**: Regulatory controller. Writes and publishes OPA policies; approves compliance-level waivers.
*   **Permissions**: Read/Write on OPA policy registries and OpenFGA mapping tables. Read-only on strategic themes and execution workspaces.
*   **Governance Exposure**: Central authority of the Governance Control Plane.
*   **Frequency of Use**: Medium (audits, policy revisions, exception queue reviews).
*   **Trust Needs**: Immutable audit ledgers, Cypher query accuracy, lineage provenance maps.
*   **Information Needs**: Rego editor errors, FGA tuple graph viewer, Marquez log explorer, exception registry.
*   **Collaboration Touchpoints**:
    *   *Humans*: Executive (risk signoff), Operations Leader (alert review).
    *   *Agents*: Governor Agent (real-time blocks), Knowledge Manager Agent (provenance trace).
*   **Failure Risks if Experience is Poor**: Opaque system state hides policy drift or un-audited exceptions, risking license breaches (GPLv3 in core IP).

---

## 8. Jobs-To-Be-Done (JTBD) Matrix

### Functional Jobs
*   **Ingest & Validate Requirements**: Parse raw unstructured requirements to extract PII, compile functional checklists, and generate measurable outcomes. (PM | Trigger: New raw document input | Priority: Critical)
*   **Simulate execution paths**: Forecast planning candidates to choose the optimal cost-duration route. (PM | Trigger: Objective structured | Priority: High)
*   **Monitor Control Plane**: Check component topology health and resolve execution dependencies or loops. (SRE | Trigger: System check / alert | Priority: Critical)
*   **Synthesize Artifacts**: Co-author code or documentation inside sandboxed REST execution spaces. (Developer | Trigger: Active task node | Priority: Critical)
*   **Verify Business ROI**: Validate and attribute actual spent tokens to realized portfolio outcomes. (Executive | Trigger: Strategic audit | Priority: High)

### Emotional & Trust Jobs
*   **Trust Agent Decisions**: Receive clear risk reasoning panels from Challenger agents. (PM | Trigger: Plan generation | Priority: High)
*   **Prevent Budget Runaway**: Guarantee token consumption stops automatically on threshold breach. (Executive | Trigger: Cost monitoring | Priority: Critical)
*   **Confirm Sandboxed Actions**: Inspect and authorize tool execution requests before they modify production code. (Developer | Trigger: Agent tool request | Priority: Critical)
*   **Verify Compliance Waivers**: Access lineage proof and justification records before signing waivers. (Compliance | Trigger: Exception request | Priority: High)

---

## 9. User Journey Architecture

```
Objective Ingest (Requirement Studio UI)
      ↓
OPA Compliance Pre-Check
      ↓
Monte Carlo Simulation (Planning Studio UI)
      ↓
Workflow Dispatch (LangGraph DAG)
      ↓
HITL Checkpoint (Task Workspace)
      ↓
Value Realization Audit (ROI Ledger)
```

### Executive Journey
*   **Trigger**: Weekly value audit or high-risk exception notification.
*   **Context**: Needs rapid portfolio alignment and override execution.
*   **Entry Point**: Portfolio Value Dashboard / Exception Approval Inbox.
*   **Stages**: Health Assessment $\rightarrow$ Exception Analysis $\rightarrow$ Override Authorization $\rightarrow$ ROI Verification.
*   **Failure Point**: Opaque justification blocks cause executive frustration or blind risk acceptance.
*   **KPIs**: Average exception cycle time, Portfolio ROI (%).

### Product Manager Journey
*   **Trigger**: Strategic request from executive board.
*   **Context**: Converting ideas into structured active objectives.
*   **Entry Point**: Requirement Ingestion Studio.
*   **Stages**: Document Upload $\rightarrow$ Critique Checklist Review $\rightarrow$ Plan Simulation runs $\rightarrow$ Roadmap publication.
*   **Failure Point**: CPU parsing crashes on long PDFs; lack of completeness criteria leads to simulation failures.
*   **KPIs**: Requirements completeness score (%), Plan Success Probability (%).

---

## 10. Service Blueprints

### Objective Ingestion Flow
*   **User Action**: Paste requirement or upload PDF in Requirement Studio.
*   **Frontstage System**: Display skeleton loading state; display critique Checklist and Ingestion preview panel.
*   **Human-Agent Collaboration**: PM resolves critique checklist; Challenger Agent flags initial scope risks.
*   **Backstage Services**: DTASE Engine (masks PII), Marker REST service on port 8000 (PDF parse), LiteLLM Gateway.
*   **Governance & Compliance**: Enforces Law 1 (Objective measurability check).
*   **Evidence Generated**: Completeness checklist metadata, PII masking verification hashes.

### Governance Exception Override Flow
*   **User Action**: Executive reviews pending waiver EXC-xxx in Exception Inbox. Inputs signature token.
*   **Frontstage System**: Display active exception details, violating Rego rule clause, and justification prompt.
*   **Human-Agent Collaboration**: Executor Agent requests override; Challenger Agent details risk impact; Executive signs off.
*   **Backstage Services**: OPA Policy Engine, OpenFGA authorization APIs.
*   **Governance & Compliance**: Enforces SoD (owner != approver).
*   **Evidence Generated**: EXC audit logs, signed cryptographically-validated override tokens.

---

## 11. Experience Principles
*   **Objective Supremacy**: The primary interface container is always the Objective, not the task. Bad: A board of manual tickets without parent objective goals. Good: An interactive dependency network of objectives.
*   **Governance First**: Compliance status and access controls must remain visible. Bad: Concealing a policy rejection within server logs. Good: Displaying a red banner showing the specific Rego clause that blocked the execution.
*   **Accountable Autonomy**: Autonomy dynamically scales based on trust scores, but humans remain the final safety gate. Bad: Executor Agent automatically committing code to main. Good: A HITL approval panel displaying a side-by-side code diff.

---

## 12. UX North Star Framework
*   **North Star**: "To provide a governed, friction-free operational control plane where enterprises manage, execute, and verify strategic intent through a transparent, continuously learning human-AI workforce."
*   **UX Anti-Patterns**: Opaque Agent Chains ("Agent Executing..." without active logs); Invisible Governance Verdicts (silently rejecting execution); Unverified Value Metrics (ROI without provenance link).

---
---

# PART 3 — APPLICATION ARCHITECTURE (PHASE 3)

## 13. Front-End Architecture

### Architecture Style
*   **Verified**: Single-page dashboard apps (`uawos_dashboard.html`, `uawos_requirement_studio.html`, etc.) served via a lightweight Python server wrapper on port 8099. Written in native ES6 Vanilla JavaScript and CSS variables.
*   **Inferred**: standalone HTML files share a common design token stylesheet to present a unified glassmorphic appearance.
*   **Recommended front-end pattern**: A BFF-oriented modular SPA shell. Share common UI elements (progress rings, cards) as native W3C Web Components.
*   **Why it fits UAWOS**: Prevents page reload latency during rapid re-planning cycles. Web Components encapsulate Outfit/Inter font styling natively without complex bundlers.

### State Management Strategy
*   **Verified**: Client-side state is handled in-memory within custom ES6 JavaScript controllers. Persistent state falls back to local server JSON files (`uawos_*_state.json`) which act as a fallback for PostgreSQL.
*   **Inferred**: strict vs. weighted health score calculations and agent latency metrics are updated in-memory via 5-second polling of `GET /api/status`.
*   **Recommended front-end pattern**: Centralized unidirectionally updated state store with SessionStorage cache to persist context across page transitions.

### Routing Strategy
*   **Verified**: Server-side URL mapping registers paths (`GET /roadmap` serves `uawos_roadmap.html`) in `apps/api/main.py` lines 83–130.
*   **Inferred**: Deep-linking to specific objectives uses query parameters (`/delivery.html?objective_id=UUID`).
*   **Recommended front-end pattern**: Client-side History routing with permission guards.

### Authentication & Authorization Architecture
*   **Verified**: Headers pass secure tokens via `X-UAWOS-Token`. OpenFGA relational rules (`fga_client.py`) validate role constraints (restricting budget actions to CEO, Lead Engineer, Database Expert, Admin). Enforces Separation of Duties.
*   **Inferred**: Buttons and override actions are dynamically disabled on load by querying OpenFGA.
*   **Recommended front-end pattern**: Centralized policy-aware UI directives that evaluate local permissions cache on element mount.

### API Integration & Real-Time Event Architecture
*   **Verified**: HTTP Polling of `GET /api/status` occurs at 5-second intervals.
*   **Inferred**: High latency LLM ingestion calls display skeleton states via the polling daemon.
*   **Recommended front-end pattern**: Implement Server-Sent Events (SSE) `/api/status/stream` to replace polling. Inject idempotency keys into all mutation POST requests.
*   **Why it fits UAWOS**: Real-time event streams allow SREs to catch runaway agent loops immediately, executing the kill switch before excessive token charges accumulate.

### Observability, Auditability, and Explainability Architecture
*   **Verified**: Dashboard displays core service container states (OPA, Qdrant, Postgres) and strict health metrics. Marquez OpenLineage logs map requirement-to-delivery tables.
*   **Inferred**: Rejection payloads display OPA Rego rule errors and Challenger agent risk evaluations in-context.
*   **Recommended front-end pattern**: An interactive slide-out drawer that displays Marquez OpenLineage trace graphs when a user clicks on any value realization metric.

### Multi-Tenant and Enterprise Boundary Considerations
*   **Verified**: Currently optimized for single-tenant, local-first environments to ensure strict data privacy.
*   **Inferred**: Portfolio views scoped by FGA user-portfolio relationship boundaries.
*   **Recommended front-end pattern**: Namespace-scoped state store. Headers inject Tenant ID and Workspace ID into all REST operations.
*   **Unverified**: Cross-tenant policy registries or global tenant billing models are unverified.

---

## 14. Feature Architecture

### Executive Command Center
*   **Verification Status**: Verified.
*   **Purpose**: High-level value audits and exception approvals interface.
*   **Primary Users**: Executive (CEO/CFO).
*   **Core Screens**: Portfolio ROI ledger, pending exceptions queue, active blocker alert cards.
*   **Governance Implications**: Enforces Separation of Duties.
*   **Cross-Links**: Budget Management, Governance Center, Audit Center.

### Objective Management
*   **Verification Status**: Verified.
*   **Purpose**: Manages the life cycle, dependency mappings, and health of system objectives.
*   **Primary Users**: Product Manager.
*   **Core Screens**: Objective dependency graph viewer, conflict resolution screen.
*   **Governance Implications**: Deducts 20 points from health score if outcomes are missing (Law 1).
*   **Cross-Links**: Requirement Studio, Planning Studio, Value Realization Hub.

### Portfolio Management
*   **Verification Status**: Verified.
*   **Purpose**: Manages collections of objectives under strategic themes and value capacities.
*   **Primary Users**: Executive / Founder (CEO).
*   **Core Screens**: Portfolio Catalog workspace, Strategic Theme settings.
*   **Governance Implications**: Enforces department-level budget bounds.
*   **Cross-Links**: Executive Command Center, Budget Management.

### Planning Studio
*   **Verification Status**: Inferred.
*   **Purpose**: Proposes, compares, and simulates execution plan candidates.
*   **Primary Users**: Product Manager.
*   **Core Screens**: Candidate Plan Comparison board, Simulation run console.
*   **Governance Implications**: OPA pre-checks cost boundaries before selection.
*   **Cross-Links**: Requirement Studio, Simulation Center.

### Requirement Studio
*   **Verification Status**: Verified.
*   **Purpose**: Ingests unstructured documents and voice inputs to compile requirements.
*   **Primary Users**: Product Manager.
*   **Core Screens**: Text/PDF Upload pane, Critique checklist interface.
*   **Governance Implications**: PII masking and license isolation (Marker sandbox).
*   **Cross-Links**: Objective Management, Planning Studio.

### Workforce Management
*   **Verification Status**: Inferred.
*   **Purpose**: Manages capacity, allocations, and availability of humans and agents.
*   **Primary Users**: Operations Leader, SRE.
*   **Core Screens**: Team Allocation dashboard, availability timelines.
*   **Governance Implications**: Restricts capability assignment to validated entities.
*   **Cross-Links**: Workforce Management, Agent Registry.

### Agent Registry
*   **Verification Status**: Verified.
*   **Purpose**: Directory for registering, auditing, and managing AI agent profiles.
*   **Primary Users**: Operations Leader, SRE.
*   **Core Screens**: Agent Catalog board, Agent metrics panel with Kill Switches.
*   **Governance Implications**: Suspends agents automatically if trust score falls below 70.
*   **Cross-Links**: Workforce Management, Governance Center.

### Governance Center
*   **Verification Status**: Verified.
*   **Purpose**: High-level interface to inspect exceptions, waivers, and access matrices.
*   **Primary Users**: Compliance Officer.
*   **Core Screens**: OPA Status console, OpenFGA relationship visualizer.
*   **Governance Implications**: Central control dashboard.
*   **Cross-Links**: Policy Management, Audit Center.

### Policy Management
*   **Verification Status**: Verified.
*   **Purpose**: Authors, compiles, and deploys OPA Rego policy files.
*   **Primary Users**: Compliance Officer.
*   **Core Screens**: Rego Policy Editor, policy compiler checks.
*   **Governance Implications**: Rego policies govern all system actions.
*   **Cross-Links**: Governance Center, Exception Management.

### Budget Management
*   **Verification Status**: Verified.
*   **Purpose**: Manages and tracks spent metrics, token costs, and limit adjustments.
*   **Primary Users**: Executive, Product Manager.
*   **Core Screens**: Budget Ledger details panel, override request console.
*   **Governance Implications**: Blocks agent operations on budget breach.
*   **Cross-Links**: Executive Command Center, Exception Management.

### Knowledge Graph Explorer
*   **Verification Status**: Verified.
*   **Purpose**: Visualizes and queries semantic connections, document logs, and ontologies.
*   **Primary Users**: Product Manager, Compliance Officer.
*   **Core Screens**: Graph search workspace, Neo4j graph nodes.
*   **Governance Implications**: Validates Law 9 (No Knowledge without Provenance).
*   **Cross-Links**: Audit Center, Requirement Studio.

### Simulation Center
*   **Verification Status**: Verified.
*   **Purpose**: Manages Mesa-based Monte Carlo simulation tasks and runs.
*   **Primary Users**: Product Manager, Simulation Agent.
*   **Core Screens**: Simulation setup board, scenario comparison console.
*   **Governance Implications**: Forecast results precede planning selection.
*   **Cross-Links**: Planning Studio, Requirement Studio.

### Value Realization Hub
*   **Verification Status**: Verified.
*   **Purpose**: Real-time business value validation and ROI ledger updates.
*   **Primary Users**: Executive, Product Manager.
*   **Core Screens**: Live ROI details, outcome realization panels.
*   **Governance Implications**: Validates Law 12 (No Value Claim without Measurement).
*   **Cross-Links**: Portfolio Management, Objective Management.

### Analytics Platform
*   **Verification Status**: Inferred.
*   **Purpose**: Displays PMCMS maturity scores, forecast variance, and trust radar indices.
*   **Primary Users**: Executive, Product Manager, SRE.
*   **Core Screens**: PMCMS maturity dashboard, Performance Analytics.
*   **Governance Implications**: Logs PMCMS compliance metrics.
*   **Cross-Links**: Agent Registry, Value Realization Hub.

### Audit Center
*   **Verification Status**: Verified.
*   **Purpose**: Inspects Marquez lineage graphs and read-only Postgres audit records.
*   **Primary Users**: Compliance Officer.
*   **Core Screens**: Marquez logs explorer, audit ledger screen.
*   **Governance Implications**: Ensures total system trace checks.
*   **Cross-Links**: Governance Center, Knowledge Graph Explorer.

### Settings and Administration
*   **Verification Status**: Inferred.
*   **Purpose**: Manages jwt tokens, FGA role bindings, and refresh intervals.
*   **Primary Users**: Operations Leader, Compliance Officer.
*   **Core Screens**: User role mapping registry, configuration console.
*   **Governance Implications**: Ensures baseline security configurations.
*   **Cross-Links**: Governance Center.

---

## 15. Cross-Module Architecture

### Shared Workflows
*   **Objective Lifecycle**: Ingestion Studio $\rightarrow$ Objective Graph (Cycle Check) $\rightarrow$ Planning Simulation $\rightarrow$ Budget allocation $\rightarrow$ Workflow dispatch (LangGraph) $\rightarrow$ Lineage logging (Marquez) $\rightarrow$ ROI audits.
*   **Governance Exception**: Budget/Workflow limit exceeded (OPA Block) $\rightarrow$ Exception EXC-xxx queue entry $\rightarrow$ Executive Command Center Override signoff $\rightarrow$ Workflow execution resume.

### Shared Services & UI Patterns
*   **Shared Services**: Identity Context (JWT-based role gating), Governance pre-flight checks, Notification toasts, Trust Score updates.
*   **Shared UI Patterns**: Dark slate theme tokens, HSL status pills, line-graph variance cards, Marquez audit drawers, focus indicators (`outline: 2px solid #818cf8` with offsets).

### Cross-Cutting Failure States
*   **Partial Telemetry Outage**: BFF API fails to read container status. Command Center switches badges to Grey ("Offline") but leaves relational data panels operational.
*   **Budget Lockout**: Runaway token cost loops trigger budget breaches. UI suspends Executor Agent and alerts SRE.

---

## 16. Validation Review

*   **Architecture**: Pure Python server routing is lightweight and fast.
    *   *Blocker*: Synchronous backend routing blocks long-running requests during ingestion.
    *   *Assumption*: Client polling resolves async updates until a SSE streaming gateway is deployed.
*   **Governance**: OPA and OpenFGA permissions checks are verified.
    *   *Blocker*: None.
    *   *Assumption*: OpenFGA tuples are statically seeded on server start.
*   **Scalability**: Neo4j, Postgres, and Qdrant databases are verified.
    *   *Blocker*: Concurrency issues will cause file write locks on local JSON state stores.
    *   *Assumption*: A migration to PostgreSQL tables will replace fallback JSON files.
*   **UX**: Curved visual graphs and dark glassmorphic tokens are verified.
    *   *Blocker*: WCAG AA violations on circular SVGs (lack of screen-reader support).
    *   *Assumption*: Custom focus rings and aria-labels are injected via Web Component wrappers.
*   **Implementation Readiness**: Core API endpoints are active.
    *   *Blocker*: Inline styling duplication across HTML files complicates UI standardization.
    *   *Assumption*: A central tokens stylesheet is imported by all standalone HTML files.

---

## 17. Assumptions
*   We assume that the client application communicates with the backend HTTP server over port 8099 with connection timeouts set to 30 seconds.
*   We assume that the user's browser is modern and supports ES6 module imports and CSS custom variables natively.
*   We assume that PII masking heuristics in the DTASE engine occur on the client or in a secure gateway before sending data to Ollama.
*   We assume that the PostgreSQL audit logs and Marquez lineage records are read-only and cannot be modified by any user role.
*   We assume the C4 topology viewer renders static configuration maps generated from the system’s Docker compose layout.
