# Engineering Debt Register

**Debt Summary Score:** 64 / 100

### Active TODOs and FIXMEs

| File | Line | Task / Details |
| :--- | :--- | :--- |
| uawos_proactive_governance.py | 104 | or line_strip == "# TODO" |

### Suppressed Warnings / Type Ignores

| File | Line | Suppressed Rule / Line Details |
| :--- | :--- | :--- |
| uawos_agent_runtime.py | 520 | `cls._registry[name] = fn  # type: ignore[assignment]` |
| uawos_budget.py | 5 | `allocate_action_budget,  # noqa: F401` |
| uawos_budget.py | 6 | `allocate_objective_budget,  # noqa: F401` |
| uawos_budget.py | 9 | `process_approval_request,  # noqa: F401` |
| uawos_budget.py | 10 | `record_agent_cost,  # noqa: F401` |
| uawos_budget.py | 11 | `submit_approval_request,  # noqa: F401` |
| uawos_dashboard_daemon.py | 17 | `from apps.api.main import app, start_server  # noqa: F401` |
| uawos_dashboard_daemon.py | 19 | `from interfaces.rest.auth import SECURE_TOKEN, decode_token_payload  # noqa: F401` |
| uawos_dashboard_daemon.py | 20 | `from interfaces.rest.system import daemon_loop, run_health_checks  # noqa: F401` |
| uawos_governance.py | 10 | `get_dynamic_agent_autonomy_level,  # noqa: F401` |
| uawos_governance.py | 14 | `run_governor_audit_analysis,  # noqa: F401` |
| uawos_governance.py | 16 | `from infrastructure.security.opa_client import evaluate_via_opa  # noqa: F401` |
| uawos_proactive_governance.py | 111 | `if any(s in line_strip for s in ["noqa", "type: ignore", "pylint: disable"]):` |
| uawos_traceability.py | 324 | `import uawos_dtase  # noqa: F401` |
| uawos_traceability.py | 391 | `import uawos_budget  # noqa: F401` |
| uawos_traceability.py | 568 | `import uawos_integrations  # noqa: F401` |
| uawos_workflow.py | 6 | `check_temporal_worker_queues,  # noqa: F401` |
| uawos_autogen_adapter.py | 87 | `import autogen  # noqa: F401` |
| uawos_langgraph_adapter.py | 70 | `import langgraph  # noqa: F401` |
| uawos_langgraph_adapter.py | 71 | `from langgraph.graph import END, StateGraph  # noqa: F401` |
| uawos_langgraph_adapter.py | 205 | `from langgraph.graph import StateGraph, END  # noqa` |
| uawos_semantic_kernel_adapter.py | 86 | `import semantic_kernel  # noqa: F401` |
| uawos_semantic_kernel_adapter.py | 316 | `id_int = int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**31 - 1)  # noqa: S324` |

*Last updated: 2026-06-22T06:52:35+0530*
