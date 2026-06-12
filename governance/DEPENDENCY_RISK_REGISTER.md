# Dependency Risk Register

## Third-Party Package Audits

| Package Name | License Type | Compliance Verdict | Security Vulnerabilities | Operational Risks |
| :--- | :--- | :--- | :--- | :--- |
| pydantic-ai | Apache-2.0 | Approved | None | Beta library API change risk |
| dspy-ai | MIT | Approved | IndentationError resolved | Syntax break risk on PEP-649 (Python 3.14+) |
| psycopg2-binary | BSD | Approved | None | Uses port 5435 instead of default postgres |
| marker-wrapper | GPLv3 | Isolated | None | Isolated to port 8000 REST service; compliant |

*Last updated: 2026-06-12T14:34:09+0530*
