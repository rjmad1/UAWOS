"""
uawos_langgraph_adapter.py
==========================
UAWOS LangGraph Absorption Adapter — Wave 4 Deliverable

Provides a governed LangGraph runtime that sits BEHIND the UAWOS
IWorkflowRuntime and IAgentRuntime interfaces. Business workflows
NEVER import langgraph directly — they use this adapter via the
interface contracts.

Governance:
  - Every node transition calls IPolicyEvaluator before execution.
  - Every state snapshot is written to the UAWOS checkpointer.
  - Every lifecycle event is emitted with full Correlation/Causation IDs.
  - Iteration limit guard blocks infinite graph loops (RSK-RM-03).

Standards: WAAS, GCF v1.0, ESLS, KMLS
"""

from __future__ import annotations

import os
import time
import uuid
from collections.abc import Callable
from typing import Any

from uawos_agent_runtime import (
    AuditEntry,
    EventCategory,
    IAuditProvider,
    IPolicyEvaluator,
    ITraceProvider,
    LifecycleEvent,
    PolicyVerdict,
    UAWOSBaseAgentRuntime,
    UAWOSBaseWorkflowRuntime,
    UAWOSContext,
    UAWOSLocalToolExecutor,
)
from uawos_state_utils import load_state, save_state

# ---------------------------------------------------------------------------
# State File — required by load_state/save_state auto-resolution
# ---------------------------------------------------------------------------
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_langgraph_adapter_state.json")


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
    }


# ---------------------------------------------------------------------------
# LangGraph Availability Guard
# ---------------------------------------------------------------------------
_LANGGRAPH_AVAILABLE = False
try:
    import langgraph  # noqa: F401
    from langgraph.graph import END, StateGraph  # noqa: F401

    _LANGGRAPH_AVAILABLE = True
except ImportError:
    pass  # Adapter degrades gracefully — runs in simulation mode


# ---------------------------------------------------------------------------
# UAWOS State Schema Normalizer
#   Converts LangGraph state dicts to UAWOS-standard JSON schema before
#   writing to the checkpoint store.
# ---------------------------------------------------------------------------


def _normalize_state(raw_state: dict, context: UAWOSContext) -> dict:
    """
    Maps a LangGraph raw state dict to the UAWOS canonical state schema.
    This prevents framework-specific keys from bleeding into the audit store.
    """
    return {
        "schema_version": "1.0",
        "correlation_id": context.correlation_id,
        "causation_id": context.causation_id,
        "objective_id": context.objective_id,
        "workflow_id": context.workflow_id,
        "agent_id": context.agent_id,
        "action_id": context.action_id,
        "captured_at": time.time(),
        "state_payload": {
            k: (v if isinstance(v, (str, int, float, bool, list, dict, type(None))) else str(v))
            for k, v in raw_state.items()
        },
    }


# ---------------------------------------------------------------------------
# UAWOS SQL Checkpointer Adapter
#   Wave 2 stub — production replaces with direct Postgres INSERT via uawos_db
# ---------------------------------------------------------------------------


class UAWOSSqlCheckpointer:
    """
    Checkpointer that persists LangGraph state snapshots to UAWOS persistence.
    Production implementation: write rows to uawos_agent_checkpoints table in Postgres.
    Current implementation: write to runtime state JSON (Wave 2 stub).
    """

    def save(self, thread_id: str, state: dict, context: UAWOSContext) -> str:
        checkpoint_id = f"CKP-{uuid.uuid4().hex[:8].upper()}"
        normalized = _normalize_state(state, context)

        runtime_state = load_state(STATE_FILE, get_default_state)
        if "checkpoints" not in runtime_state:
            runtime_state["checkpoints"] = {}
        if thread_id not in runtime_state["checkpoints"]:
            runtime_state["checkpoints"][thread_id] = []

        runtime_state["checkpoints"][thread_id].append(
            {
                "checkpoint_id": checkpoint_id,
                "thread_id": thread_id,
                "state": normalized,
                "saved_at": time.time(),
            }
        )
        save_state(STATE_FILE, runtime_state)
        return checkpoint_id

    def load(self, thread_id: str) -> dict | None:
        runtime_state = load_state(STATE_FILE, get_default_state)
        checkpoints = runtime_state.get("checkpoints", {}).get(thread_id, [])
        if not checkpoints:
            return None
        return checkpoints[-1]["state"]

    def list_checkpoints(self, thread_id: str) -> list[dict]:
        runtime_state = load_state(STATE_FILE, get_default_state)
        return runtime_state.get("checkpoints", {}).get(thread_id, [])


