# Blast Radius Registry

## Component Impact Metrics

| Service / Module | Blast Radius Score | Criticality | Downstream Dependents | Upstream Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| uawos_action | 20 | Low | uawos_dashboard_daemon | 3 |
| uawos_db | 78 | Critical | uawos_autogen_adapter, uawos_integrations, uawos_value, uawos_knowledge, uawos_governance, uawos_agent_runtime, uawos_weaverouter, uawos_workflow, uawos_workforce, uawos_outcome, uawos_planning, uawos_sdk, uawos_cli, uawos_learning, uawos_dashboard_daemon, uawos_budget, uawos_audit_ledger, uawos_state_utils, uawos_dtase, uawos_resource, uawos_memory, uawos_proactive_governance, uawos_agent_workforce, uawos_requirement_studio, uawos_semantic_kernel_adapter, uawos_sandbox_runtime, uawos_pmcms, uawos_simulation, uawos_action, uawos_event_bus, uawos_traceability, uawos_observability, uawos_objective, uawos_langgraph_adapter, uawos_decision | 1 |
| uawos_workflow | 30 | Medium | uawos_action, uawos_pmcms, uawos_dashboard_daemon | 3 |
| uawos_state_utils | 100 | Critical | uawos_autogen_adapter, uawos_integrations, uawos_value, uawos_knowledge, uawos_governance, uawos_agent_runtime, uawos_weaverouter, uawos_workflow, uawos_workforce, uawos_outcome, uawos_planning, uawos_cli, uawos_sdk, uawos_learning, uawos_budget, uawos_dashboard_daemon, uawos_audit_ledger, uawos_dtase, uawos_resource, uawos_memory, uawos_agent_workforce, uawos_requirement_studio, uawos_semantic_kernel_adapter, uawos_sandbox_runtime, uawos_pmcms, uawos_simulation, uawos_action, uawos_event_bus, uawos_traceability, uawos_observability, uawos_objective, uawos_langgraph_adapter, uawos_decision | 2 |
| uawos_agent_runtime | 21 | Low | uawos_autogen_adapter, uawos_semantic_kernel_adapter, uawos_audit_ledger, uawos_sandbox_runtime, uawos_event_bus, uawos_langgraph_adapter | 3 |
| uawos_governance | 30 | Medium | uawos_autogen_adapter, uawos_semantic_kernel_adapter, uawos_dashboard_daemon, uawos_agent_runtime, uawos_audit_ledger, uawos_sandbox_runtime, uawos_event_bus, uawos_pmcms, uawos_langgraph_adapter | 2 |
| uawos_agent_workforce | 17 | Low | uawos_autogen_adapter, uawos_action, uawos_planning, uawos_semantic_kernel_adapter, uawos_cli, uawos_governance, uawos_dashboard_daemon, uawos_agent_runtime, uawos_audit_ledger, uawos_workflow, uawos_event_bus, uawos_sandbox_runtime, uawos_pmcms, uawos_langgraph_adapter | 2 |
| uawos_audit_ledger | 25 | Low | uawos_autogen_adapter, uawos_semantic_kernel_adapter | 3 |
| uawos_autogen_adapter | 15 | Low | *None* | 5 |
| uawos_sandbox_runtime | 25 | Low | uawos_autogen_adapter, uawos_semantic_kernel_adapter | 3 |
| uawos_budget | 35 | Medium | uawos_sdk, uawos_dashboard_daemon, uawos_weaverouter, uawos_dtase, uawos_traceability, uawos_pmcms, uawos_objective, uawos_memory | 1 |
| uawos_cli | 15 | Low | *None* | 2 |
| uawos_integrations | 30 | Medium | uawos_traceability, uawos_cli, uawos_dashboard_daemon | 2 |
| uawos_context | 35 | Medium | uawos_autogen_adapter, uawos_integrations, uawos_value, uawos_knowledge, uawos_governance, uawos_agent_runtime, uawos_weaverouter, uawos_workflow, uawos_db, uawos_workforce, uawos_outcome, uawos_planning, uawos_sdk, uawos_cli, uawos_learning, uawos_dashboard_daemon, uawos_budget, uawos_audit_ledger, uawos_state_utils, uawos_dtase, uawos_resource, uawos_memory, uawos_proactive_governance, uawos_agent_workforce, uawos_requirement_studio, uawos_semantic_kernel_adapter, uawos_sandbox_runtime, uawos_pmcms, uawos_simulation, uawos_action, uawos_event_bus, uawos_traceability, uawos_observability, uawos_objective, uawos_langgraph_adapter, uawos_decision | 0 |
| uawos_dashboard_daemon | 15 | Low | *None* | 24 |
| uawos_value | 25 | Low | uawos_pmcms, uawos_dashboard_daemon | 1 |
| uawos_knowledge | 25 | Low | uawos_sdk, uawos_memory, uawos_dashboard_daemon | 2 |
| uawos_workforce | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_outcome | 25 | Low | uawos_pmcms, uawos_objective, uawos_sdk, uawos_dashboard_daemon | 2 |
| uawos_planning | 30 | Medium | uawos_action, uawos_pmcms, uawos_workflow, uawos_dashboard_daemon | 3 |
| uawos_learning | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_dtase | 30 | Medium | uawos_sdk, uawos_dashboard_daemon, uawos_traceability, uawos_pmcms, uawos_objective | 1 |
| uawos_resource | 25 | Low | uawos_pmcms, uawos_dashboard_daemon | 2 |
| uawos_memory | 25 | Low | uawos_sdk, uawos_dashboard_daemon | 4 |
| uawos_proactive_governance | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_requirement_studio | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_pmcms | 20 | Low | uawos_dashboard_daemon | 11 |
| uawos_simulation | 25 | Low | uawos_pmcms, uawos_dashboard_daemon | 2 |
| uawos_traceability | 20 | Low | uawos_dashboard_daemon | 4 |
| uawos_observability | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_objective | 30 | Medium | uawos_pmcms, uawos_sdk, uawos_dashboard_daemon | 5 |
| uawos_decision | 25 | Low | uawos_pmcms, uawos_dashboard_daemon | 1 |
| uawos_weaverouter | 25 | Low | uawos_sdk, uawos_dashboard_daemon, uawos_dtase, uawos_traceability, uawos_pmcms, uawos_objective, uawos_memory | 1 |
| uawos_event_bus | 15 | Low | *None* | 3 |
| uawos_langgraph_adapter | 15 | Low | *None* | 3 |
| uawos_sdk | 15 | Low | *None* | 4 |
| uawos_semantic_kernel_adapter | 15 | Low | *None* | 5 |

*Last updated: 2026-06-13T06:30:04+0530*
