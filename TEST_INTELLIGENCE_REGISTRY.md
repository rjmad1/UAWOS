# TEST_INTELLIGENCE_REGISTRY.md

## Repository Overview

### Last Updated
2026-06-12

### Total Tests
- Unit: 230
- Integration: 25
- E2E: 0
- Contract: 0
- Performance: 0
- Security: 4

### Coverage Health Score
50

### Redundant Tests Identified
2

### Candidate Tests For Removal
2

---

# TEST INVENTORY

## Test ID
TEST-001

### Name
Objective Intake & Parsing Tests (FR-011 to FR-016)

### Category
Unit

### Purpose
Validates objective parsing from voice, text, documents, transcripts, images, and APIs.

### Risk Covered
Miscalibrated text analysis or ingestion failure.

### Blast Radius

#### Services
- Objective Ingestion Service

#### APIs
- POST /api/dtase/analyze

#### Datastores
- None

#### User Journeys
- Objective Ingestion Journey

#### Downstream Systems
- Objective Engine


### Criticality
High

### Failure Impact
High

### Maintenance Cost
Low

### Execution Cost
Low

### Flakiness Risk
Low

### Owner
Platform Core Team

### Last Validated
2026-06-12

### Coverage Overlap
TEST-014

### Removal Candidate
No

### Notes
Uses local heuristics for fallback parsing.

---

## Test ID
TEST-002

### Name
Objective Priority & Ownership Management (FR-017 to FR-020)

### Category
Unit

### Purpose
Verifies that owner, sponsor, priority, and dependency maps are correctly persisted.

### Risk Covered
Metadata loss or corruption of objective parameters.

### Blast Radius

#### Services
- Objective Management Engine

#### APIs
- POST /api/objective/submit

#### Datastores
- PostgreSQL (uawos_objectives)
- uawos_objective_state.json

#### User Journeys
- Objective Ingestion Journey

#### Downstream Systems
- Planning Engine


### Criticality
Critical

### Failure Impact
High

### Maintenance Cost
Low

### Execution Cost
Low

### Flakiness Risk
Low

### Owner
Platform Core Team

### Last Validated
2026-06-12

### Coverage Overlap
None

### Removal Candidate
No

### Notes
Asserts constraints on mandatory objective metadata.

---

## Test ID
TEST-003

### Name
Objective Conflict Detection Engine (FR-021 to FR-022)

### Category
Unit

### Purpose
Verifies detection of circular dependencies and priority mismatches between objectives.

### Risk Covered
Agent deadlocks or circular execution pipelines.

### Blast Radius

#### Services
- Objective Management Engine

#### APIs
- GET /api/objective/conflicts

#### Datastores
- uawos_objective_state.json

#### User Journeys
- Objective Ingestion Journey

#### Downstream Systems
- Planning Engine


### Criticality
Critical

### Failure Impact
High

### Maintenance Cost
Medium

### Execution Cost
Low

### Flakiness Risk
Low

### Owner
Platform Core Team

### Last Validated
2026-06-12

### Coverage Overlap
None

### Removal Candidate
No

### Notes
Performs Depth-First Search (DFS) cycles checks.

---

## Test ID
TEST-004

### Name
Objective Versioning & History (FR-023 to FR-024)

### Category
Unit

### Purpose
Validates state history tracking and version increment rules on update.

### Risk Covered
Audit log gaps or state regression during updates.

### Blast Radius

#### Services
- Objective Management Engine

#### APIs
- POST /api/objective/action

#### Datastores
- PostgreSQL (uawos_objectives)

#### User Journeys
- Objective Ingestion Journey

#### Downstream Systems
- Observability Engine


### Criticality
Medium

### Failure Impact
Medium

### Maintenance Cost
Low

### Execution Cost
Low

### Flakiness Risk
Low

### Owner
Platform Core Team

### Last Validated
2026-06-12

### Coverage Overlap
None

### Removal Candidate
No