# ---------------------------------------------------------------------------
# LangGraph Workflow Adapter — IWorkflowRuntime
# ---------------------------------------------------------------------------


class LangGraphWorkflowAdapter(UAWOSBaseWorkflowRuntime):
    """
    Governed LangGraph workflow runtime adapter.

    When LangGraph is installed:
      - Compiles a StateGraph from the workflow_definition node list.
      - Injects a pre-node interceptor that evaluates governance policy.
      - Uses UAWOSSqlCheckpointer after every node run.

    When LangGraph is NOT installed (development / Wave 0-3 stages):
      - Simulates graph execution deterministically.
      - All governance, event, and audit pipelines remain fully active.
    """

    def __init__(
        self,
        policy_evaluator: IPolicyEvaluator | None = None,
        audit_provider: IAuditProvider | None = None,
        trace_provider: ITraceProvider | None = None,
    ):
        super().__init__(policy_evaluator, audit_provider, trace_provider)
        self._checkpointer = UAWOSSqlCheckpointer()
        self._node_registry: dict[str, dict[str, Callable]] = {}
        self._langgraph_graphs: dict[str, Any] = {}

    def register_node(
        self,
        runtime_id: str,
        node_name: str,
        fn: Callable,
    ) -> None:
        """Register a callable as a named graph node."""
        if runtime_id not in self._node_registry:
            self._node_registry[runtime_id] = {}
        self._node_registry[runtime_id][node_name] = fn

    def compile_workflow(self, workflow_definition: dict) -> str:
        """
        Compile a workflow definition into a LangGraph StateGraph (or simulation).
        workflow_definition keys:
          - nodes: list[str] — ordered list of node names
          - edges: list[tuple[str, str]] — (from_node, to_node) pairs
          - conditional_edges: dict — {from_node: {condition_key: to_node}}
        """
        runtime_id = super().compile_workflow(workflow_definition)

        if _LANGGRAPH_AVAILABLE:
            # Build StateGraph with governance interceptor wrapping each node
            from langgraph.graph import StateGraph, END  # noqa

            graph = StateGraph(dict)

            nodes = workflow_definition.get("nodes", [])
            edges = workflow_definition.get("edges", [])

            for node in nodes:
                # Wrap each node with the governance interceptor
                graph.add_node(node, self._make_governed_node(node, runtime_id))

            for from_node, to_node in edges:
                if to_node == "__end__":
                    graph.add_edge(from_node, END)
                else:
                    graph.add_edge(from_node, to_node)

            if nodes:
                graph.set_entry_point(nodes[0])

            self._langgraph_graphs[runtime_id] = graph.compile()

        self._runtimes[runtime_id]["langgraph_available"] = _LANGGRAPH_AVAILABLE
        return runtime_id

    def _make_governed_node(self, node_name: str, runtime_id: str) -> Callable:
        """
        Creates a governance-wrapped node function for LangGraph.
        The interceptor calls OPA/OpenFGA before the actual node function runs.
        """

        def governed_node(state: dict) -> dict:
            # Reconstruct context from state metadata
            ctx = UAWOSContext.from_dict(state.get("__uawos_context__", {}))

            # Governance gate
            policy_result = self._policy.evaluate_policy(
                f"{runtime_id}:{node_name}",
                {"actor": ctx.actor, "actor_role": ctx.actor_role, "node": node_name},
            )
            if policy_result.verdict != PolicyVerdict.APPROVED:
                self._audit.write_audit(
                    AuditEntry(
                        event_type="NODE_BLOCKED",
                        actor=ctx.actor,
                        context=ctx.to_dict(),
                        decision="REJECTED",
                        provenance={"node": node_name, "reason": policy_result.reason},
                    )
                )
                return {**state, "__governance_block__": policy_result.reason}

            # Execute the registered node function
            user_fn = self._node_registry.get(runtime_id, {}).get(node_name)
            output = user_fn(state) if user_fn else state

            # Checkpoint after node execution
            child_ctx = ctx.child(f"{node_name}-{uuid.uuid4().hex[:4]}")
            self._checkpointer.save(runtime_id, output, child_ctx)

            # Emit ActionCompleted
            self._tracer.emit_event(
                LifecycleEvent(
                    event_type=EventCategory.ACTION_COMPLETED,
                    actor=ctx.actor,
                    correlation_id=ctx.correlation_id,
                    causation_id=ctx.action_id,
                    entity_ref=f"{runtime_id}:{node_name}",
                    payload={"node": node_name, "iteration": output.get("__iteration__", 0)},
                )
            )

            return output

        return governed_node

    def _do_run_step(
        self,
        runtime_id: str,
        step_id: str,
        state: dict,
        context: UAWOSContext,
    ) -> dict:
        """
        Run a single workflow step.
        - If LangGraph is available: invoke the compiled graph for this node.
        - If not: execute the registered node function directly (simulation mode).
        """
        state_with_ctx = {**state, "__uawos_context__": context.to_dict()}

        if _LANGGRAPH_AVAILABLE and runtime_id in self._langgraph_graphs:
            graph = self._langgraph_graphs[runtime_id]
            result = graph.invoke(state_with_ctx)
        else:
            # Simulation mode
            user_fn = self._node_registry.get(runtime_id, {}).get(step_id)
            result = user_fn(state_with_ctx) if user_fn else {**state_with_ctx, f"_{step_id}_output": "simulated"}

        # Always checkpoint the result
        checkpoint_id = self._checkpointer.save(runtime_id, result, context)
        result["__checkpoint_id__"] = checkpoint_id
        return result

    def replay_from_checkpoint(
        self,
        runtime_id: str,
        checkpoint_index: int,
        context: UAWOSContext,
    ) -> dict:
        """
        Time-travel: load a specific historical state checkpoint and return it.
        Production: extend to re-run subsequent steps from that state.
        """
        checkpoints = self._checkpointer.list_checkpoints(runtime_id)
        if not checkpoints or checkpoint_index >= len(checkpoints):
            return {"error": "Checkpoint not found."}

        target = checkpoints[checkpoint_index]
        self._audit.write_audit(
            AuditEntry(
                event_type="STATE_REPLAYED",
                actor=context.actor,
                context=context.to_dict(),
                decision="APPROVED",
                provenance={
                    "runtime_id": runtime_id,
                    "checkpoint_id": target["checkpoint_id"],
                    "replayed_at": time.time(),
                },
            )
        )
        return target["state"]


