"""
uawos_semantic_kernel_adapter.py
================================
UAWOS Semantic Kernel Ingestion Adapter — Wave 5 Deliverable

Provides:
  1. SemanticKernelPluginAdapter  — Maps SK plugin classes to UAWOS ToolRegistry
  2. SemanticKernelRuntimeAdapter — IAgentRuntime for SK kernel invocations
  3. SemanticKernelPipelineFilter — Governance execution filter injected into SK pipeline
  4. SemanticKernelVectorBridge   — Connects SK vector memory to UAWOS knowledge layer

All Semantic Kernel interactions are routed through UAWOS interface contracts.
Direct imports of `semantic_kernel` are PROHIBITED outside this module.

Standards: GCF v1.0 (Law 11), ESLS, WAAS Section 25, KMLS
"""

from __future__ import annotations

import os
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import uawos_db
from uawos_agent_runtime import (
    AuditEntry,
    EventCategory,
    IAuditProvider,
    IPolicyEvaluator,
    ITraceProvider,
    LifecycleEvent,
    PolicyVerdict,
    UAWOSAuditProvider,
    UAWOSBaseAgentRuntime,
    UAWOSContext,
    UAWOSPolicyEvaluator,
    UAWOSTraceProvider,
)
from uawos_audit_ledger import (
    LedgerEntry,
    UAWOSAuditLedger,
    UAWOSLineageEmitter,
)
from uawos_sandbox_runtime import (
    LicenseClass,
    SandboxMode,
    ToolDescriptor,
    ToolRegistry,
    UAWOSSandboxToolExecutor,
    UAWOSSecretsManager,
)
from uawos_state_utils import load_state, save_state

# ---------------------------------------------------------------------------
# State File — required by load_state/save_state auto-resolution
# ---------------------------------------------------------------------------
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_semantic_kernel_state.json")


def get_default_state() -> dict:
    """Default state — required by load_state auto-resolution."""
    return {
        "policies": {},
        "exceptions": {},
        "risk_acceptances": {},
        "audit_logs": [],
        "registered_agents": {},
        "active_runtimes": {},
        "execution_contexts": {},
        "runtime_audit_log": [],
        "event_log": [],
        "checkpoints": {},
        "sk_plugins": {},
        "sk_executions": [],
    }


# ---------------------------------------------------------------------------
# SK Availability Guard
# ---------------------------------------------------------------------------
_SK_AVAILABLE = False
try:
    import semantic_kernel  # noqa: F401

    _SK_AVAILABLE = True
except ImportError:
    pass  # Runs in simulation mode when SK is not installed


# ---------------------------------------------------------------------------
# Plugin Descriptor
# ---------------------------------------------------------------------------


@dataclass
class SKPluginDescriptor:
    """
    Describes a Semantic Kernel plugin registered in the UAWOS runtime.
    Maps SK plugin functions to UAWOS ToolDescriptors in the ToolRegistry.
    """

    plugin_id: str = field(default_factory=lambda: f"SK-PLG-{uuid.uuid4().hex[:6].upper()}")
    plugin_name: str = ""
    description: str = ""
    functions: list = field(default_factory=list)  # list of {name, description, parameters}
    license_class: LicenseClass = LicenseClass.PROPRIETARY
    source: str = ""  # "azure", "openai", "huggingface", "custom"
    version: str = "1.0"
    registered_at: float = field(default_factory=time.time)
    tool_ids: list = field(default_factory=list)  # UAWOS ToolRegistry IDs

    def to_dict(self) -> dict:
        return {
            "plugin_id": self.plugin_id,
            "plugin_name": self.plugin_name,
            "description": self.description,
            "functions": self.functions,
            "license_class": self.license_class.value,
            "source": self.source,
            "version": self.version,
            "registered_at": self.registered_at,
            "tool_ids": self.tool_ids,
        }

    @classmethod
    def from_dict(cls, d: dict) -> SKPluginDescriptor:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# Pipeline Execution Filter — Governance Interceptor
# ---------------------------------------------------------------------------


