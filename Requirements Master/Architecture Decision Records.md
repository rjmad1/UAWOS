# Universal AI Workforce Operating System (UAWOS)

# Architecture Decision Records (ADRs)

This document contains the formal Architecture Decision Records for the Delta Ecosystem Discovery & Acceleration Layer of the Universal AI Workforce Operating System (UAWOS).

---

# ADR-001: Rejection of AGPLv3 Metabase for BI & Analytics Layer

## Status
Approved

## Context
UAWOS requires a Business Intelligence (BI) and Analytics tool to render execution metrics, visualize portfolio statuses, and expose value dashboards. The user suggested evaluating **Metabase** (https://github.com/metabase/metabase) as a potential candidate. 

However, Metabase is primarily licensed under the **AGPLv3** (GNU Affero General Public License version 3). The AGPLv3 contains strong copyleft provisions that trigger source disclosure requirements if any part of the platform interacts with it over a network.

## Decision
We **REJECT** Metabase due to its AGPLv3 license. 

To replace Metabase, we **ADOPT** **Apache Superset** (Apache 2.0 license) for interactive dashboarding and enterprise-grade charts. Additionally, we **ADOPT** **Evidence** (MIT license) as an analytics-as-code solution for compiling markdown reports from SQL queries.

## Consequences
* **IP Protection**: Prevents any risk of copyleft pollution to UAWOS core IP.
* **Service Orchestration**: Apache Superset and Evidence are added to the [docker-compose.yml](file:///c:/Users/rajaj/Projects/UAWOS/docker-compose.yml) and [requirements.txt](file:///c:/Users/rajaj/Projects/UAWOS/requirements.txt) files.
* **Compliance**: Aligns with the [Governance Catalog.md](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/Governance%20Catalog.md) licensing rules.

---

# ADR-002: Wrapping GPLv3 Marker for PDF Parsing

## Status
Approved

## Context
Evaluating document ingestion tools highlighted **Marker** (https://github.com/VikParuchuri/marker) as a high-accuracy PDF-to-Markdown parser. However, Marker is licensed under **GPLv3**, which has copyleft restrictions if compiled/imported directly into UAWOS Python execution environments.

## Decision
We **WRAP** Marker. It must never be imported as a Python package inside UAWOS source code. Instead, Marker is deployed as a standalone REST API microservice inside an isolated container. Communication with it occurs exclusively via HTTP endpoints.

## Consequences
* **Legal Isolation**: Keeps GPLv3 code separated from the core platform codebase.
* **Alternate Framework**: For standard PDF ingestion, we prioritize **Unstructured** (Apache 2.0) and **LlamaIndex** parser plugins.

---

# ADR-003: Ingesting Graphiti and Mem0 for Memory Architecture

## Status
Approved

## Context
AI agents need to store long-term memory, session state, and event relationships. Custom development of memory graph stores would require significant engineering effort.

## Decision
We **ADOPT** **Mem0** (Apache 2.0) for long-term user profile and session memory, and **Graphiti** (Apache 2.0) for temporal knowledge graph indexing. 

## Consequences
* **Reduced Effort**: Eliminates the need to construct graph-based memory storage structures from scratch.
* **Integration**: Memory states are synchronized to the Neo4j Graph Database via the Neo4j MCP.
