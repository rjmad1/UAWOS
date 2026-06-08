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
