# Blast Radius Registry

## Component Impact Metrics

| Service / Module | Blast Radius Score | Criticality | Downstream Dependents | Upstream Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| uawos_action | 20 | Low | uawos_dashboard_daemon | 3 |
| uawos_workflow | 30 | Medium | uawos_action, uawos_pmcms, uawos_dashboard_daemon | 3 |
| uawos_state_utils | 100 | Critical | uawos_langgraph_adapter, uawos_agent_runtime, uawos_requirement_studio, uawos_weaverouter, uawos_simulation, uawos_pmcms, uawos_event_bus, uawos_integrations, uawos_governance, uawos_action, uawos_audit_ledger, uawos_value, uawos_observability, uawos_sdk, uawos_planning, uawos_sandbox_runtime, uawos_outcome, uawos_decision, uawos_traceability, uawos_autogen_adapter, uawos_workforce, uawos_workflow, uawos_semantic_kernel_adapter, uawos_dashboard_daemon, uawos_knowledge, uawos_budget, uawos_memory, uawos_agent_workforce, uawos_learning, uawos_objective, uawos_resource, uawos_dtase, uawos_cli | 2 |
| uawos_db | 78 | Critical | uawos_langgraph_adapter, uawos_agent_runtime, uawos_requirement_studio, uawos_weaverouter, uawos_state_utils, uawos_simulation, uawos_pmcms, uawos_event_bus, uawos_integrations, uawos_governance, uawos_action, uawos_audit_ledger, uawos_value, uawos_observability, uawos_sdk, uawos_planning, uawos_sandbox_runtime, uawos_outcome, uawos_decision, uawos_traceability, uawos_autogen_adapter, uawos_workforce, uawos_workflow, uawos_semantic_kernel_adapter, uawos_dashboard_daemon, uawos_proactive_governance, uawos_knowledge, uawos_budget, uawos_memory, uawos_agent_workforce, uawos_learning, uawos_objective, uawos_resource, uawos_dtase, uawos_cli | 1 |
| uawos_agent_runtime | 21 | Low | uawos_langgraph_adapter, uawos_audit_ledger, uawos_semantic_kernel_adapter, uawos_sandbox_runtime, uawos_autogen_adapter, uawos_event_bus | 3 |
| uawos_governance | 30 | Medium | uawos_langgraph_adapter, uawos_agent_runtime, uawos_audit_ledger, uawos_semantic_kernel_adapter, uawos_dashboard_daemon, uawos_sandbox_runtime, uawos_pmcms, uawos_autogen_adapter, uawos_event_bus | 2 |
| uawos_agent_workforce | 17 | Low | uawos_langgraph_adapter, uawos_workflow, uawos_governance, uawos_agent_runtime, uawos_action, uawos_audit_ledger, uawos_semantic_kernel_adapter, uawos_dashboard_daemon, uawos_planning, uawos_sandbox_runtime, uawos_pmcms, uawos_cli, uawos_autogen_adapter, uawos_event_bus | 2 |
| uawos_audit_ledger | 25 | Low | uawos_autogen_adapter, uawos_semantic_kernel_adapter | 3 |
| uawos_autogen_adapter | 15 | Low | *None* | 5 |
| uawos_sandbox_runtime | 25 | Low | uawos_autogen_adapter, uawos_semantic_kernel_adapter | 3 |
| uawos_budget | 35 | Medium | uawos_objective, uawos_weaverouter, uawos_dashboard_daemon, uawos_sdk, uawos_dtase, uawos_pmcms, uawos_traceability, uawos_memory | 1 |
| uawos_cli | 15 | Low | *None* | 2 |
| uawos_integrations | 30 | Medium | uawos_traceability, uawos_cli, uawos_dashboard_daemon | 2 |
| uawos_context | 35 | Medium | uawos_langgraph_adapter, uawos_agent_runtime, uawos_requirement_studio, uawos_weaverouter, uawos_state_utils, uawos_simulation, uawos_pmcms, uawos_event_bus, uawos_integrations, uawos_governance, uawos_action, uawos_audit_ledger, uawos_value, uawos_observability, uawos_sdk, uawos_planning, uawos_db, uawos_sandbox_runtime, uawos_outcome, uawos_decision, uawos_traceability, uawos_autogen_adapter, uawos_workforce, uawos_workflow, uawos_semantic_kernel_adapter, uawos_dashboard_daemon, uawos_proactive_governance, uawos_knowledge, uawos_budget, uawos_memory, uawos_agent_workforce, uawos_learning, uawos_objective, uawos_resource, uawos_dtase, uawos_cli | 0 |
| uawos_dashboard_daemon | 15 | Low | *None* | 24 |
| uawos_requirement_studio | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_simulation | 25 | Low | uawos_pmcms, uawos_dashboard_daemon | 2 |
| uawos_pmcms | 20 | Low | uawos_dashboard_daemon | 11 |
| uawos_value | 25 | Low | uawos_pmcms, uawos_dashboard_daemon | 1 |
| uawos_observability | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_planning | 30 | Medium | uawos_pmcms, uawos_workflow, uawos_action, uawos_dashboard_daemon | 3 |
| uawos_decision | 25 | Low | uawos_pmcms, uawos_dashboard_daemon | 1 |
| uawos_outcome | 25 | Low | uawos_pmcms, uawos_objective, uawos_sdk, uawos_dashboard_daemon | 2 |
| uawos_traceability | 20 | Low | uawos_dashboard_daemon | 4 |
| uawos_workforce | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_proactive_governance | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_knowledge | 25 | Low | uawos_memory, uawos_sdk, uawos_dashboard_daemon | 2 |
| uawos_memory | 25 | Low | uawos_sdk, uawos_dashboard_daemon | 4 |
| uawos_learning | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_objective | 30 | Medium | uawos_pmcms, uawos_sdk, uawos_dashboard_daemon | 5 |
| uawos_resource | 25 | Low | uawos_pmcms, uawos_dashboard_daemon | 2 |
| uawos_dtase | 30 | Medium | uawos_objective, uawos_dashboard_daemon, uawos_sdk, uawos_pmcms, uawos_traceability | 1 |
| uawos_weaverouter | 25 | Low | uawos_objective, uawos_dashboard_daemon, uawos_sdk, uawos_dtase, uawos_pmcms, uawos_traceability, uawos_memory | 1 |
| uawos_event_bus | 15 | Low | *None* | 3 |
| uawos_langgraph_adapter | 15 | Low | *None* | 3 |
| uawos_sdk | 15 | Low | *None* | 4 |
| uawos_semantic_kernel_adapter | 15 | Low | *None* | 5 |

*Last updated: 2026-06-13T11:42:55+0530*
