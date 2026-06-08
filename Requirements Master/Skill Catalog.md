# Universal AI Workforce Operating System (UAWOS)

# Skill Catalog

## Version

1.0

## Status

Normative Catalog Specification

---

# 1. Purpose

This catalog defines the standardized skills, capability taxonomies, execution cost boundaries, and system dependencies for human and AI workforce entities within UAWOS. It aligns with the SkillOpt integration specifications defined in the [Workforce, Agent & Autonomy Standard (WAAS)](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/Workforce,%20Agent%20&%20Autonomy%20Standard%20(WAAS).md).

---

# 2. Skill Classification & Cost Boundaries

Every skill registered inside the Skill Registry is classified by domain, complexity, and resource footprint:

## 2.1. Core Platform Skills

| Skill ID | Name | Category | Primary Dependency | Cost Class (Financial / Token / Compute) | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SKL-AI-01** | Prompt Tuning | AI Engineering | DSPy | Low (Tokens only) | Auto-optimizes and compiles prompt templates based on performance data. |
| **SKL-AI-02** | Structural Parsing | AI Engineering | Instructor | Low (Local CPU) | Extracts validated JSON output matching a specific Pydantic schema. |
| **SKL-RAG-01**| Dense Retrieval | Knowledge / RAG | FastEmbed, Qdrant | Low (Compute) | Generates dense embeddings and retrieves matching document snippets. |
| **SKL-RAG-02**| Graph Traversal | Knowledge / RAG | Neo4j MCP | Medium (Neo4j DB) | Traverses ontology relationships to resolve cross-entity context. |
| **SKL-DOC-01**| C4 Architecture | Design / Docs | Structurizr, Mermaid | Low (Mermaid rendering) | Synthesizes plain text requirements into C4 architectural diagrams. |
| **SKL-SEC-01**| Vulnerability Audit| Security | Trivy, Grype | Medium (CPU scan time) | Scans container images and SBOM records for registered CVE database entries. |
| **SKL-DAT-01**| Analytical Transform| Data Engineering | dbt-core, ClickHouse | High (Query Compute) | Runs analytical transformations on raw logs to output value maps. |
| **SKL-SIM-01**| Monte Carlo Run | Simulation | Mesa, NetworkX | High (Compute intensive) | Runs simulated agent portfolio execution pathways to predict outcomes. |
| **SKL-GOV-01**| Lineage Audit | Governance | OpenLineage, Marquez | Medium | Audits data movements from source database to destination graphs. |

## 2.2. Community / Imported Skills (Claude Directory)

