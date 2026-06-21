# Blast Radius Registry

## Component Impact Metrics

| Service / Module | Blast Radius Score | Criticality | Downstream Dependents | Upstream Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| uawos_action | 15 | Low | *None* | 2 |
| uawos_state_utils | 100 | Critical | uawos_workflow, uawos_autogen_adapter, uawos_event_bus, uawos_sdk, uawos_agent_workforce, uawos_objective, uawos_sandbox_runtime, uawos_value, uawos_memory, uawos_planning, uawos_traceability, uawos_observability, uawos_resource, uawos_semantic_kernel_adapter, uawos_knowledge, uawos_action, uawos_workforce, uawos_learning, uawos_dtase, uawos_langgraph_adapter, uawos_budget, uawos_cli, uawos_governance, uawos_agent_runtime, uawos_audit_ledger, uawos_decision, uawos_integrations, uawos_outcome, uawos_simulation, uawos_pmcms, uawos_weaverouter, uawos_requirement_studio | 0 |
| uawos_db | 71 | High | uawos_workflow, uawos_autogen_adapter, uawos_event_bus, uawos_sdk, uawos_agent_workforce, uawos_objective, uawos_sandbox_runtime, uawos_planning, uawos_traceability, uawos_resource, uawos_semantic_kernel_adapter, uawos_knowledge, uawos_action, uawos_langgraph_adapter, uawos_cli, uawos_proactive_governance, uawos_agent_runtime, uawos_audit_ledger, uawos_integrations, uawos_outcome, uawos_simulation, uawos_pmcms | 0 |
| uawos_agent_runtime | 21 | Low | uawos_audit_ledger, uawos_autogen_adapter, uawos_langgraph_adapter, uawos_event_bus, uawos_sandbox_runtime, uawos_semantic_kernel_adapter | 3 |
| uawos_governance | 25 | Low | uawos_audit_ledger, uawos_autogen_adapter, uawos_langgraph_adapter, uawos_event_bus, uawos_pmcms, uawos_sandbox_runtime, uawos_semantic_kernel_adapter, uawos_agent_runtime | 1 |
| uawos_agent_workforce | 30 | Medium | uawos_cli, uawos_pmcms, uawos_traceability, uawos_integrations | 2 |
| uawos_audit_ledger | 25 | Low | uawos_semantic_kernel_adapter, uawos_autogen_adapter | 3 |
| uawos_budget | 25 | Low | uawos_weaverouter, uawos_traceability, uawos_dtase | 1 |
| uawos_cli | 15 | Low | *None* | 2 |
| uawos_integrations | 25 | Low | uawos_cli, uawos_traceability | 3 |
| uawos_context | 20 | Low | uawos_sdk | 0 |
| uawos_dashboard_daemon | 15 | Low | *None* | 0 |
| uawos_decision | 20 | Low | uawos_pmcms | 1 |
| uawos_dtase | 20 | Low | uawos_traceability | 1 |
| uawos_weaverouter | 20 | Low | uawos_traceability, uawos_dtase | 2 |
| uawos_event_bus | 15 | Low | *None* | 3 |
| uawos_knowledge | 15 | Low | *None* | 2 |
| uawos_learning | 15 | Low | *None* | 1 |
| uawos_memory | 20 | Low | uawos_sdk | 1 |
| uawos_objective | 25 | Low | uawos_pmcms, uawos_sdk | 3 |
| uawos_outcome | 20 | Low | uawos_sdk, uawos_pmcms, uawos_objective | 2 |
| uawos_observability | 20 | Low | uawos_weaverouter, uawos_traceability, uawos_dtase | 1 |
| uawos_planning | 20 | Low | uawos_pmcms | 2 |
| uawos_pmcms | 15 | Low | *None* | 11 |
| uawos_workflow | 20 | Low | uawos_pmcms | 2 |
| uawos_simulation | 20 | Low | uawos_pmcms | 2 |
| uawos_resource | 20 | Low | uawos_pmcms | 2 |
| uawos_value | 20 | Low | uawos_pmcms | 1 |
| uawos_proactive_governance | 15 | Low | *None* | 1 |
| uawos_requirement_studio | 15 | Low | *None* | 1 |
| uawos_sandbox_runtime | 25 | Low | uawos_semantic_kernel_adapter, uawos_autogen_adapter | 3 |
| uawos_sdk | 15 | Low | *None* | 4 |
| uawos_traceability | 15 | Low | *None* | 4 |
| uawos_workforce | 15 | Low | *None* | 1 |
| uawos_autogen_adapter | 15 | Low | *None* | 5 |
| uawos_langgraph_adapter | 15 | Low | *None* | 3 |
| uawos_semantic_kernel_adapter | 15 | Low | *None* | 5 |

*Last updated: 2026-06-21T19:38:57+0530*
