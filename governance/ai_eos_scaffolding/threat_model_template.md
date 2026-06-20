# Threat Model Template: [Component/Service Name]
# Location: /security/threat_models/

## 1. Metadata
*   **Target Component**: [e.g., User Authentication Service]
*   **Security Owner**: [Agent/User Email]
*   **Review Date**: [YYYY-MM-DD]
*   **Current Risk Rating**: [Low / Medium / High / Critical]

## 2. Component Architecture Overview
*Describe the entry points, trust boundaries, database integrations, and cloud hosting configurations for this component.*

## 3. Data Flow Diagram Reference
*Link to visual diagram in /architecture showing how data traverses trust boundaries.*

## 4. Threat Matrix (STRIDE Model)

| ID | Threat Category | Threat Description | Severity | Mitigation Strategy | Validation Verification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| T01 | **Spoofing** | Adversary attempts to mimic a legitimate backend agent payload. | High | Cryptographically sign all agent-to-agent messages in orchestration layer. | Validate verification checks in routing test suite. |
| T02 | **Tampering** | Code modifications submitted directly to main bypassing gates. | Critical | Enforce branch protection rules blocking direct pushes to develop/main. | Check branch policies configuration in Github settings. |
| T03 | **Repudiation** | An agent denies taking an action that caused resource deletion. | Medium | Enforce immutable, hashed audit trails on all agent-executed commands. | Audit logs verification script check. |
| T04 | **Information Disclosure** | Leakage of API tokens or customer PII into standard stdout logs. | Critical | Deploy automatic regex scrubbers to sanitize log fields before ingestion. | Verify trufflehog scanner outputs in CI/CD pipeline. |
| T05 | **Denial of Service** | Agent loop triggers recursive API requests depleting server resources. | High | Set strict token budgets and tool rate limit rules (e.g., max 10 calls/min). | Verify tool sandbox rate limits config. |
| T06 | **Elevation of Privilege** | Frontend agent reads database schemas by tricking agent permissions. | High | Scope IAM roles and folder execution limits according to Least Privilege. | Validate config checks in Agent Registry. |

## 5. AI-Specific Vulnerability Assessments
*   **Prompt Injection Risks**: [Describe delimiters, validation steps]
*   **Knowledge Poisoning Controls**: [Detail validation rules on OKF files]
*   **Data Lineage Scoping**: [State data classification limits for LLM cache]