These skills are imported from [Claude Directory](https://www.claudedirectory.org/) and saved locally in [Requirements Master/claudedirectory_imports/skills/](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/).

| Skill ID | Name | Category | Primary Dependency | Cost Class | Description | Link |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SKL-DIR-01** | refactor | Software Engineering | None | Low | Automated code refactoring and optimization. | [refactor.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/refactor.md) |
| **SKL-DIR-02** | sql-optimizer | Database Engineering | PostgreSQL | Low | Optimizes SQL query performance and indexes. | [sql-optimizer.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/sql-optimizer.md) |
| **SKL-DIR-03** | api-docs | Documentation | OpenAPI | Low | Generates OpenAPI / Swagger docs from code. | [api-docs.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/api-docs.md) |
| **SKL-DIR-04** | architecture-diagram | Design / Docs | Mermaid | Low | Generates Mermaid diagrams from text descriptions. | [architecture-diagram.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/architecture-diagram.md) |
| **SKL-DIR-05** | changelog | Version Control | git | Low | Generates structured changelogs from git history. | [changelog.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/changelog.md) |
| **SKL-DIR-06** | code-walkthrough | Documentation | None | Low | Explains code sections in plain natural language. | [code-walkthrough.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/code-walkthrough.md) |
| **SKL-DIR-07** | test-gen | Quality Engineering | pytest / jest | Low | Generates unit tests for code components. | [test-gen.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/test-gen.md) |
| **SKL-DIR-08** | webapp-testing | Quality Engineering | Playwright | Medium | Formulates and runs end-to-end web app tests. | [webapp-testing.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/webapp-testing.md) |
| **SKL-DIR-09** | playwright-skill | Quality Engineering | Playwright | Medium | Drives browser actions for functional testing. | [playwright-skill.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/playwright-skill.md) |
| **SKL-DIR-10** | security-audit | Security | Semgrep | Medium | Runs static analysis checks for OWASP Top 10. | [security-audit.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/security-audit.md) |
| **SKL-DIR-11** | deps-audit | Security | Dependency-Track | Medium | Audits project dependencies for CVEs. | [deps-audit.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/deps-audit.md) |
| **SKL-DIR-12** | docker-compose | Infrastructure | Docker | Medium | Generates and verifies multi-container layouts. | [docker-compose.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/docker-compose.md) |
| **SKL-DIR-13** | env-setup | Infrastructure | None | Low | Automates setup of virtual environments. | [env-setup.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/env-setup.md) |
| **SKL-DIR-14** | git-bisect | Software Engineering | git | Low | Automates git bisect runs to isolate bugs. | [git-bisect.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/git-bisect.md) |
| **SKL-DIR-15** | migrate-db | Database Engineering | PostgreSQL | Medium | Designs and verifies database schema migrations. | [migrate-db.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/migrate-db.md) |
| **SKL-DIR-16** | monorepo-manager | Software Engineering | None | Low | Manages monorepo dependencies and boundaries. | [monorepo-manager.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/monorepo-manager.md) |
| **SKL-DIR-17** | perf-benchmark | Quality Engineering | None | Medium | Runs load tests and micro-benchmarks. | [perf-benchmark.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/perf-benchmark.md) |
| **SKL-DIR-18** | superpowers-executing-plans | Strategy / Execution | None | Low | Coordinates subagents to execute plans. | [superpowers-executing-plans.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/superpowers-executing-plans.md) |
| **SKL-DIR-19** | superpowers-subagent-driven-development | Agent Engineering | None | Medium | Delegates tasks to specialized subagents. | [superpowers-subagent-driven-development.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/superpowers-subagent-driven-development.md) |
| **SKL-DIR-20** | superpowers-test-driven-development | Quality Engineering | None | Low | Runs red-green-refactor loops. | [superpowers-test-driven-development.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/superpowers-test-driven-development.md) |
| **SKL-DIR-21** | superpowers-verification-before-completion | Quality Engineering | None | Low | Validates implementation against plan before finish. | [superpowers-verification-before-completion.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/superpowers-verification-before-completion.md) |
| **SKL-DIR-22** | superpowers-writing-plans | Strategy / Execution | None | Low | Generates detailed implementation plans. | [superpowers-writing-plans.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/superpowers-writing-plans.md) |
| **SKL-DIR-23** | superpowers-writing-skills | Agent Engineering | None | Low | Authoring new reusable agent skills. | [superpowers-writing-skills.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/superpowers-writing-skills.md) |
| **SKL-DIR-24** | superpowers-using-git-worktrees | Software Engineering | git | Low | Manages parallel branches cleanly via worktrees. | [superpowers-using-git-worktrees.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/superpowers-using-git-worktrees.md) |
| **SKL-DIR-25** | web-asset-generator | Design / UI | None | Low | Generates UI assets, styling, and graphics. | [web-asset-generator.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/web-asset-generator.md) |
| **SKL-DIR-26** | d3js-visualization | Design / UI | D3.js | Low | Builds rich, interactive data visualizations. | [d3js-visualization.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/d3js-visualization.md) |
| **SKL-DIR-27** | skills-frontend-design | Design / UI | CSS / React | Low | Codes premium, responsive, and beautiful layouts. | [skills-frontend-design.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/claudedirectory_imports/skills/skills-frontend-design.md) |

---

# 3. Execution Cost Boundaries

To prevent run-away agent processing fees or resource depletion, UAWOS enforces the following execution limits:
* **Token Budget limits**: High-cost skills (e.g., `SKL-SIM-01`) must have a predefined maximum token consumption threshold per invocation (e.g., 200k input/output tokens).
* **Financial Cap controls**: Any agent executing a workflow utilizing a high-cost skill must verify available budget allocations inside the `Resource Graph` prior to execution.
* **Compute Bounds**: Tasks requiring high local CPU/GPU usage (e.g., `SKL-SEC-01` dependency scanning or heavy embedding generation) are queued and throttled to prevent platform performance degradation.

---

# 4. Registration & Validation Standards

A capability is registered inside the Skill Registry by providing a standardized Skill Specification file (`SKILL.md`) inside the local directory.
Every skill registration must pass:
1. **Schema Check**: Validates input-output parameters and JSON structures.
2. **License Scan**: Confirms dependencies do not violate license constraints (e.g., no AGPL libraries).
3. **Trust Score Initialization**: Starts at a default baseline (0.70) and is dynamically updated on every execution based on error rates and outputs.
