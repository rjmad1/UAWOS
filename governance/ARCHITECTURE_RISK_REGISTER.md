# Architectural Risk Register

| Component | Architectural Risk / Violation | Remediation Action |
| :--- | :--- | :--- |
| uawos_state_utils | Circular import dependency cycle detected: uawos_state_utils -> uawos_memory -> uawos_state_utils | Decouple using interfaces, abstract state classes, or callback event listeners. |
| uawos_state_utils | Circular import dependency cycle detected: uawos_state_utils -> uawos_memory -> uawos_knowledge -> uawos_state_utils | Decouple using interfaces, abstract state classes, or callback event listeners. |
| uawos_state_utils | Circular import dependency cycle detected: uawos_state_utils -> uawos_memory -> uawos_weaverouter -> uawos_budget -> uawos_state_utils | Decouple using interfaces, abstract state classes, or callback event listeners. |
| uawos_dashboard_daemon | High coupling: module imports 24 other internal components. | Consolidate utilities and introduce facade or event bus patterns. |
| uawos_pmcms | High coupling: module imports 11 other internal components. | Consolidate utilities and introduce facade or event bus patterns. |

*Last updated: 2026-06-14T20:16:15+0530*