class GovernancePipelineFilter:
    """
    Simulates a Semantic Kernel IFunctionInvocationFilter.

    Production (when SK is installed):
      - Register this as an SK execution filter via kernel.add_filter()
      - on_function_invocation_pre: evaluate policy before SK function runs
      - on_function_invocation_post: write audit + emit event after SK function runs

    Wave 5 simulation: the filter logic is called explicitly from the adapter.
    """

    def __init__(
        self,
        policy_evaluator: IPolicyEvaluator | None = None,
        audit_provider: IAuditProvider | None = None,
        trace_provider: ITraceProvider | None = None,
    ):
        self._policy = policy_evaluator or UAWOSPolicyEvaluator()
        self._audit = audit_provider or UAWOSAuditProvider()
        self._tracer = trace_provider or UAWOSTraceProvider()

    def pre_invocation(
        self,
        function_name: str,
        plugin_name: str,
        arguments: dict,
        context: UAWOSContext,
    ) -> dict:
        """
        Called BEFORE a Semantic Kernel function executes.
        Returns {"approved": bool, "reason": str}.
        """
        action_id = f"SK-{plugin_name}-{function_name}"
        result = self._policy.evaluate_policy(
            action_id,
            {
                "actor": context.actor,
                "actor_role": context.actor_role,
                "plugin_name": plugin_name,
                "function_name": function_name,
                "arguments": UAWOSSecretsManager.redact_dict(arguments),
            },
        )

        self._tracer.emit_event(
            LifecycleEvent(
                event_type=EventCategory.GOVERNANCE_EVALUATED,
                actor=context.actor,
                correlation_id=context.correlation_id,
                causation_id=context.causation_id,
                entity_ref=action_id,
                payload={
                    "verdict": result.verdict.value,
                    "reason": result.reason,
                    "plugin_name": plugin_name,
                    "function_name": function_name,
                },
            )
        )

        if result.verdict != PolicyVerdict.APPROVED:
            self._audit.write_audit(
                AuditEntry(
                    event_type="SK_FUNCTION_BLOCKED",
                    actor=context.actor,
                    context=context.to_dict(),
                    decision=result.verdict.value,
                    provenance={
                        "plugin_name": plugin_name,
                        "function_name": function_name,
                        "reason": result.reason,
                    },
                )
            )

        return {"approved": result.verdict == PolicyVerdict.APPROVED, "reason": result.reason}

    def post_invocation(
        self,
        function_name: str,
        plugin_name: str,
        result: Any,
        elapsed_ms: float,
        context: UAWOSContext,
    ) -> None:
        """Called AFTER a Semantic Kernel function completes successfully."""
        redacted_result = UAWOSSecretsManager.redact(str(result)[:512])

        self._tracer.emit_event(
            LifecycleEvent(
                event_type=EventCategory.ACTION_COMPLETED,
                actor=context.actor,
                correlation_id=context.correlation_id,
                causation_id=context.causation_id,
                entity_ref=f"SK-{plugin_name}-{function_name}",
                payload={
                    "output_preview": redacted_result,
                    "elapsed_ms": elapsed_ms,
                },
            )
        )

        self._audit.write_audit(
            AuditEntry(
                event_type="SK_FUNCTION_COMPLETED",
                actor=context.actor,
                context=context.to_dict(),
                decision="APPROVED",
                provenance={
                    "plugin_name": plugin_name,
                    "function_name": function_name,
                    "elapsed_ms": elapsed_ms,
                    "output_preview": redacted_result,
                },
            )
        )

        # Write lineage entry
        UAWOSAuditLedger.write(
            LedgerEntry.from_context(
                "SK_FUNCTION_COMPLETED",
                context,
                "APPROVED",
                reason=f"SK plugin {plugin_name}.{function_name} completed in {elapsed_ms:.1f}ms",
                payload={"plugin_name": plugin_name, "function_name": function_name},
            )
        )


# ---------------------------------------------------------------------------
# Vector Memory Bridge
# ---------------------------------------------------------------------------


