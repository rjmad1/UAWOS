# Universal AI Workforce Operating System (UAWOS)

# OSS Ecosystem Catalog

## Version

1.0

## Status

Normative Catalog Specification

---

# 1. Executive Summary

This catalog contains the comprehensive architectural qualification, license assessment, security profile, operational burden evaluation, and adoption recommendations for the open-source software (OSS) and third-party systems evaluated for inclusion in the UAWOS core. All evaluations adhere to the **ADOPT → EXTEND → WRAP → FORK → BUILD** hierarchy defined in the [Bootstrap Directive (BD)](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/Bootstrap%20Directive%20(BD).md).

---

# 2. Rejection & Anti-Pattern Filters

Every candidate listed below has been screened against the following constitutional constraints:
* **AGPL Rejection**: Explicitly filters out AGPL licenses to protect UAWOS proprietary IP boundaries.
* **SaaS Lock-in Rejection**: Rejects tools requiring non-local hosting or SaaS-only access models.
* **Maintenance Rating**: Flags repositories with inactive maintainers (no releases/commits in >6 months) or single-maintainer dependencies.
* **Capability Duplication**: Avoids adding libraries that duplicate existing baseline engines.

---

# 3. Layer Evaluation Matrices

## 3.1. Architecture Knowledge & OSS Discovery Layer
*Automating software composition analysis, supply-chain governance, and repo scoring.*

| Repository | License | Maintenance / Activity | Security Review (CVEs) | Decision | Rationale / Integration Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OSS Review Toolkit (ORT)** | Apache 2.0 | High (Active) | Low Risk | **ADOPT** | Used in the CI/CD pipeline to automate software compliance audits. |
| **Scorecard (OpenSSF)** | Apache 2.0 | Very High (OpenSSF) | Negligible | **ADOPT** | Integrated into the Governance Engine to automatically score third-party repo risks. |
| **Dependency-Track** | Apache 2.0 | High | Low Risk | **WRAP** | Implemented as a containerized service to aggregate and analyze generated SBOMs. |
| **Syft** | Apache 2.0 | Very High (Anchore) | Negligible | **ADOPT** | Run in build pipelines to generate project Software Bills of Materials (SBOMs). |
| **Grype** | Apache 2.0 | Very High (Anchore) | Negligible | **ADOPT** | Ingested as the default local scanner for finding vulnerabilities in container images and SBOMs. |

---

## 3.2. AI Engineering Platform Layer
*Accelerating typed agent construction, prompt optimization, and controlled reasoning.*

| Repository | License | Maintenance / Activity | Security Review (CVEs) | Decision | Rationale / Integration Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Pydantic AI** | MIT | High (Pydantic team) | Negligible | **ADOPT** | Core platform framework for type-safe agent construction and structural messaging. |
| **DSPy** | MIT | Very High (Stanford) | Negligible | **ADOPT** | Adopted for automated prompt and weight compilation inside the Skill Optimization Layer. |
| **Instructor** | MIT | High | Negligible | **ADOPT** | Used for JSON schema enforcement and structured output extraction from LLMs. |
| **Outlines** | Apache 2.0 | High | Negligible | **ADOPT** | Adopted for constrained text generation (regex, schemas) at the lowest LLM token level. |
| **Guidance** | MIT | Moderate (Microsoft) | Negligible | **WRAP** | Wrapped for complex sequential reasoning patterns and multi-modal guidance orchestration. |

---

## 3.3. Agent Memory Layer
*Providing session memory and temporal knowledge graphs.*

| Repository | License | Maintenance / Activity | Security Review (CVEs) | Decision | Rationale / Integration Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mem0** | Apache 2.0 | High | Low Risk | **ADOPT** | Adopted for user and session long-term memory management. |
| **Zep** | Apache 2.0 (SDK) | Moderate (Commercial SaaS focus) | Low Risk | **WRAP** | SDK adopted; back-end container is wrapped locally. Enterprise SaaS capabilities are rejected. |
| **Graphiti** | Apache 2.0 | High (Zep) | Negligible | **ADOPT** | Primary local engine for temporal knowledge graph representation of memory. |

---

## 3.4. RAG & Knowledge Layer
*Accelerating retrieval architecture, local embeddings, and document parsing.*

