# Blast Radius Registry

## Component Impact Metrics

| Service / Module | Blast Radius Score | Criticality | Downstream Dependents | Upstream Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| uawos_action | 20 | Low | uawos_dashboard_daemon | 3 |
| uawos_db | 78 | Critical | uawos_workflow, uawos_requirement_studio, uawos_cli, uawos_dtase, uawos_decision, uawos_event_bus, uawos_semantic_kernel_adapter, uawos_langgraph_adapter, uawos_pmcms, uawos_learning, uawos_governance, uawos_planning, uawos_autogen_adapter, uawos_observability, uawos_sandbox_runtime, uawos_dashboard_daemon, uawos_agent_workforce, uawos_memory, uawos_weaverouter, uawos_traceability, uawos_sdk, uawos_action, uawos_audit_ledger, uawos_resource, uawos_proactive_governance, uawos_agent_runtime, uawos_objective, uawos_state_utils, uawos_budget, uawos_workforce, uawos_outcome, uawos_value, uawos_simulation, uawos_integrations, uawos_knowledge | 1 |
| uawos_workflow | 30 | Medium | uawos_dashboard_daemon, uawos_pmcms, uawos_action | 3 |
| uawos_state_utils | 100 | Critical | uawos_workflow, uawos_requirement_studio, uawos_cli, uawos_dtase, uawos_decision, uawos_event_bus, uawos_semantic_kernel_adapter, uawos_langgraph_adapter, uawos_pmcms, uawos_learning, uawos_governance, uawos_planning, uawos_autogen_adapter, uawos_observability, uawos_sandbox_runtime, uawos_dashboard_daemon, uawos_agent_workforce, uawos_memory, uawos_weaverouter, uawos_traceability, uawos_sdk, uawos_action, uawos_audit_ledger, uawos_resource, uawos_agent_runtime, uawos_objective, uawos_budget, uawos_workforce, uawos_outcome, uawos_value, uawos_simulation, uawos_integrations, uawos_knowledge | 3 |
| uawos_agent_runtime | 21 | Low | uawos_event_bus, uawos_semantic_kernel_adapter, uawos_langgraph_adapter, uawos_autogen_adapter, uawos_audit_ledger, uawos_sandbox_runtime | 3 |
| uawos_governance | 30 | Medium | uawos_event_bus, uawos_semantic_kernel_adapter, uawos_agent_runtime, uawos_langgraph_adapter, uawos_pmcms, uawos_sandbox_runtime, uawos_autogen_adapter, uawos_audit_ledger, uawos_dashboard_daemon | 2 |
| uawos_agent_workforce | 17 | Low | uawos_event_bus, uawos_semantic_kernel_adapter, uawos_agent_runtime, uawos_workflow, uawos_pmcms, uawos_langgraph_adapter, uawos_cli, uawos_governance, uawos_sandbox_runtime, uawos_planning, uawos_action, uawos_autogen_adapter, uawos_audit_ledger, uawos_dashboard_daemon | 2 |
| uawos_audit_ledger | 25 | Low | uawos_semantic_kernel_adapter, uawos_autogen_adapter | 3 |
| uawos_autogen_adapter | 15 | Low | *None* | 5 |
| uawos_sandbox_runtime | 25 | Low | uawos_semantic_kernel_adapter, uawos_autogen_adapter | 3 |
| uawos_budget | 35 | Medium | uawos_workflow, uawos_requirement_studio, uawos_dtase, uawos_cli, uawos_decision, uawos_event_bus, uawos_semantic_kernel_adapter, uawos_langgraph_adapter, uawos_pmcms, uawos_learning, uawos_governance, uawos_planning, uawos_autogen_adapter, uawos_observability, uawos_dashboard_daemon, uawos_sandbox_runtime, uawos_agent_workforce, uawos_memory, uawos_weaverouter, uawos_traceability, uawos_sdk, uawos_action, uawos_audit_ledger, uawos_resource, uawos_agent_runtime, uawos_objective, uawos_state_utils, uawos_workforce, uawos_outcome, uawos_value, uawos_simulation, uawos_integrations, uawos_knowledge | 1 |
| uawos_cli | 15 | Low | *None* | 2 |
| uawos_integrations | 30 | Medium | uawos_dashboard_daemon, uawos_cli, uawos_traceability | 2 |
| uawos_context | 35 | Medium | uawos_workflow, uawos_requirement_studio, uawos_cli, uawos_dtase, uawos_decision, uawos_event_bus, uawos_semantic_kernel_adapter, uawos_langgraph_adapter, uawos_pmcms, uawos_learning, uawos_governance, uawos_db, uawos_planning, uawos_autogen_adapter, uawos_observability, uawos_dashboard_daemon, uawos_sandbox_runtime, uawos_agent_workforce, uawos_memory, uawos_weaverouter, uawos_traceability, uawos_sdk, uawos_action, uawos_audit_ledger, uawos_proactive_governance, uawos_resource, uawos_agent_runtime, uawos_objective, uawos_state_utils, uawos_budget, uawos_workforce, uawos_outcome, uawos_value, uawos_simulation, uawos_integrations, uawos_knowledge | 0 |
| uawos_dashboard_daemon | 15 | Low | *None* | 24 |
| uawos_requirement_studio | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_dtase | 30 | Medium | uawos_pmcms, uawos_objective, uawos_traceability, uawos_sdk, uawos_dashboard_daemon | 1 |
| uawos_decision | 25 | Low | uawos_dashboard_daemon, uawos_pmcms | 1 |
| uawos_pmcms | 20 | Low | uawos_dashboard_daemon | 11 |
| uawos_learning | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_planning | 30 | Medium | uawos_action, uawos_dashboard_daemon, uawos_workflow, uawos_pmcms | 3 |
| uawos_observability | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_memory | 30 | Medium | uawos_workflow, uawos_requirement_studio, uawos_cli, uawos_dtase, uawos_decision, uawos_event_bus, uawos_semantic_kernel_adapter, uawos_langgraph_adapter, uawos_pmcms, uawos_learning, uawos_governance, uawos_planning, uawos_autogen_adapter, uawos_observability, uawos_dashboard_daemon, uawos_sandbox_runtime, uawos_agent_workforce, uawos_weaverouter, uawos_traceability, uawos_sdk, uawos_action, uawos_audit_ledger, uawos_resource, uawos_agent_runtime, uawos_objective, uawos_state_utils, uawos_budget, uawos_workforce, uawos_outcome, uawos_value, uawos_simulation, uawos_integrations, uawos_knowledge | 4 |
| uawos_traceability | 20 | Low | uawos_dashboard_daemon | 4 |
| uawos_resource | 25 | Low | uawos_dashboard_daemon, uawos_pmcms | 2 |
| uawos_proactive_governance | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_objective | 30 | Medium | uawos_dashboard_daemon, uawos_sdk, uawos_pmcms | 5 |
| uawos_workforce | 20 | Low | uawos_dashboard_daemon | 1 |
| uawos_outcome | 25 | Low | uawos_dashboard_daemon, uawos_pmcms, uawos_sdk, uawos_objective | 2 |
| uawos_value | 25 | Low | uawos_dashboard_daemon, uawos_pmcms | 1 |
| uawos_simulation | 25 | Low | uawos_dashboard_daemon, uawos_pmcms | 2 |
| uawos_knowledge | 25 | Low | uawos_workflow, uawos_requirement_studio, uawos_cli, uawos_dtase, uawos_decision, uawos_event_bus, uawos_semantic_kernel_adapter, uawos_langgraph_adapter, uawos_pmcms, uawos_learning, uawos_governance, uawos_planning, uawos_autogen_adapter, uawos_observability, uawos_dashboard_daemon, uawos_sandbox_runtime, uawos_agent_workforce, uawos_memory, uawos_weaverouter, uawos_traceability, uawos_sdk, uawos_action, uawos_audit_ledger, uawos_resource, uawos_agent_runtime, uawos_objective, uawos_state_utils, uawos_budget, uawos_workforce, uawos_outcome, uawos_value, uawos_simulation, uawos_integrations | 2 |
| uawos_weaverouter | 25 | Low | uawos_workflow, uawos_requirement_studio, uawos_dtase, uawos_cli, uawos_decision, uawos_event_bus, uawos_semantic_kernel_adapter, uawos_langgraph_adapter, uawos_pmcms, uawos_learning, uawos_governance, uawos_planning, uawos_autogen_adapter, uawos_observability, uawos_dashboard_daemon, uawos_sandbox_runtime, uawos_agent_workforce, uawos_memory, uawos_traceability, uawos_sdk, uawos_action, uawos_audit_ledger, uawos_resource, uawos_agent_runtime, uawos_objective, uawos_state_utils, uawos_budget, uawos_workforce, uawos_outcome, uawos_value, uawos_simulation, uawos_integrations, uawos_knowledge | 1 |
| uawos_event_bus | 15 | Low | *None* | 3 |
| uawos_langgraph_adapter | 15 | Low | *None* | 3 |
| uawos_sdk | 15 | Low | *None* | 4 |
| uawos_semantic_kernel_adapter | 15 | Low | *None* | 5 |

*Last updated: 2026-06-14T20:16:15+0530*
