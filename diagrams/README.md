# UAWOS System Diagrams

> **Universal AI Workforce Operating System**  
> Minimal System Diagram Set — derived from the Engineering Standards PDF  
> Version: 1.0 | Status: Baseline

This folder contains the **8 canonical system diagrams** required to communicate the UAWOS platform architecture across Product, Architecture, QA, DevOps, SRE, Design, and Engineering teams.

All diagrams follow the fields, conventions, and anti-patterns defined in the standards PDF: `Requirements Master/file.pdf`.

---

## Diagram Index

| # | File | Diagram Type | Primary Audiences |
|---|------|-------------|-------------------|
| 1 | [01-system-context.md](01-system-context.md) | System Context (C4-L1) | Product · Design · Architecture · QA · SRE |
| 2 | [02-container-diagram.md](02-container-diagram.md) | Container (C4-L2) | Architecture · Engineering · QA · SRE · DevOps |
| 3 | [03-e2e-sequence.md](03-e2e-sequence.md) | E2E Sequence (Happy Path) | QA · Engineering · SRE · Product |
| 4 | [04-domain-model.md](04-domain-model.md) | Domain Model (Bounded Context + Entities) | Product · Engineering · Architecture · QA |
| 5 | [05-state-machine.md](05-state-machine.md) | State Machine (Objective Lifecycle) | QA · SRE · Product · Engineering |
| 6 | [06-data-flow.md](06-data-flow.md) | Data Flow (PII + Trust Boundaries) | SRE · DevOps · QA · Architecture · Product |
| 7 | [07-deployment-architecture.md](07-deployment-architecture.md) | Deployment Architecture | DevOps · SRE · Engineering · QA |
| 8 | [08-observability-operations.md](08-observability-operations.md) | Observability + Operations | SRE · DevOps · Engineering |

---

## How to Read These Diagrams

All diagrams are written in **Mermaid** markdown format, which renders natively in:
- GitHub (Markdown files, Wikis, PRs)
- VS Code (with Mermaid extension)
- Notion, Confluence, Linear (via plugins)

Each diagram file includes:
1. **Purpose** — What question this diagram answers
2. **Scope** — What is in/out of scope
3. **Common Mistakes** — Anti-patterns to avoid (from standards PDF)
4. **Most Useful For** — Target teams and use cases
5. **The Diagram** — Rich Mermaid source

---

## Source Standard

Derived from: `Requirements Master/file.pdf`  
Architecture baseline: `Requirements Master/Architecture Definition Document (ADD).md`  
Reference architecture: `Requirements Master/Reference Architecture Standard (RAS).md`
