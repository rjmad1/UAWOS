# Architectural Risk Register

| Component | Architectural Risk / Violation | Remediation Action |
| :--- | :--- | :--- |
| uawos_dashboard_daemon | High coupling: module imports 24 other internal components. | Consolidate utilities and introduce facade or event bus patterns. |
| uawos_pmcms | High coupling: module imports 11 other internal components. | Consolidate utilities and introduce facade or event bus patterns. |

*Last updated: 2026-06-13T11:42:55+0530*