# ---------------------------------------------------------------------------
# LangGraph Agent Adapter — IAgentRuntime
# ---------------------------------------------------------------------------


class LangGraphAgentAdapter(UAWOSBaseAgentRuntime):
    """
    Governed LangGraph agent runtime adapter.
    Agents are graph-node functions registered per agent_class.
    Framework calls are made ONLY inside _do_execute.
    Business code uses IAgentRuntime.execute_task() exclusively.
    """

    def __init__(
        self,
        policy_evaluator: IPolicyEvaluator | None = None,
        audit_provider: IAuditProvider | None = None,
        trace_provider: ITraceProvider | None = None,
        tool_executor: UAWOSLocalToolExecutor | None = None,
    ):
        super().__init__(policy_evaluator, audit_provider, trace_provider, tool_executor)
        self._workflow_runtime = LangGraphWorkflowAdapter(policy_evaluator, audit_provider, trace_provider)
        self._agent_graph_registry: dict[str, str] = {}  # agent_id -> runtime_id

    def provision_agent_graph(
        self,
        agent_id: str,
        workflow_definition: dict,
        node_functions: dict[str, Callable],
    ) -> str:
        """
        Compile a stateful LangGraph for this agent and register it.
        node_functions: {node_name: callable}
        Returns the runtime_id.
        """
        runtime_id = self._workflow_runtime.compile_workflow(workflow_definition)
        for node_name, fn in node_functions.items():
            self._workflow_runtime.register_node(runtime_id, node_name, fn)

        self._agent_graph_registry[agent_id] = runtime_id
        try:
            state = load_state(STATE_FILE, get_default_state)
            if agent_id in state.get("registered_agents", {}):
                state["registered_agents"][agent_id]["runtime_id"] = runtime_id
                save_state(STATE_FILE, state)
        except Exception:
            pass
        return runtime_id

    def _do_execute(self, task_payload: dict, context: UAWOSContext) -> Any:
        """
        Framework-specific execution: run the agent's LangGraph.
        Called from the governed execute_task() base method ONLY after policy APPROVED.
        """
        agent_id = context.agent_id
        runtime_id = self._agent_graph_registry.get(agent_id)

        if not runtime_id:
            return {"result": "No graph provisioned for agent. Returning base response.", "agent_id": agent_id}

        # Run the first step of the agent's workflow graph
        step_result = self._workflow_runtime.run_step(
            runtime_id=runtime_id,
            step_id=task_payload.get("entry_node", "start"),
            state=task_payload,
            context=context,
        )
        return step_result


