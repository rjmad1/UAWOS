# Diagram 6 — Data Flow Diagram (PII + Trust Boundaries)

## Purpose
Establishes security/compliance truth — where PII data lives, who can access it, where it is encrypted, and how audit logging flows across the system.

## Questions This Diagram Answers
- Where is PII stored in the system?
- Who can access sensitive data?
- Where do we encrypt in-transit vs. at-rest?
- Where are retention/deletion flows defined?
- What are the trust boundaries between components?

## Scope
**In scope:** All data flows carrying PII or sensitive information, encryption points, trust boundary crossings, audit logging paths  
**Out of scope:** Non-sensitive internal data flows (e.g., configuration reads), UI rendering pipelines

## Common Mistakes to Avoid
- ❌ Hand-wavy "data is secure" statements without labeling PII
- ❌ Not labeling retention/deletion flows
- ❌ Missing audit log entries at trust boundary crossings
- ❌ Assuming TLS = "encrypted" without specifying at-rest encryption

## Most Useful For
SRE · DevOps · QA · Architecture · Product

---

## Trust Boundary Definitions

| Zone | Trust Level | Description |
|------|------------|-------------|
| 🔴 External | Untrusted | External users, internet, third-party APIs |
| 🟡 Edge | Low Trust | API Gateway, ingress, Marker service |
| 🟢 Internal | Trusted | Core platform engines, governance plane |
| 🔵 Data Tier | Restricted | Databases, vector stores, graph stores |
| ⚫ Admin | High Trust | Audit systems, compliance dashboards |

---

## Data Flow Diagram

```mermaid
flowchart TB
    %% Trust Boundary: External
    subgraph EXT["🔴 External Zone — Untrusted"]
        User["👤 Operator / User\n[PII: name, email, org]"]
        EnterpriseAPI["🔗 Enterprise APIs\n[Jira, Slack, Salesforce]\n[PII: names, messages, tasks]"]
        LLMCloud["☁️ Cloud LLM APIs\n[Gemini, GPT-4]\n[⚠️ PII must be masked before sending]"]
    end

    %% Trust Boundary: Edge
    subgraph EDGE["🟡 Edge Zone — Low Trust"]
        TLS_In["🔒 TLS Termination\n[HTTPS/TLS 1.3]\n[Certificate: Let's Encrypt]"]
        APIServer["📡 API Server :8099\n[Input validation · Rate limiting]\n[Auth token validation via OpenFGA]"]
        MarkerSvc["📄 Marker Service :8084\n[PDF parsing · GPLv3 sandboxed]\n[NO PII logging · Isolated container]"]
    end

    %% Trust Boundary: Internal
    subgraph INTERNAL["🟢 Internal Plane — Trusted"]
        DTASE["🔄 DTASE Engine\n[Strips PII from raw input]\n[Masks names before LLM calls]\n[Generates structured artifacts]"]
        Governance["🛡️ Governance Engine\n[Policy eval · Approval mgmt]\n[Audit record generator]"]
        OPA["📋 OPA :8181\n[Rego policy evaluation]\n[No PII stored · Stateless]"]
        OpenFGA["🔑 OpenFGA :8083\n[Relationship-based AuthZ]\n[user_id referenced only · No PII stored]"]
        Planning["📈 Planning Engine\n[Works with objective_id only]\n[No raw PII stored]"]
        Orchestrator["⚙️ Orchestration Engine\n[Task dispatch · No PII storage]"]
        LLMLocal["🤖 LiteLLM / Ollama\n[Local inference only for sensitive data]\n[TinyLlama · DeepSeek — on-prem]"]
    end

    %% Trust Boundary: Data Tier
    subgraph DATA["🔵 Data Tier — Restricted Access"]
        direction LR
        Postgres["🗄️ PostgreSQL :5435\n[PII: user records, emails, names]\n[Encrypted at rest: AES-256]\n[TLS in-transit]\n[Retention: 7 years audit log]\n[30 days execution temp records]"]
        Neo4j["🕸️ Neo4j Graph\n[PII: agent profiles, user nodes]\n[Encrypted at rest]\n[Access: internal services only]"]
        Qdrant["🔮 Qdrant :6333\n[Memory vectors: may contain PII context]\n[Encrypted at rest]\n[TTL: per MemoryAsset.ttl field]\n[Deletion: on agent decommission]"]
        StateFiles["📁 State JSON Files\n[⚠️ RISK: No encryption at rest]\n[PII exposure risk]\n[Migration → PostgreSQL required]"]
    end

    %% Trust Boundary: Admin / Compliance
    subgraph ADMIN["⚫ Admin Zone — High Trust"]
        Marquez["📊 Marquez / OpenLineage :5000\n[Execution lineage · NO PII]\n[objective_id · agent_id references only]"]
        Superset["📉 Superset :8088\n[Aggregated metrics only]\n[No PII in dashboards]\n[Auth: admin role required]"]
        DepTrack["🔍 Dependency-Track :8081\n[SBOM · License audit]\n[No PII]"]
        AuditLog["📜 Audit Log\n[WHO · WHAT · WHEN · WHY]\n[Immutable · Tamper-evident]\n[PII references via user_id only]"]
    end

    %% External → Edge flows
    User -->|"HTTPS/TLS 1.3\n[Credentials, input text, documents]"| TLS_In
    EnterpriseAPI -->|"OAuth 2.0 / API Key\n[Webhook payloads]"| TLS_In
    TLS_In -->|"Decrypted internally"| APIServer

    %% Edge → Internal flows
    APIServer -->|"Validated request\n[JWT claims verified]"| DTASE
    APIServer -->|"PDF upload\n[Sandboxed · No outbound]"| MarkerSvc
    MarkerSvc -->|"Extracted text only\n[No PII metadata]"| DTASE

    %% DTASE PII handling
    DTASE -->|"⚠️ PII MASK applied\nbefore LLM call"| LLMLocal
    DTASE -->|"⚠️ PII MASK + anonymize\nfor cloud LLM"| LLMCloud
    DTASE -->|"Structured artifact\n[PII stripped]"| APIServer

    %% Governance flows
    APIServer -->|"Policy check request\n[No PII · uses entity IDs]"| Governance
    Governance -->|"Rego evaluation\n[Stateless]"| OPA
    Governance -->|"AuthZ check\n[user_id + resource_id only]"| OpenFGA
    Governance -->|"Audit record\n[user_id · action · timestamp · outcome]"| AuditLog

    %% Data Tier writes
    APIServer -->|"INSERT/UPDATE\n[PII: TLS in-transit · AES-256 at rest]"| Postgres
    DTASE -->|"Node creation\n[Entity refs only]"| Neo4j
    LLMLocal -->|"Embedding write\n[Vector + context · TTL set]"| Qdrant
    APIServer -->|"State writes\n[⚠️ UNENCRYPTED RISK]"| StateFiles

    %% Observability flows
    Orchestrator -->|"Lineage events\n[No PII · IDs only]"| Marquez
    Marquez -->|"Persists lineage"| Postgres
    Postgres -->|"Aggregated metrics\n[No row-level PII]"| Superset
    Postgres -->|"Dependency audit"| DepTrack

    %% Retention / deletion
    Postgres -->|"🗑️ DELETE after 30 days\ntemp execution records"| Postgres
    Qdrant -->|"🗑️ TTL-based expiry\nper MemoryAsset.ttl"| Qdrant

    %% Styling
    classDef pii fill:#8B0000,color:#fff,stroke:#ff6666
    classDef encrypted fill:#1a3a1a,color:#90EE90,stroke:#4aae4a
    classDef risk fill:#5c3a00,color:#FFD700,stroke:#FFA500
    classDef admin fill:#1a1a3a,color:#aaaaff,stroke:#5555aa
    classDef external fill:#3a0000,color:#ffaaaa,stroke:#aa0000

    class User,EnterpriseAPI external
    class Postgres,Neo4j,Qdrant encrypted
    class StateFiles risk
    class AuditLog,Marquez,Superset,DepTrack admin
    class LLMCloud pii
```