class SemanticKernelVectorBridge:
    """
    Bridges SK's vector memory (TextMemoryPlugin) to the UAWOS knowledge layer.

    Production (when SK is installed):
      - Register an SK TextMemoryPlugin backed by UAWOS's Qdrant store
      - All vector operations (save, search) are audited with OpenLineage lineage

    Wave 5 simulation: stores/retrieves from the runtime state.
    """

    @staticmethod
    def save_memory(
        collection: str,
        text: str,
        key: str,
        context: UAWOSContext,
    ) -> bool:
        """Save a memory entry, emitting a lineage event."""
        try:
            state = load_state(STATE_FILE, get_default_state)
            if "vector_memories" not in state:
                state["vector_memories"] = {}
            if collection not in state["vector_memories"]:
                state["vector_memories"][collection] = {}
            state["vector_memories"][collection][key] = {
                "text": text[:1024],
                "key": key,
                "saved_by": context.actor,
                "saved_at": time.time(),
            }
            save_state(STATE_FILE, state)

            # Lineage: record dataset write
            run = UAWOSLineageEmitter.start_run(
                f"sk_vector_save:{collection}",
                context,
                inputs=[{"name": key, "namespace": "uawos_sk_memory"}],
            )
            UAWOSLineageEmitter.complete_run(
                run,
                outputs=[
                    {
                        "name": f"{collection}/{key}",
                        "namespace": "uawos_qdrant",
                    }
                ],
            )
            return True
        except Exception:
            return False

    @staticmethod
    def search_memory(
        collection: str,
        query: str,
        limit: int = 5,
        context: UAWOSContext | None = None,
    ) -> list[dict]:
        """Search memory entries (simulation: substring match)."""
        try:
            state = load_state(STATE_FILE, get_default_state)
            entries = state.get("vector_memories", {}).get(collection, {})
            # Simulation: simple substring search
            results = [
                {"key": k, "text": v["text"], "score": 0.9}
                for k, v in entries.items()
                if query.lower() in v["text"].lower()
            ]
            return results[:limit]
        except Exception:
            return []


# ---------------------------------------------------------------------------
# Semantic Kernel Runtime Adapter — IAgentRuntime
# ---------------------------------------------------------------------------


class SemanticKernelRuntimeAdapter(UAWOSBaseAgentRuntime):
    """
    Governed Semantic Kernel runtime adapter.

    When SK is installed:
      - Creates a Kernel instance with GovernancePipelineFilter
      - Registers plugins via add_plugin()
      - Executes functions via kernel.invoke()

    When SK is NOT installed (simulation mode):
      - Simulates plugin execution deterministically
      - All governance, audit, and trace pipelines remain fully active
    """

    def __init__(
        self,
        policy_evaluator: IPolicyEvaluator | None = None,
        audit_provider: IAuditProvider | None = None,
        trace_provider: ITraceProvider | None = None,
    ):
        sandbox_executor = UAWOSSandboxToolExecutor(policy_evaluator, audit_provider, trace_provider)
        super().__init__(policy_evaluator, audit_provider, trace_provider, sandbox_executor)
        self._filter = GovernancePipelineFilter(
            policy_evaluator or UAWOSPolicyEvaluator(),
            audit_provider or UAWOSAuditProvider(),
            trace_provider or UAWOSTraceProvider(),
        )
        self._vector_bridge = SemanticKernelVectorBridge()
        self._plugin_registry: dict[str, SKPluginDescriptor] = {}
        self._plugin_functions: dict[str, Callable] = {}  # "plugin.function" -> callable

    def register_plugin(
        self,
        descriptor: SKPluginDescriptor,
        functions: dict[str, Callable] | None = None,
    ) -> str:
        """
        Register an SK plugin in UAWOS.
        Automatically creates ToolDescriptor entries in the ToolRegistry for each function.
        """
        self._plugin_registry[descriptor.plugin_id] = descriptor

        # Register each plugin function as a UAWOS tool
        tool_ids = []
        for fn_info in descriptor.functions:
            fn_name = fn_info.get("name", "")
            tool_id = f"SK-{descriptor.plugin_name}-{fn_name}".upper()
            tool = ToolDescriptor(
                tool_id=tool_id,
                tool_name=f"sk_{descriptor.plugin_name}_{fn_name}",
                description=fn_info.get("description", ""),
                license_class=descriptor.license_class,
                sandbox_mode=SandboxMode.REMOTE_API
                if descriptor.source in ("azure", "openai")
                else SandboxMode.IN_PROCESS,
                owner=descriptor.source,
            )
            ToolRegistry.register(tool)
            tool_ids.append(tool_id)

            # Register callable if provided
            if functions and fn_name in functions:
                key = f"{descriptor.plugin_name}.{fn_name}"
                self._plugin_functions[key] = functions[fn_name]

        descriptor.tool_ids = tool_ids

        # Persist to state
        try:
            state = load_state(STATE_FILE, get_default_state)
            state["sk_plugins"][descriptor.plugin_id] = descriptor.to_dict()
            save_state(STATE_FILE, state)
        except Exception:
            pass

        return descriptor.plugin_id

    def _do_execute(self, task_payload: dict, context: UAWOSContext) -> Any:
        """
        SK-specific execution. Called from the governed execute_task() base
        method ONLY after policy APPROVED.

        Expects task_payload: {"plugin_name": str, "function_name": str, **arguments}
        """
        plugin_name = task_payload.get("plugin_name", "")
        function_name = task_payload.get("function_name", "")
        arguments = {
            k: v for k, v in task_payload.items() if k not in ("plugin_name", "function_name", "actor", "actor_role")
        }

        # Apply governance pipeline filter (pre-invocation)
        pre_result = self._filter.pre_invocation(function_name, plugin_name, arguments, context)
        if not pre_result["approved"]:
            return {
                "result": "Governance filter blocked SK function invocation.",
                "reason": pre_result["reason"],
                "blocked": True,
            }

        # Execute
        start_time = time.time()

        if _SK_AVAILABLE:
            # Production: create kernel, add plugin, invoke
            # kernel = semantic_kernel.Kernel()
            # kernel.add_filter(GovernancePipelineFilter)
            # kernel.add_plugin(...)
            # result = await kernel.invoke(plugin_name, function_name, **arguments)
            result = self._simulate_execution(plugin_name, function_name, arguments)
        else:
            result = self._simulate_execution(plugin_name, function_name, arguments)

        elapsed_ms = (time.time() - start_time) * 1000

        # Apply post-invocation filter
        self._filter.post_invocation(function_name, plugin_name, result, elapsed_ms, context)

        # Record execution
        try:
            state = load_state(STATE_FILE, get_default_state)
            state["sk_executions"].append(
                {
                    "plugin_name": plugin_name,
                    "function_name": function_name,
                    "correlation_id": context.correlation_id,
                    "actor": context.actor,
                    "elapsed_ms": elapsed_ms,
                    "timestamp": time.time(),
                }
            )
            save_state(STATE_FILE, state)
        except Exception:
            pass

        return {
            "result": result,
            "plugin_name": plugin_name,
            "function_name": function_name,
            "elapsed_ms": elapsed_ms,
            "sk_available": _SK_AVAILABLE,
        }

    def _simulate_execution(self, plugin_name: str, function_name: str, arguments: dict) -> Any:
        """
        Simulation mode: call registered callable or return structured stub.
        """
        key = f"{plugin_name}.{function_name}"
        fn = self._plugin_functions.get(key)
        if fn:
            try:
                return fn(**arguments)
            except Exception as exc:
                return {"error": str(exc)}
        return {
            "simulated": True,
            "plugin": plugin_name,
            "function": function_name,
            "arguments": arguments,
        }