# ---------------------------------------------------------------------------
# Semantic Kernel Stub Adapter — IAgentRuntime (Wave 5 Placeholder)
# ---------------------------------------------------------------------------


class SemanticKernelAgentAdapter(UAWOSBaseAgentRuntime):
    """
    Wave 5 placeholder adapter for Microsoft Semantic Kernel.
    Enforces all governance interfaces — SK plugin execution goes inside _do_execute.
    Production: connect the SK Kernel, register plugins, inject execution filters.
    """

    def _do_execute(self, task_payload: dict, context: UAWOSContext) -> Any:
        """
        Production: invoke the SK Kernel.invoke() call here.
        All governance, audit, and trace pipelines are handled by the base class.
        """
        # Wave 5: Replace stub with:
        #   kernel = Kernel()
        #   kernel.add_plugin(...)
        #   result = await kernel.invoke(...)
        return {
            "result": "Semantic Kernel adapter stub — Wave 5 not yet ingested.",
            "agent_id": context.agent_id,
            "wave": 5,
        }


# ---------------------------------------------------------------------------
# AutoGen Sandbox Adapter — IAgentRuntime (Wave 6 Placeholder)
# ---------------------------------------------------------------------------


class AutoGenSandboxAdapter(UAWOSBaseAgentRuntime):
    """
    Wave 6 sandbox adapter for Microsoft AutoGen.
    AutoGen conversational agents run in an isolated Docker container.
    All tool calls, code executions, and message outputs are audited.

    CRITICAL RESTRICTION: AutoGen's UserProxyAgent code execution MUST route
    through the Docker Sandbox REST API — never via local subprocess.
    """

    SANDBOX_ENDPOINT = "http://localhost:8000/execute"  # Wave 3 Docker sandbox API

    def _do_execute(self, task_payload: dict, context: UAWOSContext) -> Any:
        """
        Production: invoke AutoGen conversation inside Docker sandbox.
        Wave 6: Replace stub with containerised AutoGen execution.
        """
        return {
            "result": "AutoGen sandbox adapter stub — Wave 6 not yet ingested.",
            "agent_id": context.agent_id,
            "wave": 6,
            "sandbox_url": self.SANDBOX_ENDPOINT,
        }


# ---------------------------------------------------------------------------
# Self-Tests
# ---------------------------------------------------------------------------