### Notes
Ensures historical state snapshot is saved.

---

## Test ID
TEST-005

### Name
Objective Lifecycle Transitions (FR-025 to FR-028)

### Category
Unit

### Purpose
Verifies transitional actions including archival, restoration, cancellation, and pausing.

### Risk Covered
Illegal state transitions or hanging execution loops.

### Blast Radius

#### Services
- Objective Management Engine

#### APIs
- POST /api/objective/action

#### Datastores
- uawos_objective_state.json

#### User Journeys
- All Dashboard Operations

#### Downstream Systems
- Workflow Engine


### Criticality
High

### Failure Impact
High

### Maintenance Cost
Low

### Execution Cost
Low

### Flakiness Risk
Low

### Owner
Platform Core Team

### Last Validated
2026-06-12

### Coverage Overlap
None

### Removal Candidate
No

### Notes
Maintains deterministic status flags.

---

## Test ID
TEST-006

### Name
Objective Scoring & Health Engine (FR-029 to FR-030)

### Category
Unit

### Purpose
Verifies dynamic health score calculations under Constitutional Law 1.

### Risk Covered
Corrupted health signals or unflagged budget breaches.

### Blast Radius

#### Services
- Objective Management Engine

#### APIs
- GET /api/objective/list

#### Datastores
- uawos_objective_state.json

#### User Journeys
- Objective Ingestion Journey

#### Downstream Systems
- Observability Engine


### Criticality
High

### Failure Impact
High

### Maintenance Cost
Low

### Execution Cost
Low

### Flakiness Risk
Low

### Owner
Platform Core Team

### Last Validated
2026-06-12

### Coverage Overlap
None

### Removal Candidate
No

### Notes
Penalizes health scores for missing outcomes, cycles, or budget warnings.

---

## Test ID
TEST-007

### Name
Measurable Outcomes Validation (FR-031 to FR-040)

### Category
Unit

### Purpose
Validates outcome parameters including metric, unit, weights, dependencies, baselines, and forecasting.

### Risk Covered
Broken ROI calculation or lack of outcome quantification.

### Blast Radius

#### Services
- Outcome Engine

#### APIs
- POST /api/outcome/submit

#### Datastores
- PostgreSQL
- uawos_outcome_state.json

#### User Journeys
- Value Realization Ingestion

#### Downstream Systems
- Value Engine


### Criticality
High

### Failure Impact
High

### Maintenance Cost
Low

### Execution Cost
Low

### Flakiness Risk
Low

### Owner
Platform Core Team

### Last Validated
2026-06-12

### Coverage Overlap
None

### Removal Candidate
No

### Notes
Maintains key outcome metrics and forecasts progress.

---

## Test ID
TEST-008

### Name
Planning & Simulation Engine (FR-041 to FR-060)

### Category
Unit

### Purpose
Verifies generation and ranking of alternative plans.

### Risk Covered
Flawed route choices or incorrect step dependencies.

### Blast Radius

#### Services
- Planning Engine

#### APIs
- POST /api/plan/simulate

#### Datastores
- uawos_planning_state.json

#### User Journeys
- Plan Simulation Journey

#### Downstream Systems
- Workflow Engine


### Criticality
Critical

### Failure Impact
High

### Maintenance Cost
Medium

### Execution Cost
Medium

### Flakiness Risk
Low

### Owner
Platform Core Team

### Last Validated
2026-06-12

### Coverage Overlap
None

### Removal Candidate
No

### Notes
Simulates agent execution time and cost.

---

## Test ID
TEST-009

### Name
Workflow Orchestration Engine (FR-061 to FR-070)

### Category
Unit

### Purpose
Verifies workflow state machine execution and routing.

### Risk Covered
Hanging workflow tasks or state corruption.

### Blast Radius

#### Services
- Workflow Service

#### APIs
- None

#### Datastores
- uawos_workflow_state.json

