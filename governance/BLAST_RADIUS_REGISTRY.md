# Blast Radius Registry

## Component Impact Metrics

| Service / Module | Blast Radius Score | Criticality | Downstream Dependents | Upstream Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| uawos_action | 15 | Low | *None* | 2 |
| uawos_db | 75 | High | uawos_action, uawos_agent_runtime, uawos_agent_workforce, uawos_event_bus, uawos_semantic_kernel_adapter, uawos_sandbox_runtime, uawos_integrations, uawos_memory, uawos_resource, uawos_pmcms, uawos_traceability, uawos_proactive_governance, uawos_workflow, uawos_audit_ledger, uawos_outcome, uawos_sdk, uawos_planning, uawos_cli, uawos_knowledge, uawos_simulation, uawos_autogen_adapter, uawos_objective, uawos_langgraph_adapter | 0 |
| uawos_state_utils | 100 | Critical | uawos_action, uawos_agent_runtime, uawos_agent_workforce, uawos_budget, uawos_event_bus, uawos_workforce, uawos_semantic_kernel_adapter, uawos_sandbox_runtime, uawos_weaverouter, uawos_integrations, uawos_requirement_studio, uawos_decision, uawos_memory, uawos_observability, uawos_resource, uawos_pmcms, uawos_governance, uawos_traceability, uawos_workflow, uawos_dtase, uawos_audit_ledger, uawos_outcome, uawos_sdk, uawos_planning, uawos_cli, uawos_knowledge, uawos_simulation, uawos_autogen_adapter, uawos_value, uawos_learning, uawos_objective, uawos_langgraph_adapter | 0 |
| uawos_agent_runtime | 21 | Low | uawos_semantic_kernel_adapter, uawos_sandbox_runtime, uawos_autogen_adapter, uawos_langgraph_adapter, uawos_audit_ledger, uawos_event_bus | 3 |
| uawos_governance | 25 | Low | uawos_semantic_kernel_adapter, uawos_sandbox_runtime, uawos_pmcms, uawos_agent_runtime, uawos_autogen_adapter, uawos_langgraph_adapter, uawos_audit_ledger, uawos_event_bus | 1 |
| uawos_agent_workforce | 30 | Medium | uawos_integrations, uawos_cli, uawos_pmcms, uawos_traceability | 2 |
| uawos_audit_ledger | 25 | Low | uawos_semantic_kernel_adapter, uawos_autogen_adapter | 3 |
| uawos_budget | 25 | Low | uawos_dtase, uawos_traceability, uawos_weaverouter | 1 |
| uawos_cli | 15 | Low | *None* | 2 |
| uawos_integrations | 25 | Low | uawos_cli, uawos_traceability | 3 |
| uawos_context | 20 | Low | uawos_sdk | 0 |
| uawos_dashboard_daemon | 15 | Low | *None* | 0 |
| uawos_decision | 20 | Low | uawos_pmcms | 1 |
| uawos_dtase | 20 | Low | uawos_traceability | 1 |
| uawos_weaverouter | 20 | Low | uawos_dtase, uawos_traceability | 2 |
| uawos_event_bus | 15 | Low | *None* | 3 |
| uawos_knowledge | 15 | Low | *None* | 2 |
| uawos_learning | 15 | Low | *None* | 1 |
| uawos_memory | 20 | Low | uawos_sdk | 2 |
| uawos_objective | 25 | Low | uawos_pmcms, uawos_sdk | 3 |
| uawos_outcome | 20 | Low | uawos_objective, uawos_pmcms, uawos_sdk | 2 |
| uawos_observability | 20 | Low | uawos_dtase, uawos_traceability, uawos_weaverouter | 1 |
| uawos_planning | 20 | Low | uawos_pmcms | 2 |
| uawos_pmcms | 15 | Low | *None* | 11 |
| uawos_resource | 20 | Low | uawos_pmcms | 2 |
| uawos_simulation | 20 | Low | uawos_pmcms | 2 |
| uawos_value | 20 | Low | uawos_pmcms | 1 |
| uawos_workflow | 20 | Low | uawos_pmcms | 2 |
| uawos_proactive_governance | 15 | Low | *None* | 1 |
| uawos_requirement_studio | 15 | Low | *None* | 1 |
| uawos_sandbox_runtime | 25 | Low | uawos_semantic_kernel_adapter, uawos_autogen_adapter | 3 |
| uawos_sdk | 15 | Low | *None* | 4 |
| uawos_traceability | 15 | Low | *None* | 4 |
| uawos_workforce | 15 | Low | *None* | 1 |
| uawos_autogen_adapter | 15 | Low | *None* | 5 |
| uawos_langgraph_adapter | 15 | Low | *None* | 3 |
| uawos_semantic_kernel_adapter | 15 | Low | *None* | 5 |

*Last updated: 2026-06-21T18:03:18+0530*
