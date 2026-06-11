# Diagram 4 — Domain Model (Bounded Context + Entities)

## Purpose
Establishes shared language for business logic, prevents domain mismatch across teams, and defines canonical entity ownership.

## Questions This Diagram Answers
- What is an Objective vs. an Outcome vs. a Plan?
- Who owns which entity? What is the source of truth for each?
- Where are the bounded context boundaries?

## Scope
**In scope:** First-class entities, bounded contexts, key relationships  
**Out of scope:** Database schema details, API payload shapes, UI components

## Common Mistakes to Avoid
- ❌ Turning the domain model into a DB schema (avoid data types/foreign keys)
- ❌ Defining an unbounded "god domain" with no context separation
- ❌ Missing the source-of-truth ownership annotation per entity

## Most Useful For
Product · Engineering · Architecture · QA

---

## Bounded Context Map

```mermaid
graph TB
    subgraph BC_OBJ["📋 Objective Management Domain"]
        Objective["**Objective**\n────────────────\nid · title · priority\nstatus · health_score\nowner · deadline\ndependencies[]"]
        Outcome["**Outcome**\n────────────────\nid · objective_id\nmeasure · target\nbaseline · actual\nvalue_dimension"]
        Portfolio["**Portfolio**\n────────────────\nid · name · theme\nbudget · owner\nobjectives[]"]
        Workspace["**Workspace**\n────────────────\nid · org_id · name\ncontext · members[]"]
    end

    subgraph BC_EXEC["⚙️ Execution Domain"]
        Plan["**Plan**\n────────────────\nid · objective_id\ntype · steps[]\ncost_forecast\nduration_forecast\nprobability"]
        Workflow["**Workflow**\n────────────────\nid · plan_id\nsteps[] · status\nscheduled_at\norchestrator_id"]
        Action["**Action**\n────────────────\nid · workflow_id\ntype · tool\nparams · status\nrequires_approval\nreversible"]
        Artifact["**Artifact**\n────────────────\nid · action_id\ntype · content\nprovenance\nconfidence"]
    end

    subgraph BC_WORK["👥 Workforce Domain"]
        Agent["**Agent**\n────────────────\nid · name · type\ncapabilities[]\ntrust_score\nreputation_history\nautonomy_level"]
        AgentTeam["**Agent Team**\n────────────────\nid · name · agents[]\ngoal · owner"]
        Human["**Human**\n────────────────\nid · name · role\nteam · permissions[]\napproval_authority"]
        Capability["**Capability**\n────────────────\nid · name · type\nskills[] · version"]
    end

    subgraph BC_GOV["🛡️ Governance Domain"]
        Policy["**Policy**\n────────────────\nid · name · type\nrego_rule · scope\nversion · owner"]
        Risk["**Risk**\n────────────────\nid · objective_id\nseverity · probability\nimpact · mitigations[]"]
        Approval["**Approval**\n────────────────\nid · action_id\nrequester · approver\nstatus · timestamp\nrationale"]
        Constraint["**Constraint**\n────────────────\nid · type · scope\nvalue · enforced_by"]
    end

    subgraph BC_KNOW["🧠 Knowledge Domain"]
        KnowledgeAsset["**Knowledge Asset**\n────────────────\nid · title · type\nsource · provenance\nconfidence · owner\nlifecycle"]
        MemoryAsset["**Memory Asset**\n────────────────\nid · agent_id\nvector · content\ncreated_at · ttl"]
        Evidence["**Evidence**\n────────────────\nid · claim_id\nsource · type\nconfidence · timestamp"]
        Claim["**Claim**\n────────────────\nid · statement\nstatus · validated_by\nsource_of_truth"]
    end

    subgraph BC_VAL["💰 Value Domain"]
        Metric["**Metric**\n────────────────\nid · name · type\nunit · target\nactual · slo"]
        Decision["**Decision**\n────────────────\nid · context\nrationale · options[]\nchosen · outcome\nexplainability"]
        ValueRealization["**Value Realization**\n────────────────\nid · objective_id\nfinancial · operational\nstrategic · risk\nlearning · timestamp"]
        Budget["**Budget**\n────────────────\nid · objective_id\nallocated · actual\ntoken_spend\nmodel_costs[]"]
    end

    subgraph BC_RES["📦 Resource Domain"]
        Resource["**Resource**\n────────────────\nid · type · name\ncapacity · available\nschedulable\nallocated_to[]"]
        Assumption["**Assumption**\n────────────────\nid · statement\nowner · validated\nrisk_if_wrong"]
        Hypothesis["**Hypothesis**\n────────────────\nid · statement\nexperiment_id\nstatus · evidence[]"]
        Experiment["**Experiment**\n────────────────\nid · hypothesis_id\nmethod · result\nlearning"]
    end

    %% Cross-context relationships
    Objective -->|"has many"| Outcome
    Objective -->|"decomposes into"| Objective
    Objective -->|"generates"| Plan
    Portfolio -->|"contains"| Objective
    Workspace -->|"scopes"| Portfolio

    Plan -->|"produces"| Workflow
    Workflow -->|"triggers"| Action
    Action -->|"creates"| Artifact
    Action -->|"needs"| Approval

    Agent -->|"has"| Capability
    AgentTeam -->|"composed of"| Agent
    Human -->|"grants"| Approval
    Agent -->|"executes"| Action

    Policy -->|"governs"| Action
    Policy -->|"governs"| Agent
    Risk -->|"threatens"| Objective
    Constraint -->|"limits"| Agent

    Evidence -->|"supports"| Claim
    Claim -->|"informs"| Decision
    Decision -->|"creates"| Action
    KnowledgeAsset -->|"contains"| Evidence

    Decision -->|"realizes"| ValueRealization
    Outcome -->|"measured by"| Metric
    Budget -->|"tracks"| Objective
    ValueRealization -->|"evaluates"| Objective

    Resource -->|"allocated to"| Workflow
    Hypothesis -->|"tested by"| Experiment
    Experiment -->|"produces"| Evidence

    style BC_OBJ fill:#1e3a5f,color:#e8f4fd,stroke:#4a9ece
    style BC_EXEC fill:#1a3a1a,color:#e8fde8,stroke:#4aae4a
    style BC_WORK fill:#3a1a3a,color:#fde8fd,stroke:#ae4aae
    style BC_GOV fill:#3a1a1a,color:#fde8e8,stroke:#ae4a4a
    style BC_KNOW fill:#3a2a1a,color:#fdf0e8,stroke:#ae804a
    style BC_VAL fill:#1a2a3a,color:#e8f0fd,stroke:#4a6aae
    style BC_RES fill:#2a3a1a,color:#f0fde8,stroke:#6aae4a
```

