# Diagram 8 — Observability + Operations

## Purpose
Makes UAWOS operable, measurable, and supportable. Defines SLIs, SLOs, metrics/logs/traces flow, alert routing, runbook triggers, and on-call ownership.

## Questions This Diagram Answers
- How do we detect issues before users do?
- What triggers a page? What is our SLO and error budget?
- Who is on call? What do they do when alerted?
- What dashboards and runbooks exist?

## Scope
**In scope:** All observability signals, SLI/SLO definitions, alert routing, runbook mapping, on-call ownership  
**Out of scope:** Application code instrumentation details, dashboard UI screenshots

## Common Mistakes to Avoid
- ❌ Defining alerts without SLOs (alerts mean nothing without a target)
- ❌ No runbooks attached to alert conditions
- ❌ No ownership routing (who gets paged?)
- ❌ Missing error budget burn rate tracking

## Most Useful For
SRE · DevOps · Engineering

---

## Observability Signal Flow

```mermaid
flowchart LR
    subgraph SOURCES["📊 Signal Sources (All Platform Components)"]
        UAWOS_API["UAWOS API Server\n:8099"]
        AGENTS["Agent Executor Pool\n[Planner · Executor · Reviewer]"]
        GOVERNANCE["Governance Engine\n[OPA · OpenFGA]"]
        PLANNING["Planning Engine\n+ Simulation Engine"]
        KNOWLEDGE["Knowledge Engine\n+ Learning Engine"]
        INFRA["Infrastructure\n[PostgreSQL · Qdrant · Neo4j\nTemporal · Docker]"]
        LLM["LLM Gateway\n[LiteLLM · Ollama]"]
    end

    subgraph COLLECTION["🔄 Collection Layer"]
        METRICS["Metrics Collector\n[Prometheus / CloudWatch]\n• Counters · Gauges · Histograms\n• Scrape interval: 15s"]
        LOGS["Log Aggregator\n[Fluent Bit / CloudWatch Logs]\n• Structured JSON logs\n• Log levels: DEBUG · INFO · WARN · ERROR"]
        TRACES["Trace Collector\n[OpenTelemetry Collector]\n• Distributed traces\n• Span propagation: W3C TraceContext"]
        LINEAGE["Lineage Tracker\n[Marquez / OpenLineage]\n• Execution data flow events\n• Dataset-level lineage"]
        AUDIT["Audit Collector\n[Immutable Audit Log]\n• Every governance decision\n• Every agent action\n• WORM storage"]
    end

    subgraph STORE["💾 Observability Store"]
        PROM_STORE["Prometheus TSDB\n[Metrics time-series]\n[Retention: 30 days]"]
        LOG_STORE["Log Storage\n[S3 / CloudWatch Logs]\n[Retention: 90 days hot\n7 years cold]"]
        TRACE_STORE["Jaeger / X-Ray\n[Trace storage]\n[Retention: 7 days hot]"]
        AUDIT_STORE["Audit Store\n[PostgreSQL — Immutable]\n[Retention: 7 years]"]
    end

    subgraph DASHBOARDS["📈 Dashboards"]
        OPS_DASH["Operations Dashboard\n[UAWOS Dashboard :8099]\n• Objective health heatmap\n• Agent execution status\n• Budget burn rate"]
        SLO_DASH["SLO Dashboard\n[Superset :8088 / Grafana]\n• Error budget remaining\n• SLI trend lines\n• Burn rate alerts"]
        EXEC_DASH["Executive Dashboard\n[Value Realization view]\n• Objective completion rate\n• Value realized vs. forecast\n• Cost per objective"]
        LINEAGE_DASH["Lineage Dashboard\n[Marquez Web :5001]\n• Data flow maps\n• Dataset health\n• Job run history"]
    end

    subgraph ALERTING["🔔 Alert Routing"]
        ALERT_MGR["Alert Manager\n[Prometheus AlertManager]"]
        PAGERDUTY["PagerDuty\n[On-call routing]"]
        SLACK_ALERTS["Slack #uawos-alerts\n[Non-critical notifications]"]
        EMAIL["Email Escalation\n[Critical unacknowledged > 30 min]"]
    end

    subgraph ONCALL["👥 On-Call Ownership"]
        SRE_ONCALL["SRE On-Call\n[Infrastructure · Availability\n· Database · Deployment]"]
        ENG_ONCALL["Engineering On-Call\n[Application bugs · Agent loops\n· Planning failures]"]
        COMPLIANCE_ONCALL["Compliance On-Call\n[Policy violations · Audit failures\n· Security incidents]"]
    end

    subgraph RUNBOOKS["📖 Runbooks"]
        RB1["RB-001: Objective Stuck\n[diagnosis · retry steps\n· escalation path]"]
        RB2["RB-002: Agent Loop Timeout\n[kill signal · state recovery\n· LLM failover]"]
        RB3["RB-003: Budget Alert\n[cost spike investigation\n· agent throttling\n· emergency stop]"]
        RB4["RB-004: Policy Violation\n[OPA evaluation trace\n· exception request flow]"]
        RB5["RB-005: Database Down\n[failover steps\n· state reconciliation]"]
        RB6["RB-006: LLM Offline\n[heuristic fallback\n· model switching\n· queue drain]"]
    end

    %% Signal flows
    UAWOS_API --> METRICS & LOGS & TRACES & AUDIT
    AGENTS --> METRICS & LOGS & TRACES & LINEAGE
    GOVERNANCE --> METRICS & LOGS & AUDIT
    PLANNING --> METRICS & LOGS & TRACES
    KNOWLEDGE --> METRICS & LOGS & LINEAGE
    INFRA --> METRICS & LOGS
    LLM --> METRICS & LOGS & TRACES

    METRICS --> PROM_STORE
    LOGS --> LOG_STORE
    TRACES --> TRACE_STORE
    AUDIT --> AUDIT_STORE
    LINEAGE --> LOG_STORE

    PROM_STORE --> SLO_DASH & ALERT_MGR
    LOG_STORE --> OPS_DASH & LINEAGE_DASH
    TRACE_STORE --> OPS_DASH
    AUDIT_STORE --> EXEC_DASH
    LINEAGE --> LINEAGE_DASH

    ALERT_MGR -->|"P1 · P2 alerts"| PAGERDUTY
    ALERT_MGR -->|"P3 · P4 alerts"| SLACK_ALERTS
    PAGERDUTY -->|"Unack > 30 min"| EMAIL

    PAGERDUTY -->|"Infra alerts"| SRE_ONCALL
    PAGERDUTY -->|"App alerts"| ENG_ONCALL
    PAGERDUTY -->|"Compliance alerts"| COMPLIANCE_ONCALL

    SRE_ONCALL --> RB5
    ENG_ONCALL --> RB1 & RB2 & RB3 & RB6
    COMPLIANCE_ONCALL --> RB4

    style SOURCES fill:#0d1117,color:#c9d1d9,stroke:#30363d
    style COLLECTION fill:#0d2137,color:#79c0ff,stroke:#1f6feb
    style STORE fill:#1a2a1a,color:#7ee787,stroke:#238636
    style DASHBOARDS fill:#2d1a2d,color:#d2a8ff,stroke:#8b949e
    style ALERTING fill:#2d1a1a,color:#ff7b72,stroke:#da3633
    style ONCALL fill:#2d2d0d,color:#e3b341,stroke:#9e6a03
    style RUNBOOKS fill:#1a1a2d,color:#58a6ff,stroke:#388bfd
```