---

## PII Data Inventory

| Data Element | Classification | Stored In | Encrypted At Rest | Retention | Deletion Trigger |
|-------------|---------------|-----------|------------------|-----------|-----------------|
| User name / email | PII | PostgreSQL | ✅ AES-256 | 7 years (audit) | Account deletion |
| Objective content | Business Sensitive | PostgreSQL + Neo4j | ✅ | 7 years | Manual / archived |
| Memory vectors | Potentially PII | Qdrant | ✅ | Per `MemoryAsset.ttl` | Agent decommission |
| Audit log entries | Compliance | PostgreSQL | ✅ | 7 years | Never (immutable) |
| LLM prompts | Sensitive | LiteLLM (local only) | ✅ Local | Session only | End of session |
| State JSON files | Business | Filesystem | ❌ **RISK** | Indefinite | Manual |
| Lineage events | Internal | Marquez + PostgreSQL | ✅ | 90 days | Automated |

---

## Encryption Standards

| Location | In-Transit | At-Rest | Key Management |
|---------|-----------|---------|---------------|
| API Server | TLS 1.3 | N/A | Let's Encrypt |
| PostgreSQL | TLS | AES-256 | PostgreSQL pgcrypto |
| Neo4j | TLS | AES-256 | Native |
| Qdrant | TLS | AES-256 | Native |
| LLM Local | localhost only | OS-level | N/A |
| State JSON | ❌ None | ❌ None | **Requires migration** |

---

*Source: `Requirements Master/file.pdf` · `PRTCS.md` · `CIAS.md` · `uawos_governance.py` · `uawos_db.py`*
