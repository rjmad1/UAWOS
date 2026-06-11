# Diagram 5 — State Machine (Objective Lifecycle)

## Purpose
Defines the canonical lifecycle and all allowable transitions for the **Objective** — the most critical entity in the UAWOS platform. All governance rules, execution logic, and value measurement depend on the correct state of an Objective.

## Questions This Diagram Answers
- What transitions are allowed? Which are forbidden?
- What states cause a stuck objective?
- What can be retried? What is terminal?
- Who can trigger each transition?

## Scope
**In scope:** Objective entity state machine, all valid/invalid transitions, triggers, terminal states  
**Out of scope:** Sub-objective state machines, Plan/Workflow/Action state machines (separate diagrams)

## Common Mistakes to Avoid
- ❌ Skipping edge/failure states (Blocked, At Risk, Failed)
- ❌ Not marking terminal states clearly (Completed, Failed, Cancelled, Archived)
- ❌ Missing the governance gate on state transitions

## Most Useful For
QA · SRE · Product · Engineering

---

## State Machine Diagram

```mermaid
stateDiagram-v2
    [*] --> Draft : CREATE objective\n(human submits input)

    Draft --> Validating : SUBMIT for validation\n[DTASE analysis triggered]

    Validating --> Draft : VALIDATION_FAILED\n[Missing outcome / low health score]\n→ User revises

    Validating --> PendingApproval : VALIDATION_PASSED\n[health_score ≥ 60, outcome present]

    PendingApproval --> Draft : REJECTED by Governance\n[Policy violation detected]\n→ User amends

    PendingApproval --> Active : APPROVED\n[Governance clearance granted]\n[Plan generated + budget approved]

    Active --> Paused : PAUSE requested\n[Human-initiated or resource conflict]\n→ Workflows suspended

    Paused --> Active : RESUME\n[Human approval + resource freed]

    Paused --> Cancelled : CANCEL\n[Business decision — terminal]

    Active --> Blocked : BLOCKED condition detected\n[Circular dependency / policy block /\nexternal integration failure]

    Blocked --> Active : UNBLOCKED\n[Conflict resolved / dependency cleared]

    Blocked --> Failed : TIMEOUT in blocked state\n[> 72 hours without resolution]

    Active --> AtRisk : HEALTH_DEGRADED\n[health_score < 40 OR\ncost_actual > 120% allocated OR\ndeadline < 3 days remaining]

    AtRisk --> Active : HEALTH_RESTORED\n[Human intervention + remediation plan\napplied by Recommendation Engine]

    AtRisk --> Failed : HEALTH_CRITICAL\n[health_score < 10 OR\ncost_actual > 200% allocated]

    Active --> Completed : OUTCOME_VERIFIED\n[All outcomes measured ≥ target\nGovernance sign-off received\nValue Realization recorded]

    Completed --> Archived : ARCHIVE\n[30 days post-completion\nor manual trigger]

    Failed --> Archived : ARCHIVE\n[Post-mortem completed\nLearning Engine update triggered]

    Cancelled --> Archived : ARCHIVE\n[Retained for audit trail]

    Completed --> [*]
    Failed --> [*]
    Cancelled --> [*]
    Archived --> [*]

    note right of Draft
        Health score calculated:
        - Has measurable outcome: +40
        - Has owner: +20
        - Has deadline: +15
        - Has budget: +15
        - Has dependencies mapped: +10
        Max: 100 | Minimum to activate: 60
    end note

    note right of Active
        Continuous monitoring:
        - Budget variance check (daily)
        - Dependency health check
        - Agent execution telemetry
        - SLO tracking
    end note

    note right of Blocked
        Auto-escalation triggered if
        blocked > 24 hours.
        Governance Engine notifies owner
        and suggests resolution paths.
    end note

    note right of Completed
        Value Realization triggers:
        - Learning Engine update
        - Organizational knowledge promotion
        - Outcome metrics recorded
        - ROI calculation
    end note
```

---

## Transition Authority Matrix

| Transition | Who Can Trigger | Automated? | Governance Required? |
|-----------|----------------|-----------|---------------------|
| Draft → Validating | Any authorized user | ✅ Partially | No |
| Validating → PendingApproval | DTASE + Governance Engine | ✅ Automated | No |
| PendingApproval → Active | Governance Engine | ✅ Automated (OPA) | ✅ Yes |
| PendingApproval → Draft | Governance Engine | ✅ Automated | ✅ Yes |
| Active → Paused | PM / Operations Lead | ❌ Human | ✅ Notified |
| Active → AtRisk | Observability Engine | ✅ Automated | ✅ Notified |
| Active → Blocked | Orchestration Engine | ✅ Automated | ✅ Escalated |
| Active → Completed | Governance Engine | ✅ Automated | ✅ Yes |
| Blocked → Failed | System (timeout) | ✅ Automated | ✅ Logged |
| Any → Cancelled | PM / Executive | ❌ Human | ✅ Audit recorded |

---

## Terminal States

| State | Retryable? | Learning Signal? | Audit Required? |
|-------|-----------|-----------------|----------------|
| Completed | ❌ | ✅ Full learning update | ✅ Yes |
| Failed | Via new Objective | ✅ Failure analysis | ✅ Yes |
| Cancelled | Via new Objective | ✅ Partial | ✅ Yes |
| Archived | ❌ | ✅ Read-only | ✅ Yes |

---

## Related State Machines (Future Diagrams)

- **Plan State Machine**: Draft → Simulating → Approved → Executing → Completed / Failed
- **Action State Machine**: Pending → Executing → AwaitingApproval → Completed / Failed / Rolled Back
- **Agent State Machine**: Idle → Assigned → Executing → Reviewing → Complete / Suspended

---

*Source: `Requirements Master/file.pdf` · `ADD.md` · `uawos_objective.py` · `uawos_governance.py`*