def run_self_tests():
    print("Running LangGraph Adapter self tests...")

    state_seed = get_default_state()
    state_seed["policies"] = {
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
    import uawos_db

    uawos_db.db_save_state("uawos_governance_state", state_seed)
    uawos_db.db_save_state("uawos_agent_runtime_state", state_seed)
    uawos_db.db_save_state("uawos_langgraph_adapter_state", state_seed)

    ctx = UAWOSContext(
        objective_id="OBJ-001",
        workflow_id="WF-LG-001",
        actor="Lead Engineer",
        actor_role="Lead Engineer",
    )

    # LG-01: State normalization
    normalized = _normalize_state({"messages": ["hello"], "step": 1}, ctx)
    assert normalized["schema_version"] == "1.0"
    assert "state_payload" in normalized
    print("  [PASS] LG-01: State normalization verified.")

    # LG-02: Checkpointer save/load
    ckp = UAWOSSqlCheckpointer()
    ckp_id = ckp.save("WF-TEST", {"key": "value"}, ctx)
    assert ckp_id.startswith("CKP-")
    loaded = ckp.load("WF-TEST")
    assert loaded["state_payload"]["key"] == "value"
    print("  [PASS] LG-02: UAWOSSqlCheckpointer save/load verified.")

    # LG-03: LangGraph workflow adapter — compile
    adapter = LangGraphWorkflowAdapter()
    rid = adapter.compile_workflow(
        {
            "nodes": ["start", "process", "end"],
            "edges": [("start", "process"), ("process", "end"), ("end", "__end__")],
        }
    )
    assert rid.startswith("WF-")
    print(
        f"  [PASS] LG-03: LangGraphWorkflowAdapter.compile_workflow verified (LG={'available' if _LANGGRAPH_AVAILABLE else 'simulation'})."
    )

    # LG-04: Node registration + step execution
    adapter.register_node(rid, "start", lambda s: {**s, "started": True})
    result = adapter.run_step(rid, "start", {"input": "test"}, ctx.child())
    assert result["status"] == "OK"
    print("  [PASS] LG-04: LangGraphWorkflowAdapter.run_step verified.")

    # LG-05: Checkpoint list after step
    checkpoints = ckp.list_checkpoints(rid)
    assert len(checkpoints) >= 1
    print("  [PASS] LG-05: Post-step checkpoint persistence verified.")

    # LG-06: Replay from checkpoint
    replayed = adapter.replay_from_checkpoint(rid, 0, ctx)
    assert "state_payload" in replayed
    print("  [PASS] LG-06: LangGraphWorkflowAdapter.replay_from_checkpoint verified.")

    # LG-07: Agent adapter — register + provision graph
    agent_adapter = LangGraphAgentAdapter()
    agent_adapter.register_agent("AGENT-LG-01", "PlannerAgent", ["plan_generation"], ctx)
    prov_rid = agent_adapter.provision_agent_graph(
        "AGENT-LG-01",
        {"nodes": ["start"], "edges": []},
        {"start": lambda s: {**s, "plan_generated": True}},
    )
    assert prov_rid.startswith("WF-")
    print("  [PASS] LG-07: LangGraphAgentAdapter.provision_agent_graph verified.")

    # LG-08: Agent task execution (approved)
    exec_ctx = ctx.child()
    exec_ctx.agent_id = "AGENT-LG-01"
    task_result = agent_adapter.execute_task(
        {"entry_node": "start", "actor": "Lead Engineer", "actor_role": "Lead Engineer"},
        exec_ctx,
    )
    assert task_result["status"] == "APPROVED"
    print("  [PASS] LG-08: LangGraphAgentAdapter.execute_task (APPROVED) verified.")

    # LG-09: Agent task blocked (GPLv3)
    blocked_ctx = ctx.child()
    blocked_ctx.agent_id = "AGENT-LG-01"
    blocked = agent_adapter.execute_task(
        {"uses_marker_library": True, "entry_node": "start"},
        blocked_ctx,
    )
    assert blocked["status"] == "REJECTED"
    print("  [PASS] LG-09: LangGraphAgentAdapter.execute_task (REJECTED — GPLv3) verified.")

    # LG-10: SK stub adapter
    sk_adapter = SemanticKernelAgentAdapter()
    sk_adapter.register_agent("AGENT-SK-01", "SemanticKernelAgent", ["plugin_execution"], ctx)
    sk_result = sk_adapter.execute_task(
        {"actor": "Lead Engineer", "actor_role": "Lead Engineer"},
        ctx.child(),
    )
    assert sk_result["status"] == "APPROVED"
    assert "Semantic Kernel" in sk_result["output"]["result"]
    print("  [PASS] LG-10: SemanticKernelAgentAdapter stub verified.")

    # LG-11: AutoGen stub adapter
    ag_adapter = AutoGenSandboxAdapter()
    ag_adapter.register_agent("AGENT-AG-01", "AutoGenConversable", ["group_chat"], ctx)
    ag_result = ag_adapter.execute_task(
        {"actor": "Lead Engineer", "actor_role": "Lead Engineer"},
        ctx.child(),
    )
    assert ag_result["status"] == "APPROVED"
    assert "AutoGen" in ag_result["output"]["result"]
    print("  [PASS] LG-11: AutoGenSandboxAdapter stub verified.")

    print("\nAll LangGraph Adapter self tests completed successfully!")


if __name__ == "__main__":
    run_self_tests()