---

## SLI / SLO Definitions

| SLI | Measurement | SLO Target | Error Budget (30d) |
|-----|------------|-----------|-------------------|
| **Objective Success Rate** | % objectives reaching Completed state | ≥ 85% | 15% failure budget |
| **API Availability** | % successful HTTP responses (non-5xx) | ≥ 99.5% | 3.6 hours/month |
| **Objective Intake Latency** | P95 time from input → Validating state | ≤ 30 seconds | — |
| **Governance Decision Latency** | P99 OPA evaluation time | ≤ 500 ms | — |
| **LLM Availability** | % LLM requests that succeed or fallback | ≥ 95% | 5% failure budget |
| **Dashboard Load Time** | P90 initial page load | ≤ 1.5 seconds | — |
| **Budget Accuracy** | Actual spend within ±20% of forecast | ≥ 80% | 20% variance budget |
| **Audit Completeness** | % actions with corresponding audit records | 100% | 0% (hard requirement) |
| **Governance Compliance Rate** | % executions passing all OPA policies | ≥ 99% | 1% exception budget |

---

## Alert Severity Definitions

| Priority | Severity | Response SLA | Examples |
|---------|---------|-------------|---------|
| P1 | Critical | 5 minutes | API down · DB down · Governance engine down |
| P2 | High | 30 minutes | SLO burn rate > 5x · LLM offline > 10 min · Budget spike > 200% |
| P3 | Medium | 4 hours | Agent loop timeout · Objective stuck > 24h · LLM latency high |
| P4 | Low | Next business day | Dependency-Track vulnerability · State file write failure |

---

## Key Metrics Reference

| Metric | Type | Label | Alert Threshold |
|--------|------|-------|----------------|
| `uawos_objective_health_score` | Gauge | `objective_id` | < 40 → P3 alert |
| `uawos_api_request_duration_seconds` | Histogram | `endpoint` | P95 > 5s → P2 |
| `uawos_agent_loop_timeout_total` | Counter | `agent_type` | > 5/hour → P3 |
| `uawos_budget_variance_ratio` | Gauge | `objective_id` | > 1.2 → P3, > 2.0 → P2 |
| `uawos_governance_policy_violation_total` | Counter | `policy_id` | > 0 → immediate alert |
| `uawos_llm_error_rate` | Gauge | `model` | > 0.1 → P2 |
| `uawos_objective_completion_rate_7d` | Gauge | — | < 0.7 → P3 |
| `uawos_audit_log_gap_seconds` | Gauge | `component` | > 60s → P1 |

---

## Runbook Quick Reference

| Runbook | Trigger | First Action |
|---------|---------|-------------|
| RB-001 | Objective stuck > 24h | Check dependency graph for cycles → `GET /api/objective/conflicts` |
| RB-002 | Agent loop > 30 min | Kill Temporal workflow → restart executor agent |
| RB-003 | Budget spike alert | Check `uawos_budget_state.json` → identify token-expensive model → throttle |
| RB-004 | Policy violation | Review OPA trace → submit exception request via Governance UI |
| RB-005 | PostgreSQL down | Check Docker container health → failover to read replica → alert SRE |
| RB-006 | LLM offline | Confirm heuristic fallback active → switch model in LiteLLM config → drain queue |

---

*Source: `Requirements Master/file.pdf` · `OTDTS.md` · `uawos_observability.py` · `uawos_governance.py`*
