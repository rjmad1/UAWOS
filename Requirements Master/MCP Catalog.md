# Universal AI Workforce Operating System (UAWOS)

# MCP Catalog

## Version

1.0

## Status

Normative Catalog Specification

---

# 1. Purpose

This catalog defines the expanded Model Context Protocol (MCP) server ecosystem for UAWOS. All MCP integrations SHALL route through the **UAWOS MCP Gateway** and comply with the governance rules defined in the [Integration, Tooling & MCP Standard (ITMS)](file:///c:/Users/rajaj/Projects/UAWOS/Requirements%20Master/Integration,%20Tooling%20&%20MCP%20Standard%20(ITMS).md).

---

# 2. Expanded MCP Servers Catalog

## 2.1. Engineering Servers

### GitLab MCP
* **Purpose**: Issue tracking, merge request management, pipeline trigger execution, and repository search.
* **Scope**: Ingest GitLab API client.
* **Trust Requirement**: High (requires personal access token governance).

### Bitbucket MCP
* **Purpose**: Code reviews, commit analysis, and pull request audits in Bitbucket server environments.
* **Scope**: Ingest Bitbucket REST API adapter.
* **Trust Requirement**: High.

### SonarQube MCP
* **Purpose**: Fetch code quality gates, code smell reports, security hotspots, and static analysis metrics.
* **Scope**: Ingest SonarQube quality query tools.
* **Trust Requirement**: Medium.

### Jenkins MCP
* **Purpose**: Retrieve build statuses, trigger test execution, and query automation logs.
* **Scope**: Ingest Jenkins API client.
* **Trust Requirement**: High (Write capabilities restricted to approved release pathways).

---

## 2.2. Documentation Servers

### Confluence MCP
* **Purpose**: Create pages, read project spaces, update specifications, and catalog team documents.
* **Scope**: Ingest Confluence REST client.
* **Trust Requirement**: High.

### Notion MCP
* **Purpose**: Query team databases, modify workspace pages, and extract team wiki outlines.
* **Scope**: Ingest Notion client SDK.
* **Trust Requirement**: Medium.

### Docusaurus MCP
* **Purpose**: Parse documentation structures and auto-generate sidebar configurations.
* **Scope**: Ingest Local static-site configuration tool.
* **Trust Requirement**: Low (read-only).

---

## 2.3. Architecture Servers

### Mermaid MCP
* **Purpose**: Transform plain-text descriptions into Mermaid schema strings and compile Mermaid diagrams to SVG/PNG.
* **Scope**: Ingest Mermaid-CLI rendering pipeline.
* **Trust Requirement**: Low.

### PlantUML MCP
* **Purpose**: Compile UML sequence, class, and component diagrams from PlantUML text structures.
* **Scope**: Ingest Local PlantUML jar server.
* **Trust Requirement**: Low.

---

## 2.4. Cloud Servers

### AWS MCP
* **Purpose**: Read-only asset discovery, cost audits, resource status checks, and CloudWatch metrics tracking.
* **Scope**: Ingest AWS Boto3 adapter.
* **Trust Requirement**: Very High (strict read-only role mapping).

### Azure MCP
* **Purpose**: Resource group audits, VM tracking, and resource tagging.
* **Scope**: Ingest Azure SDK wrapper.
* **Trust Requirement**: Very High.

### Terraform MCP
* **Purpose**: Run plan executions, scan TF state files, and analyze drift in configured infrastructure.
* **Scope**: Ingest Terraform CLI wrapper.
* **Trust Requirement**: Critical (State write locks require strategic approval).

---

## 2.5. Data Servers

### Redis MCP
* **Purpose**: Query cache metrics, flush transient keys, and read session state data during testing.
* **Scope**: Ingest Redis client.
* **Trust Requirement**: High (protected keys hidden).

### Kafka MCP
* **Purpose**: Consume topic events, verify schema registry mappings, and monitor lag across consumers.
* **Scope**: Ingest Kafka Admin client.
* **Trust Requirement**: Critical.

### ClickHouse MCP
* **Purpose**: Run high-speed analytical queries and pull system utilization logs.
* **Scope**: Ingest ClickHouse client.
* **Trust Requirement**: High.

### OpenSearch MCP
* **Purpose**: Perform semantic searches, index metadata documents, and check search node cluster health.
* **Scope**: Ingest OpenSearch REST client.
* **Trust Requirement**: High.

### Neo4j MCP
* **Purpose**: Read/write knowledge graph nodes, traversals, and ontology relationships.
* **Scope**: Ingest Neo4j driver.
* **Trust Requirement**: Critical (Core to the Knowledge Graph Layer).

---

## 2.6. Collaboration Servers

### Slack MCP
* **Purpose**: Post execution logs, ping human owners for approvals, and receive incoming commands.
* **Scope**: Ingest Slack WebClient.
* **Trust Requirement**: High (strictly governed by channel policies).

### Teams MCP
* **Purpose**: Post cards to Teams channels, fetch incoming conversation context, and trigger alerts.
* **Scope**: Ingest Microsoft Graph client.
* **Trust Requirement**: High.

### Discord MCP
* **Purpose**: Direct alerts to developer channels and fetch community feedback inputs.
* **Scope**: Ingest Discord API client.
* **Trust Requirement**: Medium.

---

# 3. Registry Registration & Governance Rules

All MCP servers listed in this catalog MUST be registered inside the UAWOS MCP Registry database.
* **Read / Write Isolation**: Every tool exposed by an MCP Server is designated as either `READ` or `WRITE`. All `WRITE` tools (such as sending a Slack message, editing Confluence, or triggering a Jenkins build) MUST be evaluated by the Policy Engine (OPA) and require human authorization if their risk profile exceeds Level 2.
* **Audit Trail**: The UAWOS MCP Gateway logs all tool payloads, timestamps, calling agents, and execution return statuses into the immutable ClickHouse audit ledger.
