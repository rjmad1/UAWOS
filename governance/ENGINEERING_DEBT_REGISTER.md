# Engineering Debt Register

**Debt Summary Score:** 64 / 100

### Active TODOs and FIXMEs

| File | Line | Task / Details |
| :--- | :--- | :--- |
| uawos_proactive_governance.py | 81 | # Scan for TODOs and suppressions |
| uawos_proactive_governance.py | 84 | # TODO |
| uawos_proactive_governance.py | 85 | if "TODO" in line_strip or "FIXME" in line_strip: |
| uawos_proactive_governance.py | 86 | match = re.search(r"(?:TODO|FIXME)[:\s]+(.*)", line_strip, re.IGNORECASE) |
| uawos_proactive_governance.py | 315 | Accumulation |
| uawos_proactive_governance.py | 322 | lines in source files.", |
| uawos_proactive_governance.py | 329 | comments.", |
| uawos_proactive_governance.py | 410 | # Future Risk Score: derived from TODOs, circular paths, and unmitigated warnings |
| uawos_proactive_governance.py | 994 | f.write("### Active TODOs and FIXMEs\n\n") |

### Suppressed Warnings / Type Ignores

| File | Line | Suppressed Rule / Line Details |
| :--- | :--- | :--- |
| uawos_agent_runtime.py | 520 | `cls._registry[name] = fn  # type: ignore[assignment]` |
| uawos_autogen_adapter.py | 87 | `import autogen  # noqa: F401` |
| uawos_langgraph_adapter.py | 70 | `import langgraph  # noqa: F401` |
| uawos_langgraph_adapter.py | 71 | `from langgraph.graph import END, StateGraph  # noqa: F401` |
| uawos_langgraph_adapter.py | 205 | `from langgraph.graph import StateGraph, END  # noqa` |
| uawos_proactive_governance.py | 90 | `if any(s in line_strip for s in ["noqa", "type: ignore", "pylint: disable"]):` |
| uawos_semantic_kernel_adapter.py | 86 | `import semantic_kernel  # noqa: F401` |

*Last updated: 2026-06-12T14:34:09+0530*