---

## Entity Source of Truth

| Entity | Source of Truth | Store | Owner Domain |
|--------|----------------|-------|-------------|
| Objective | UAWOS Core | PostgreSQL + Objective Graph | Objective Management |
| Outcome | UAWOS Core | PostgreSQL + Value Graph | Objective Management |
| Plan | Planning Engine | PostgreSQL | Execution |
| Workflow | Temporal | Temporal DB | Execution |
| Action | Action Service | PostgreSQL | Execution |
| Agent | Agent Registry | Agent Graph (Neo4j) | Workforce |
| Policy | Policy Registry | Policy Graph + OPA | Governance |
| Knowledge Asset | Knowledge Engine | Knowledge Graph + Qdrant | Knowledge |
| Decision | Governance Engine | PostgreSQL + Knowledge Graph | Value |
| Budget | Budget Service | PostgreSQL | Value |
| Value Realization | Value Engine | Value Graph | Value |

---

## Constitutional Laws Affecting Entities

| Law | Entity Affected | Rule |
|-----|----------------|------|
| Law 1 | Objective | Must contain at least one measurable Outcome |
| Law 5 | Action | Irreversible actions require explicit human Approval |
| Law 11 | Agent | All agent actions must be verifiable and auditable |
| Law 14 | Knowledge Asset | Organizational knowledge takes precedence over external |

---

*Source: `Requirements Master/file.pdf` · `ADD.md` · `COS.md` · `uawos_objective.py` · `uawos_traceability.py`*