| Repository | License | Maintenance / Activity | Security Review (CVEs) | Decision | Rationale / Integration Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Haystack** | Apache 2.0 | High (Deepset) | Low Risk | **ADOPT** | Core enterprise retrieval pipelines and document ingestion orchestrations. |
| **LlamaIndex** | MIT | Very High | Low Risk | **ADOPT** | Used for structured data indexing and document-to-graph transformations. |
| **FastEmbed** | Apache 2.0 | High (Qdrant) | Negligible | **ADOPT** | Lightweight CPU-first embedding generation in local agent sandboxes. |
| **Unstructured** | Apache 2.0 | High | Moderate (Heavy deps) | **WRAP** | Wrapped as a separate local service due to heavy OS-level dependencies. |
| **Marker** | GPLv3 | High | Negligible | **WRAP / ISOLATE** | **WARNING**: Contains GPLv3 copyleft license. Must be isolated as a standalone container, never imported as a direct dependency. |

---

## 3.5. UI/UX Acceleration Layer
*Reducing frontend implementation effort.*

| Component | License | Maintenance / Type | Decision | Rationale / Integration Path |
| :--- | :--- | :--- | :--- | :--- |
| **v0.dev** | SaaS | Proprietary (Vercel) | **WRAP** | Used as an external developer utility; components generated are copy-pasted under MIT. No SaaS runtime link. |
| **21st.dev** | MIT | Community Registry | **ADOPT** | Library of copy-paste Tailwind/React primitives for the developer portal. |
| **Magic UI** | MIT | Active | **ADOPT** | Component library for landing, metrics, and visualization overlays. |
| **Aceternity UI** | MIT | Active | **ADOPT** | UI components for visual dashboards and portal landing screens. |
| **shadcn/ui** | MIT | High | **ADOPT** | Foundation UI layer. Copied directly into the codebase to prevent dependency lock-in. |
| **React Flow** | MIT | High | **ADOPT** | Primary library for rendering the Objective and Policy Graphs in the UI. |
| **Excalidraw** | MIT | Active | **WRAP** | Embedded as a canvas wrapper for human collaborative modeling and wireframing. |

---

## 3.6. Design System Layer
*Syncing tokens from designs to production.*

| Repository | License | Maintenance / Activity | Decision | Rationale / Integration Path |
| :--- | :--- | :--- | :--- | :--- |
| **Figma API** | SaaS | Proprietary | **WRAP** | Implemented as a token extractor script used during design hand-offs. |
| **Style Dictionary** | Apache 2.0 | Active (Amazon) | **ADOPT** | Automated design token compilation from Figma JSON into CSS/JS variables. |

---

## 3.7. Documentation Automation Layer
*Publishing portal pages, reference designs, and specifications.*

| Repository | License | Maintenance / Activity | Decision | Rationale / Integration Path |
| :--- | :--- | :--- | :--- | :--- |
| **Docusaurus** | MIT | Active (Meta) | **ADOPT** | Developer portal framework. Integrates dynamically with the service catalog. |
| **MkDocs Material** | MIT | Active | **ADOPT** | Used for developer specifications and API reference docs. |
| **Mermaid** | MIT | High | **ADOPT** | Ingested for auto-generating sequence, flowchart, and workflow diagrams. |
| **Structurizr** | Apache 2.0 | Moderate | **WRAP** | Wrapped Java/CLI utility to export C4 models into Mermaid markup. |
| **Backstage TechDocs** | Apache 2.0 | High (Spotify) | **EXTEND** | Integrated directly into the Backstage portal instance. |

---

## 3.8. Security Automation Layer
*Static and runtime vulnerability screening.*

| Repository | License | Maintenance / Activity | Decision | Rationale / Integration Path |
| :--- | :--- | :--- | :--- | :--- |
| **Semgrep** | LGPL 2.1 | Active | **ADOPT** | Integrated into local git hooks and CI/CD pipelines. |
| **Trivy** | Apache 2.0 | Active (Aquasecurity) | **ADOPT** | Runs automatically on built containers in target CI workflows. |
| **OWASP Dep Check** | Apache 2.0 | Active | **ADOPT** | Used in CI/CD build scripts to scan npm/pip dependencies. |
| **Gitleaks** | MIT | Active | **ADOPT** | Pre-commit hook and build-step secret scanning scanner. |
| **Falco** | Apache 2.0 | Active (CNCF) | **WRAP** | Installed on runtime hosts to detect anomalous security behavior. |