#### User Journeys
- All Dashboard Operations

#### Downstream Systems
- Action Management Engine


### Criticality
Critical

### Failure Impact
High

### Maintenance Cost
Medium

### Execution Cost
Medium

### Flakiness Risk
Low

### Owner
Platform Core Team

### Last Validated
2026-06-12

### Coverage Overlap
None

### Removal Candidate
No

### Notes
Core coordinator of all agent workflow steps.

---

## Test ID
TEST-010

### Name
Action Execution Engine (FR-071 to FR-080)

### Category
Unit

### Purpose
Verifies individual agent action invocations and tracking.

### Risk Covered
Untracked or runaway agent tool invocations.

### Blast Radius

#### Services
- Action Service

#### APIs
- None

#### Datastores
- uawos_action_state.json

#### User Journeys
- All restricted operations

#### Downstream Systems
- Observability Engine


### Criticality
Critical

### Failure Impact
High

### Maintenance Cost
Medium

### Execution Cost
Medium

### Flakiness Risk
Low

### Owner
Platform Core Team

### Last Validated
2026-06-12

### Coverage Overlap
None

### Removal Candidate
No

### Notes
Triggers LLM tool calls and logs execution history.

---

## Test ID
TEST-011

### Name
Budget cost controls (FR-151 to FR-160)

### Category
Unit

### Purpose
Verifies daily compute/token limit checking and OPA cost blockades.

### Risk Covered
Excessive token spend or budget overruns.

### Blast Radius

#### Services
- Budget Management Service

#### APIs
- POST /api/budget/action

#### Datastores
- PostgreSQL (uawos_budget)
- uawos_budget_state.json

#### User Journeys
- Plan Simulation Journey

#### Downstream Systems
- Governance Service


### Criticality
High

### Failure Impact
High

### Maintenance Cost
Low

### Execution Cost
Low

### Flakiness Risk
Low

### Owner
Platform Core Team

### Last Validated
2026-06-12

### Coverage Overlap
None

### Removal Candidate
No

### Notes
Asserts compliance against allocated token budgets.

---

## Test ID
TEST-012

### Name
Wave 1 Tenant Isolation Integration Tests

### Category
Integration

### Purpose
Verifies thread-safe context propagation, database tenant filters, and vector separation.

### Risk Covered
Cross-tenant database leaks or plaintext file state writes.

### Blast Radius

#### Services
- All database connection utilities

#### APIs
- All APIs

#### Datastores
- PostgreSQL
- Qdrant Vector DB

#### User Journeys
- All Multi-Tenant Journeys

#### Downstream Systems
- All system components


### Criticality
Critical

### Failure Impact
High

### Maintenance Cost
Medium

### Execution Cost
Medium

### Flakiness Risk
Low

### Owner
Infrastructure Team

### Last Validated
2026-06-12

### Coverage Overlap
TEST-013

### Removal Candidate
No

### Notes
Assures file fallback system decommissioning.

---

## Test ID
TEST-013

### Name
Wave 4/5 Neo4j & Multi-Tenant State Isolation Tests

### Category
Integration

### Purpose
Verifies Neo4j REST synchronization and tenant isolation via state utils.

### Risk Covered
Neo4j sync drift or tenant data exposure.

### Blast Radius

#### Services
- Knowledge Management Service
- Neo4j Sync Router

#### APIs
- GET /api/traceability

#### Datastores
- Neo4j
- PostgreSQL

#### User Journeys
- Governance Audit Journey

#### Downstream Systems
- Apache Superset


### Criticality
Critical

### Failure Impact
High

### Maintenance Cost
Medium

### Execution Cost
High

### Flakiness Risk
Medium

### Owner
Infrastructure Team

### Last Validated
2026-06-12

### Coverage Overlap
TEST-012 TEST-015

### Removal Candidate
No

### Notes
Requires Neo4j and PostgreSQL containers.

---

## Test ID
TEST-014

