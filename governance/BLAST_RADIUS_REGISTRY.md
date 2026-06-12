# Blast Radius Registry

## Component Impact Metrics

| Service / Module | Blast Radius Score | Criticality | Downstream Dependents | Upstream Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| uawos_action | 20 | Low | uawos_dashboard_daemon | 3 |
| uawos_workflow | 30 | Medium | uawos_dashboard_daemon, uawos_action, uawos_pmcms | 3 |
| uawos_state_utils | 100 | Critical | uawos_learning, uawos_traceability, uawos_outcome, uawos_agent_workforce, uawos_audit_ledger, uawos_decision, uawos_governance, uawos_memory, uawos_resource, uawos_autogen_adapter, uawos_knowledge, uawos_sdk, uawos_semantic_kernel_adapter, uawos_objective, uawos_budget, uawos_pmcms, uawos_observability, uawos_integrations, uawos_sandbox_runtime, uawos_planning, uawos_cli, uawos_simulation, uawos_workforce, uawos_agent_runtime, uawos_workflow, uawos_value, uawos_requirement_studio, uawos_dashboard_daemon, uawos_event_bus, uawos_langgraph_adapter, uawos_action | 2 |
| uawos_db | 81 | Critical | uawos_learning, uawos_traceability, uawos_outcome, uawos_agent_workforce, uawos_audit_ledger, uawos_governance, uawos_decision, uawos_memory, uawos_resource, uawos_proactive_governance, uawos_autogen_adapter, uawos_knowledge, uawos_sdk, uawos_semantic_kernel_adapter, uawos_objective, uawos_budget, uawos_pmcms, uawos_observability, uawos_state_utils, uawos_integrations, uawos_sandbox_runtime, uawos_planning, uawos_cli, uawos_simulation, uawos_workforce, uawos_agent_runtime, uawos_workflow, uawos_value, uawos_requirement_studio, uawos_dashboard_daemon, uawos_event_bus, uawos_langgraph_adapter, uawos_action | 1 |
| uawos_agent_runtime | 22 | Low | uawos_autogen_adapter, uawos_semantic_kernel_adapter, uawos_audit_ledger, uawos_sandbox_runtime, uawos_event_bus, uawos_langgraph_adapter | 3 |
| uawos_governance | 30 | Medium | uawos_autogen_adapter, uawos_agent_runtime, uawos_semantic_kernel_adapter, uawos_audit_ledger, uawos_dashboard_daemon, uawos_event_bus, uawos_sandbox_runtime, uawos_langgraph_adapter, uawos_pmcms | 2 |
| uawos_agent_workforce | 18 | Low | uawos_autogen_adapter, uawos_agent_runtime, uawos_workflow, uawos_semantic_kernel_adapter, uawos_audit_ledger, uawos_governance, uawos_dashboard_daemon, uawos_planning, uawos_event_bus, uawos_sandbox_runtime, uawos_cli, uawos_langgraph_adapter, uawos_action, uawos_pmcms | 2 |
| uawos_audit_ledger | 25 | Low | uawos_semantic_kernel_adapter, uawos_autogen_adapter | 3 |
| uawos_autogen_adapter | 15 | Low | *None* | 5 |
| uawos_sandbox_runtime | 25 | Low | uawos_semantic_kernel_adapter, uawos_autogen_adapter | 3 |
| uawos_budget | 30 | Medium | uawos_traceability, uawos_sdk, uawos_dashboard_daemon, uawos_objective, uawos_pmcms | 1 |
| uawos_cli | 15 | Low | *None* | 2 |
| uawos_integrations | 30 | Medium | uawos_cli, uawos_dashboard_daemon, uawos_traceability | 2 |
| uawos_context | 35 | Medium | uawos_learning, uawos_traceability, uawos_outcome, uawos_agent_workforce, uawos_audit_ledger, uawos_decision, uawos_governance, uawos_memory, uawos_resource, uawos_proactive_governance, uawos_autogen_adapter, uawos_knowledge, uawos_sdk, uawos_semantic_kernel_adapter, uawos_objective, uawos_budget, uawos_pmcms, uawos_observability, uawos_state_utils, uawos_integrations, uawos_sandbox_runtime, uawos_planning, uawos_db, uawos_cli, uawos_simulation, uawos_workforce, uawos_agent_runtime, uawos_workflow, uawos_value, uawos_requirement_studio, uawos_dashboard_daemon, uawos_event_bus, uawos_langgraph_adapter, uawos_action | 0 |
| uawos_dashboard_daemon | 15 | Low | *None* | 24 |
| uawos_learning | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_traceability | 20 | Low | uawos_dashboard_daemon | 3 |
| uawos_outcome | 25 | Low | uawos_objective, uawos_dashboard_daemon, uawos_sdk, uawos_pmcms | 2 |
| uawos_decision | 25 | Low | uawos_dashboard_daemon, uawos_pmcms | 1 |
| uawos_memory | 25 | Low | uawos_dashboard_daemon, uawos_sdk | 3 |
| uawos_resource | 25 | Low | uawos_dashboard_daemon, uawos_pmcms | 2 |
| uawos_proactive_governance | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_knowledge | 25 | Low | uawos_dashboard_daemon, uawos_memory, uawos_sdk | 2 |
| uawos_dtase | 30 | Medium | uawos_traceability, uawos_sdk, uawos_dashboard_daemon, uawos_objective, uawos_pmcms | 0 |
| uawos_objective | 30 | Medium | uawos_dashboard_daemon, uawos_sdk, uawos_pmcms | 5 |
| uawos_pmcms | 20 | Low | uawos_dashboard_daemon | 11 |
| uawos_observability | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_planning | 30 | Medium | uawos_workflow, uawos_dashboard_daemon, uawos_action, uawos_pmcms | 3 |
| uawos_simulation | 25 | Low | uawos_dashboard_daemon, uawos_pmcms | 2 |
| uawos_workforce | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_value | 25 | Low | uawos_dashboard_daemon, uawos_pmcms | 1 |
| uawos_requirement_studio | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_event_bus | 15 | Low | *None* | 3 |
| uawos_langgraph_adapter | 15 | Low | *None* | 3 |
| uawos_sdk | 15 | Low | *None* | 4 |
| uawos_semantic_kernel_adapter | 15 | Low | *None* | 5 |

*Last updated: 2026-06-12T14:34:09+0530*