---

## 3.9. Data Engineering Layer
*Data ingestion pipelines, transforms, and databases.*

| Repository | License | Maintenance / Activity | Decision | Rationale / Integration Path |
| :--- | :--- | :--- | :--- | :--- |
| **Airbyte** | ELv2 | High | **WRAP** | Run in isolated containers to replicate database sources into RAG vector layers. |
| **dbt-core** | Apache 2.0 | Active | **ADOPT** | Standard for data transformation and modeling within the Value Engine. |
| **Meltano** | MIT | Active | **WRAP** | Wrapped for declarative ELT pipeline scheduling and tool execution. |
| **ClickHouse** | Apache 2.0 | Very High | **WRAP** | Primary analytical store for events and long-term logs. |

---

## 3.10. Analytics & BI Layer
*Business intelligence and metric analytics.*

| Repository | License | Maintenance / Activity | Decision | Rationale / Integration Path |
| :--- | :--- | :--- | :--- | :--- |
| **Metabase** | AGPLv3 | High | **REJECT** | **REJECTED**: AGPLv3 copyleft license poses severe proprietary code integration risks. |
| **Apache Superset** | Apache 2.0 | High (ASF) | **ADOPT** | Approved BI platform. Ingested to replace Metabase. |
| **Evidence** | MIT | Active | **ADOPT** | Analytics-as-code generator for rendering markdown value reports. |

---

## 3.11. Digital Twin & Simulation Layer
*Modeling complex workforce, portfolio, and graph dynamics.*

| Repository | License | Maintenance / Activity | Decision | Rationale / Integration Path |
| :--- | :--- | :--- | :--- | :--- |
| **Mesa** | Apache 2.0 | Active | **ADOPT** | Core agent simulation library inside the Simulation Engine. |
| **AnyLogic Refs** | N/A | Proprietary | **BUILD** | Rejected for direct use due to proprietary license. Reference design patterns only. |
| **NetworkX** | BSD-3 | High | **ADOPT** | Primary python package for offline graph analysis and path routing simulations. |

---

## 3.12. Governance Intelligence Layer
*Data lineage mapping, lineage visuals, and cataloging.*

| Repository | License | Maintenance / Activity | Decision | Rationale / Integration Path |
| :--- | :--- | :--- | :--- | :--- |
| **OpenLineage** | Apache 2.0 | High | **ADOPT** | Client integrations embedded in dbt and execution hooks. |
| **Marquez** | Apache 2.0 | High | **ADOPT** | Used as the metadata storage back-end and interface for lineage charts. |
| **OpenMetadata** | Apache 2.0 | High | **WRAP** | Integrated as a standalone metadata server to catalog all assets. |

---

## 3.13. Free Intelligence APIs
*Connecting adapters to qualified intelligence endpoints.*

* **GitHub API** (REST/GraphQL): Wrapper created to query repo statistics and developer metadata.
* **Libraries.io API**: Wrapper created to retrieve dependency health and licensing data dynamically.
* **Ecosyste.ms API**: Adapter configured to check package metadata across registries.
* **OSV (Open Source Vulnerabilities) API**: Native connection built into Governance checking to retrieve CVEs.
* **NVD (National Vulnerability Database) API**: Backup vulnerability source wrapper.
* **CISA KEV (Known Exploited Vulnerabilities) API**: Ingested feed for highlighting highly exploitable system bugs.
* **Wikidata API & DBpedia**: Adapters to retrieve general ontological references for the Knowledge Engine.
* **Tavily / Serper API**: Search API adapters for the Discovery Engine search loops.
* **npm Registry / PyPI / Maven Central APIs**: Native adapters inside package verification pipelines.

---

# 4. Invalidation & Governance Controls

All adopted components listed above must be scanned by the CI/CD pipeline on every commit. Any version updates containing license changes (such as shifting to AGPL or SSPL) SHALL trigger a CI build block and require Strategist review.