### Name
DTASE Ingestion Verification Tests

### Category
Integration

### Purpose
Validates specialized domain identification (Legal, Healthcare, Product) and multi-persona translation.

### Risk Covered
Broken context parsing or LLM gateway timeouts.

### Blast Radius

#### Services
- DTASE Engine

#### APIs
- POST /api/dtase/analyze

#### Datastores
- None

#### User Journeys
- Objective Ingestion Journey

#### Downstream Systems
- Objective Engine


### Criticality
High

### Failure Impact
Medium

### Maintenance Cost
Medium

### Execution Cost
High

### Flakiness Risk
Medium

### Owner
Platform Core & Knowledge Teams

### Last Validated
2026-06-12

### Coverage Overlap
TEST-001

### Removal Candidate
No

### Notes
Connects to local model gateway.

---

## Test ID
TEST-015

### Name
Neo4j Sync Verification Test

### Category
Integration

### Purpose
Tests individual KnowledgeAsset and relationship Cypher commits to Neo4j.

### Risk Covered
Broken graph database connections or malformed Cypher syntax.

### Blast Radius

#### Services
- Knowledge Management Service

#### APIs
- None

#### Datastores
- Neo4j

#### User Journeys
- Governance Audit Journey

#### Downstream Systems
- None


### Criticality
Medium

### Failure Impact
Medium

### Maintenance Cost
Low

### Execution Cost
High

### Flakiness Risk
Low

### Owner
Infrastructure Team

### Last Validated
2026-06-12

### Coverage Overlap
TEST-013

### Removal Candidate
Yes

### Notes
Can be consolidated into TEST-013.

---

## Test ID
TEST-016

### Name
FastAPI Token Auth Tests

### Category
Security

### Purpose
Verifies token authorization checks block invalid requests and allow authenticated ones.

### Risk Covered
Exposure of REST endpoints without proper API tokens.

### Blast Radius

#### Services
- FastAPI Daemon Server

#### APIs
- /api/requirement/submit
- /api/objective/submit
- /api/budget/action
- /api/objective/action

#### Datastores
- None

#### User Journeys
- All Dashboard Operations

#### Downstream Systems
- UI Client


### Criticality
Critical

### Failure Impact
High

### Maintenance Cost
Low

### Execution Cost
Low

### Flakiness Risk
Low

### Owner
Security Team

### Last Validated
2026-06-12

### Coverage Overlap
None

### Removal Candidate
No

### Notes
Ensures baseline API perimeter security.

---

# CHANGE IMPACT LOG

## Change ID
CHANGE-2026-001

### Description
Established the Test Intelligence Registry and modified proactive governance engine to maintain metadata persistently.

### Affected Tests
- All UAWOS tests (259 total tests cataloged)

### Blast Radius Delta
None (Added registry generator to governance audit run; no production paths modified).

### New Risks Introduced
None.

### Registry Updated By
AI Assistant

### Date
2026-06-12

---

# TEST ECONOMICS DASHBOARD

## High Cost Tests

| Test ID | Cost | Justification |
|----------|--------|-------------|
| TEST-013 | High | Requires live PostgreSQL and Neo4j database containers |
| TEST-014 | High | Runs local LLM inference via LiteLLM / Ollama gateway |

## High Flakiness Tests

| Test ID | Flakiness | Action |
|----------|-----------|--------|
| TEST-013 | Medium | Added container startup retries and connection pingers |

## Redundant Coverage Candidates

| Test ID | Overlaps With | Recommendation |
|----------|---------------|----------------|
| TEST-013 | TEST-012 | Consolidate tenant isolation verification checks |
| TEST-015 | TEST-013 | Deprecate stand-alone Neo4j check in favor of Phase 4/5 suite |

## Removal Recommendations

| Test ID | Reason | Risk After Removal |
|----------|--------|-------------------|
| TEST-015 | Fully covered by Phase 4/5 integration tests (TEST-013) | None |
