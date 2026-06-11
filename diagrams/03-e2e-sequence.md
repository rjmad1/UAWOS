# Diagram 3 — E2E Sequence Diagram (Happy Path)

## Purpose
Makes execution flow explicit across services — from user intent to realized outcome — for the primary "Objective Intake → Execution → Value Realization" happy path.

## Questions This Diagram Answers
- What happens when a user submits an objective?
- Where can latency occur? What breaks if the LLM is slow?
- Where are data writes performed vs. reads only?
- Where do timeout/retry semantics apply?

## Scope
**In scope:** Objective ingestion, governance approval, plan execution, outcome delivery  
**Out of scope:** Error/failure paths, background learning cycles, multi-tenant flows

## Common Mistakes to Avoid
- ❌ Only showing service hops but missing data write events
- ❌ No timeout/retry semantics shown
- ❌ Missing governance checkpoint in the critical path

## Most Useful For
QA · Engineering · SRE · Product

---

## Diagram

```mermaid
sequenceDiagram
    autonumber

    actor User as 👤 Operator / PM
    participant Studio as Requirement Studio
    participant API as API Server :8099
    participant DTASE as DTASE Engine
    participant Marker as Marker Service (PDF)
    participant LLM as LLM Gateway (LiteLLM)
    participant Governance as Governance Engine
    participant OPA as OPA :8181
    participant OpenFGA as OpenFGA :8083
    participant Planning as Planning Engine
    participant Simulation as Simulation Engine
    participant Orchestrator as Orchestration Engine
    participant Temporal as Workflow Runtime (Temporal)
    participant Agent as Executor Agent
    participant Postgres as PostgreSQL :5435
    participant KnowledgeGraph as Knowledge Graph (Neo4j)
    participant Lineage as Marquez (Lineage)
    participant Value as Value Engine

    Note over User,Studio: ① OBJECTIVE INTAKE
    User->>Studio: Submit objective input (text/voice/PDF)
    Studio->>API: POST /api/dtase/analyze {input, context}
    API->>DTASE: Parse and translate input
    opt PDF Document Provided
        DTASE->>Marker: POST /parse {document}
        Note right of Marker: GPLv3 sandboxed container<br/>timeout: 30s
        Marker-->>DTASE: Markdown text content
    end
    DTASE->>LLM: POST /api/generate {prompt, context}
    Note right of LLM: TinyLlama/DeepSeek inference<br/>timeout: 60s · retry: 3x
    LLM-->>DTASE: Structured objective + opportunities/risks
    DTASE->>Postgres: INSERT objective record (Draft state)
    DTASE->>KnowledgeGraph: Write evidence + claims nodes
    DTASE-->>API: {objective_id, health_score, artifacts}
    API-->>Studio: Objective preview + opportunities
    User->>Studio: Review and publish objective

    Note over API,Governance: ② GOVERNANCE CHECK
    API->>Governance: Evaluate objective against policies
    Governance->>OPA: POST /v1/data/uawos/policy {objective, context}
    Note right of OPA: Rego rule evaluation<br/>Laws 1-15 enforced
    OPA-->>Governance: {allow: true/false, violations: [], budget_ok: true}
    Governance->>OpenFGA: Check user authorization for objective type
    OpenFGA-->>Governance: {allowed: true}
    Governance->>Postgres: INSERT governance_audit_record
    alt Policy violation detected
        Governance-->>API: {status: "blocked", violations: [...]}
        API-->>Studio: ⚠️ Policy violation — user notified
        User->>Studio: Resolve violation and resubmit
    else All policies pass
        Governance-->>API: {status: "approved"}
    end

    Note over API,Planning: ③ PLAN GENERATION
    API->>Planning: Generate execution plan for objective
    Planning->>Simulation: Run Monte Carlo cost/duration forecast
    Note right of Simulation: Generates 3 candidate plans<br/>with success probability scores
    Simulation-->>Planning: [{plan_A: {cost, duration, probability}}, ...]
    Planning->>Postgres: INSERT plan records (ranked by score)
    Planning-->>API: {plans: [...], recommended_plan_id}
    API-->>Studio: Plan options with forecast
    User->>Studio: Select plan → approve budget
    API->>Postgres: UPDATE plan status: "approved"

    Note over Orchestrator,Agent: ④ EXECUTION
    API->>Orchestrator: Dispatch approved plan
    Orchestrator->>Temporal: Create workflow execution (durable)
    loop For each workflow step
        Temporal->>Agent: Execute task {action_type, context, tools}
        Note right of Agent: Agent: Planner → Orchestrator → Executor<br/>Autonomy governed by trust score
        Agent->>LLM: LLM tool call / reasoning
        LLM-->>Agent: Tool result
        Agent->>Lineage: Emit lineage event (OpenLineage)
        Lineage->>Postgres: Persist lineage record
        alt Action requires human approval
            Agent->>API: POST /api/approval/request {action, rationale}
            API-->>User: 🔔 Approval required notification
            User->>API: POST /api/approval/grant {action_id}
            Note right of User: HITL checkpoint<br/>Irreversible actions blocked until granted
        end
        Agent-->>Temporal: Task complete + artifact
    end
    Temporal-->>Orchestrator: Workflow complete
    Orchestrator->>Postgres: UPDATE objective status: "Completed"

    Note over Value,User: ⑤ VALUE REALIZATION
    Orchestrator->>Value: Calculate value realization
    Value->>Postgres: Read outcome metrics vs. baseline
    Value->>KnowledgeGraph: Write outcome evidence + value score
    Value->>Postgres: INSERT value_realization_record
    Value-->>API: {value_score, dimensions: {financial, operational, strategic}}
    API-->>Studio: ✅ Objective complete — value dashboard updated
    User->>Studio: Review value realization report
```

---

## Critical Latency Points

| Step | Expected Latency | Timeout | Retry |
|------|-----------------|---------|-------|
| LLM inference (TinyLlama) | 5–30s (CPU) | 60s | 3x |
| PDF parsing (Marker) | 5–15s | 30s | 1x |
| OPA policy evaluation | < 100ms | 5s | 2x |
| Temporal workflow step | Variable | Per-step | Durable |
| PostgreSQL reads/writes | < 50ms | 5s | 3x |

## Human-in-the-Loop Checkpoints

| Checkpoint | Trigger | Required By |
|-----------|---------|------------|
| Objective publish | User reviews DTASE output | Always |
| Budget approval | Plan cost exceeds threshold | AP-05 Human Accountability |
| Irreversible action | Code commit / spend / publish | Constitutional Law |
| Policy override | Governance violation exception | Compliance Officer |

---

*Source: `Requirements Master/file.pdf` · `ADD.md` · `uawos_dashboard_daemon.py` · `uawos_governance.py`*