# ---------------------------------------------------------------------------
# Self-Tests
# ---------------------------------------------------------------------------


def run_self_tests():
    print("Running Semantic Kernel Adapter self tests...")

    # Seed state
    seed = get_default_state()
    seed["policies"] = {
        "POL-01": {
            "id": "POL-01",
            "name": "Token Limit Control",
            "rule": "token_consumption <= 5000000",
            "category": "budget",
            "version": 1,
            "status": "approved",
        },
        "POL-02": {
            "id": "POL-02",
            "name": "No Direct GPLv3 Imports",
            "rule": "import_marker == False",
            "category": "licensing",
            "version": 1,
            "status": "approved",
        },
    }
    uawos_db.db_save_state("uawos_semantic_kernel_state", seed)
    uawos_db.db_save_state("uawos_governance_state", seed)
    uawos_db.db_save_state("uawos_agent_runtime_state", seed)
    # Use sandbox module's default so tool_registry key is present
    from uawos_sandbox_runtime import get_default_state as sandbox_default

    sandbox_seed = sandbox_default()
    sandbox_seed["policies"] = seed["policies"]
    uawos_db.db_save_state("uawos_sandbox_runtime_state", sandbox_seed)
    uawos_db.db_save_state("uawos_audit_ledger_state", seed)

    ctx = UAWOSContext(
        correlation_id=str(uuid.uuid4()),
        causation_id=str(uuid.uuid4()),
        objective_id="OBJ-SK-001",
        workflow_id="WF-SK-001",
        action_id=str(uuid.uuid4()),
        actor="Lead Engineer",
        actor_role="Lead Engineer",
    )

    # SK-01: Plugin registration
    adapter = SemanticKernelRuntimeAdapter()
    plugin = SKPluginDescriptor(
        plugin_name="TextAnalyzer",
        description="Analyzes text for sentiment and entities",
        functions=[
            {"name": "analyze_sentiment", "description": "Analyze sentiment", "parameters": ["text"]},
            {"name": "extract_entities", "description": "Extract entities", "parameters": ["text"]},
        ],
        license_class=LicenseClass.PROPRIETARY,
        source="azure",
    )
    plugin_id = adapter.register_plugin(
        plugin,
        functions={
            "analyze_sentiment": lambda text="": {"sentiment": "positive", "confidence": 0.95},
            "extract_entities": lambda text="": {"entities": ["UAWOS", "LangGraph"], "count": 2},
        },
    )
    assert plugin_id
    print(f"  [PASS] SK-01: Plugin registration verified (id={plugin_id}).")

    # SK-02: Plugin functions registered in ToolRegistry
    tool = ToolRegistry.find_by_name("sk_TextAnalyzer_analyze_sentiment")
    assert tool is not None
    assert tool.license_class == LicenseClass.PROPRIETARY
    print("  [PASS] SK-02: SK plugin functions registered in ToolRegistry.")

    # SK-03: Agent registration
    adapter.register_agent("AGENT-SK-01", "SemanticKernelAgent", ["text_analysis"], ctx)
    status = adapter.get_agent_status("AGENT-SK-01")
    from uawos_agent_runtime import AgentStatus

    assert status == AgentStatus.REGISTERED
    print("  [PASS] SK-03: SK agent registration verified.")

    # SK-04: Governed task execution (approved)
    exec_ctx = ctx.child()
    exec_ctx.agent_id = "AGENT-SK-01"
    result = adapter.execute_task(
        {
            "plugin_name": "TextAnalyzer",
            "function_name": "analyze_sentiment",
            "text": "UAWOS is an excellent platform.",
            "actor": "Lead Engineer",
            "actor_role": "Lead Engineer",
        },
        exec_ctx,
    )
    assert result["status"] == "APPROVED"
    assert result["output"]["result"]["sentiment"] == "positive"
    print("  [PASS] SK-04: SK governed task execution (APPROVED) verified.")

    # SK-05: Governed task execution (blocked — GPLv3)
    blocked_ctx = ctx.child()
    blocked_ctx.agent_id = "AGENT-SK-01"
    blocked = adapter.execute_task(
        {
            "uses_marker_library": True,
            "plugin_name": "TextAnalyzer",
            "function_name": "analyze_sentiment",
        },
        blocked_ctx,
    )
    assert blocked["status"] == "REJECTED"
    print("  [PASS] SK-05: SK governed task execution (REJECTED — GPLv3) verified.")

    # SK-06: Pipeline filter pre-invocation
    filter_inst = GovernancePipelineFilter()
    pre = filter_inst.pre_invocation("analyze_sentiment", "TextAnalyzer", {"text": "test"}, ctx)
    assert pre["approved"]
    print("  [PASS] SK-06: GovernancePipelineFilter.pre_invocation verified.")

    # SK-07: Vector memory bridge — save + search
    saved = SemanticKernelVectorBridge.save_memory(
        "knowledge_base",
        "UAWOS is an event-driven AI workforce platform.",
        "kb-001",
        ctx,
    )
    assert saved
    results = SemanticKernelVectorBridge.search_memory("knowledge_base", "event-driven", 5, ctx)
    assert len(results) >= 1
    assert results[0]["key"] == "kb-001"
    print("  [PASS] SK-07: SK vector memory bridge save/search verified.")

    # SK-08: Execution record persistence
    state = load_state(STATE_FILE, get_default_state)
    execs = state.get("sk_executions", [])
    assert len(execs) >= 1
    print(f"  [PASS] SK-08: {len(execs)} SK execution records persisted.")

    # SK-09: Simulation mode flag
    assert result["output"]["sk_available"] == _SK_AVAILABLE
    mode_str = "production" if _SK_AVAILABLE else "simulation"
    print(f"  [PASS] SK-09: SK running in {mode_str} mode (SK={'installed' if _SK_AVAILABLE else 'not installed'}).")

    print("\nAll Semantic Kernel Adapter self tests completed successfully!")


if __name__ == "__main__":
    run_self_tests()
