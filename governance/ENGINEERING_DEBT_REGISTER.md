# Engineering Debt Register

**Debt Summary Score:** 58 / 100

### Active TODOs and FIXMEs

| File | Line | Task / Details |
| :--- | :--- | :--- |
| uawos_proactive_governance.py | 90 | "if \"TODO\" in", |
| uawos_proactive_governance.py | 91 | "re.search(r\"(?:TODO|FIXME)", |
| uawos_proactive_governance.py | 97 | ]) or line_strip == "# TODO": |

### Suppressed Warnings / Type Ignores

| File | Line | Suppressed Rule / Line Details |
| :--- | :--- | :--- |
| uawos_agent_runtime.py | 520 | `cls._registry[name] = fn  # type: ignore[assignment]` |
| uawos_autogen_adapter.py | 87 | `import autogen  # noqa: F401` |
| uawos_langgraph_adapter.py | 70 | `import langgraph  # noqa: F401` |
| uawos_langgraph_adapter.py | 71 | `from langgraph.graph import END, StateGraph  # noqa: F401` |
| uawos_langgraph_adapter.py | 205 | `from langgraph.graph import StateGraph, END  # noqa` |
| uawos_proactive_governance.py | 103 | `if any(s in line_strip for s in ["noqa", "type: ignore", "pylint: disable"]):` |
| uawos_semantic_kernel_adapter.py | 86 | `import semantic_kernel  # noqa: F401` |
| uawos_semantic_kernel_adapter.py | 316 | `id_int = int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**31 - 1)  # noqa: S324` |
| uawos_traceability.py | 325 | `import uawos_dtase  # noqa: F401` |
| uawos_traceability.py | 392 | `import uawos_budget  # noqa: F401` |
| uawos_traceability.py | 569 | `import uawos_integrations  # noqa: F401` |

*Last updated: 2026-06-13T06:30:04+0530*
