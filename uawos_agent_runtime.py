"""
uawos_agent_runtime.py
======================
UAWOS Agent Runtime Interface Layer — Wave 0 Deliverable

Provides the canonical abstract interface contracts that every framework adapter
(LangGraph, Semantic Kernel, AutoGen) must implement before being ingested.

Business workflows MUST only interact with these interfaces. Direct imports of
langgraph, semantic_kernel, or autogen in business modules are PROHIBITED.

Governance Principle: No framework becomes a first-class citizen inside UAWOS.
Frameworks are implementation details behind UAWOS abstractions.

Standards: WAAS, GCF v1.0, ESLS, KMLS
FR Range:  FR-091 to FR-100 (Agent Workforce), FR-061 to FR-070 (Workflow)
"""

from __future__ import annotations

import asyncio
import os
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import uawos_governance
from uawos_state_utils import load_state, save_state

# ---------------------------------------------------------------------------
# Agent Runtime State File — required by load_state/save_state auto-resolution
# ---------------------------------------------------------------------------
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_agent_runtime_state.json")


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
# Enumerations — ESLS-aligned lifecycle states
# ---------------------------------------------------------------------------


class AgentStatus(str, Enum):
    """Agent lifecycle states per ESLS Section 15."""

    REGISTERED = "Registered"
    AVAILABLE = "Available"
    ASSIGNED = "Assigned"
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    RETIRED = "Retired"


class WorkflowStatus(str, Enum):
    """Workflow lifecycle states per ESLS Section 13."""

    DRAFT = "Draft"
    READY = "Ready"
    EXECUTING = "Executing"
    SUSPENDED = "Suspended"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


class PolicyVerdict(str, Enum):
    """Governance evaluation outcomes per GCF Law 11."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"


class EventCategory(str, Enum):
    """Canonical ESLS event categories (ESLS Section 5)."""

    OBJECTIVE_CREATED = "ObjectiveCreated"
    PLAN_GENERATED = "PlanGenerated"
    WORKFLOW_STARTED = "WorkflowStarted"
    AGENT_ASSIGNED = "AgentAssigned"
    ACTION_REQUESTED = "ActionRequested"
    GOVERNANCE_EVALUATED = "GovernanceEvaluated"
    TOOL_EXECUTION_STARTED = "ToolExecutionStarted"
    TOOL_EXECUTION_COMPLETED = "ToolExecutionCompleted"
    ACTION_COMPLETED = "ActionCompleted"
    WORKFLOW_COMPLETED = "WorkflowCompleted"
    WORKFLOW_FAILED = "WorkflowFailed"


# ---------------------------------------------------------------------------
# Core Data Structures
# ---------------------------------------------------------------------------


@dataclass
class UAWOSContext:
    """
    Propagation context required on every agent invocation (ESLS Section 21).
    Injected by the Correlation Manager into every workflow step and tool call.
    """

    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    causation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    objective_id: str = ""
    workflow_id: str = ""
    agent_id: str = ""
    action_id: str = ""
    actor: str = ""
    actor_role: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "objective_id": self.objective_id,
            "workflow_id": self.workflow_id,
            "agent_id": self.agent_id,
            "action_id": self.action_id,
            "actor": self.actor,
            "actor_role": self.actor_role,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> UAWOSContext:
        ctx = cls()
        for k, v in d.items():
            if hasattr(ctx, k):
                setattr(ctx, k, v)
        return ctx

    def child(self, action_id: str = "") -> UAWOSContext:
        """Create a child context preserving correlation chain (ESLS-21).

        Correlation ID stays the same across the entire thread.
        Causation ID is set to the parent's action_id, forming the causal chain.
        A fresh action_id is generated for the child.
        """
        return UAWOSContext(
            correlation_id=self.correlation_id,
            causation_id=self.action_id,
            objective_id=self.objective_id,
            workflow_id=self.workflow_id,
            agent_id=self.agent_id,
            action_id=action_id if action_id else str(uuid.uuid4()),
            actor=self.actor,
            actor_role=self.actor_role,
            timestamp=time.time(),
        )


@dataclass
class PolicyResult:
    """Result of a governance policy evaluation (GCF Law 11)."""

    verdict: PolicyVerdict
    reason: str
    policy_ids: list[str] = field(default_factory=list)
    evaluated_at: float = field(default_factory=time.time)
    context: dict = field(default_factory=dict)


@dataclass
class AuditEntry:
    """Immutable audit artifact (GCF Section 15)."""

    entry_id: str = field(default_factory=lambda: f"AUD-{uuid.uuid4().hex[:8].upper()}")
    event_type: str = ""
    actor: str = ""
    context: dict = field(default_factory=dict)
    decision: str = ""
    provenance: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "event_type": self.event_type,
            "actor": self.actor,
            "context": self.context,
            "decision": self.decision,
            "provenance": self.provenance,
            "timestamp": self.timestamp,
        }


@dataclass
class LifecycleEvent:
    """ESLS-compliant lifecycle event envelope (ESLS Section 4)."""

    event_id: str = field(default_factory=lambda: f"EVT-{uuid.uuid4().hex[:8].upper()}")
    event_type: EventCategory = EventCategory.ACTION_REQUESTED
    event_version: str = "1.0"
    timestamp: float = field(default_factory=time.time)
    actor: str = ""
    source: str = "uawos_agent_runtime"
    correlation_id: str = ""
    causation_id: str = ""
    entity_ref: str = ""
    payload: dict = field(default_factory=dict)
    provenance: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "event_version": self.event_version,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "source": self.source,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "entity_ref": self.entity_ref,
            "payload": self.payload,
            "provenance": self.provenance,
        }


# ---------------------------------------------------------------------------
# Abstract Interface Contracts
# ---------------------------------------------------------------------------


class IPolicyEvaluator(ABC):
    """
    Interface for governance policy evaluation (GCF Law 11, OPA/OpenFGA).
    Every action execution path MUST call this before any tool or LLM invocation.
    """

    @abstractmethod
    def evaluate_policy(self, action_id: str, action_payload: dict) -> PolicyResult:
        """Synchronously evaluate governance policy for the given action."""
        ...

    @abstractmethod
    async def evaluate_policy_async(self, action_id: str, action_payload: dict) -> PolicyResult:
        """Asynchronously evaluate governance policy — non-blocking path."""
        ...


class IAuditProvider(ABC):
    """
    Interface for immutable audit artifact persistence (GCF Section 15).
    Every event MUST generate an immutable audit entry with timestamp, actor, and provenance.
    """

    @abstractmethod
    def write_audit(self, entry: AuditEntry) -> bool:
        """Persist an audit entry to the immutable audit ledger."""
        ...

    @abstractmethod
    def read_audit(self, context: UAWOSContext) -> list[AuditEntry]:
        """Retrieve all audit entries for a given correlation ID."""
        ...


class ITraceProvider(ABC):
    """
    Interface for event emission and lineage tracing (ESLS, OpenLineage).
    Every lifecycle transition MUST emit a LifecycleEvent.
    """

    @abstractmethod
    def emit_event(self, event: LifecycleEvent) -> bool:
        """Publish a lifecycle event to the event bus."""
        ...

    @abstractmethod
    def get_lineage(self, correlation_id: str) -> list[LifecycleEvent]:
        """Retrieve the full event chain for a given correlation thread."""
        ...


class IToolExecutor(ABC):
    """
    Interface for sandboxed tool execution (Wave 3 — Sandbox Runtime).
    All tool calls MUST route through this interface. Direct subprocess or
    shell calls are prohibited per the Security Policy.
    """

    @abstractmethod
    def execute_tool(
        self,
        tool_name: str,
        arguments: dict,
        context: UAWOSContext,
    ) -> dict:
        """Execute a named tool within a secure sandbox, returning its output."""
        ...

    @abstractmethod
    def list_available_tools(self) -> list[str]:
        """Return the registry of all tools available for execution."""
        ...


class IAgentRuntime(ABC):
    """
    Interface for agent registration, identity management, and task execution.
    All agent interactions go through this interface — never via direct framework imports.
    """

    @abstractmethod
    def register_agent(
        self,
        agent_id: str,
        agent_class: str,
        capabilities: list[str],
        context: UAWOSContext,
    ) -> bool:
        """Register an agent in the UAWOS Agent Registry."""
        ...

    @abstractmethod
    def execute_task(
        self,
        task_payload: dict,
        context: UAWOSContext,
    ) -> dict:
        """
        Execute a governed agent task.
        MUST call IPolicyEvaluator before any LLM or tool invocation.
        MUST emit lifecycle events via ITraceProvider.
        MUST write audit artifacts via IAuditProvider.
        """
        ...

    @abstractmethod
    def get_agent_status(self, agent_id: str) -> AgentStatus:
        """Return the current lifecycle status of a registered agent."""
        ...

    @abstractmethod
    def suspend_agent(self, agent_id: str, reason: str, context: UAWOSContext) -> bool:
        """Suspend an active agent, emitting an AgentSuspended lifecycle event."""
        ...


class IWorkflowRuntime(ABC):
    """
    Interface for deterministic, stateful workflow orchestration.
    Implementations (e.g. LangGraph adapter) must hide all framework details.
    """

    @abstractmethod
    def compile_workflow(self, workflow_definition: dict) -> str:
        """
        Compile a workflow definition into a runnable state machine.
        Returns a runtime_id string.
        """
        ...

    @abstractmethod
    def run_step(
        self,
        runtime_id: str,
        step_id: str,
        state: dict,
        context: UAWOSContext,
    ) -> dict:
        """
        Execute a single workflow step.
        MUST apply policy gate BEFORE the step runs.
        MUST emit WorkflowStarted / ActionCompleted events.
        MUST checkpoint state after each step.
        """
        ...

    @abstractmethod
    def get_workflow_state(self, runtime_id: str) -> dict:
        """Retrieve the current state of a workflow runtime."""
        ...

    @abstractmethod
    def checkpoint_state(self, runtime_id: str, state: dict) -> bool:
        """Persist the current state snapshot to the immutable audit store."""
        ...


# ---------------------------------------------------------------------------
# Default Implementations
# ---------------------------------------------------------------------------


class UAWOSPolicyEvaluator(IPolicyEvaluator):
    """
    Concrete governance policy evaluator backed by OPA and OpenFGA.
    Falls back to native Python checks if containers are offline (GCF degraded mode).
    """

    def evaluate_policy(self, action_id: str, action_payload: dict) -> PolicyResult:
        result = uawos_governance.evaluate_action_governance(action_id, action_payload)
        verdict = PolicyVerdict(result.get("verdict", "REJECTED"))
        return PolicyResult(
            verdict=verdict,
            reason=result.get("reason", ""),
            policy_ids=["POL-01", "POL-02"],
            context=action_payload,
        )

    async def evaluate_policy_async(self, action_id: str, action_payload: dict) -> PolicyResult:
        """Non-blocking async wrapper — runs governance check in thread pool."""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.evaluate_policy, action_id, action_payload)
        return result


class UAWOSAuditProvider(IAuditProvider):
    """
    In-process audit provider writing to the runtime state audit_logs list.
    Production upgrade: replace with direct Postgres INSERT via uawos_db.
    """

    def write_audit(self, entry: AuditEntry) -> bool:
        try:
            state = load_state(STATE_FILE, get_default_state)
            state["audit_logs"].append(
                {
                    "event_type": entry.event_type,
                    "details": entry.to_dict(),
                    "timestamp": entry.timestamp,
                }
            )
            save_state(STATE_FILE, state)
            return True
        except Exception:
            return False

    def read_audit(self, context: UAWOSContext) -> list[AuditEntry]:
        try:
            state = load_state(STATE_FILE, get_default_state)
        except Exception:
            return []
        logs = state.get("audit_logs", [])
        result = []
        for log in logs:
            details = log.get("details", {})
            ctx = details.get("context", {})
            if ctx.get("correlation_id") == context.correlation_id:
                result.append(
                    AuditEntry(
                        event_type=log.get("event_type", ""),
                        context=details,
                        timestamp=log.get("timestamp", 0.0),
                    )
                )
        return result


class UAWOSTraceProvider(ITraceProvider):
    """
    In-process trace provider writing lifecycle events to the runtime state log.
    Production upgrade: publish to Kafka/Redis event bus.
    """

    def emit_event(self, event: LifecycleEvent) -> bool:
        try:
            state = load_state(STATE_FILE, get_default_state)
            state["event_log"].append(event.to_dict())
            save_state(STATE_FILE, state)
            return True
        except Exception:
            return False

    def get_lineage(self, correlation_id: str) -> list[LifecycleEvent]:
        try:
            state = load_state(STATE_FILE, get_default_state)
        except Exception:
            return []
        events = state.get("event_log", [])
        result = []
        for e in events:
            if e.get("correlation_id") != correlation_id:
                continue
            try:
                evt = LifecycleEvent()
                for k, v in e.items():
                    if hasattr(evt, k):
                        if k == "event_type":
                            try:
                                setattr(evt, k, EventCategory(v))
                            except ValueError:
                                pass
                        else:
                            setattr(evt, k, v)
                result.append(evt)
            except Exception:
                pass
        return result


class UAWOSLocalToolExecutor(IToolExecutor):
    """
    Wave 0 stub tool executor — runs registered python callables.
    Wave 3 replacement: route all calls to the Docker Sandbox REST API.
    """

    _registry: dict[str, Any] = {}

    @classmethod
    def register_tool(cls, name: str, fn: Any) -> None:
        cls._registry[name] = fn  # type: ignore[assignment]

    def execute_tool(
        self,
        tool_name: str,
        arguments: dict,
        context: UAWOSContext,
    ) -> dict:
        if tool_name not in self._registry:
            return {"error": f"Tool '{tool_name}' not registered.", "verdict": "REJECTED"}

        # Governance gate — MUST pass before tool invocation (GCF Law 11)
        evaluator = UAWOSPolicyEvaluator()
        audit = UAWOSAuditProvider()
        tracer = UAWOSTraceProvider()

        action_id = context.action_id or f"TOOL-{tool_name.upper()}"
        policy_result = evaluator.evaluate_policy(
            action_id,
            {
                "actor": context.actor,
                "actor_role": context.actor_role,
                "tool_name": tool_name,
                "arguments": arguments,
            },
        )

        # Emit ToolExecutionStarted
        tracer.emit_event(
            LifecycleEvent(
                event_type=EventCategory.TOOL_EXECUTION_STARTED,
                actor=context.actor,
                correlation_id=context.correlation_id,
                causation_id=context.causation_id,
                entity_ref=tool_name,
                payload={"tool": tool_name, "arguments": arguments},
            )
        )

        if policy_result.verdict != PolicyVerdict.APPROVED:
            audit.write_audit(
                AuditEntry(
                    event_type="TOOL_BLOCKED",
                    actor=context.actor,
                    context=context.to_dict(),
                    decision=policy_result.verdict.value,
                    provenance={"reason": policy_result.reason},
                )
            )
            return {
                "error": "Governance policy blocked tool execution.",
                "verdict": policy_result.verdict.value,
                "reason": policy_result.reason,
            }

        # Execute — Wave 3 will replace this with Docker sandbox call
        try:
            output = self._registry[tool_name](**arguments)
        except Exception as exc:
            output = {"error": str(exc)}

        # Emit ToolExecutionCompleted
        tracer.emit_event(
            LifecycleEvent(
                event_type=EventCategory.TOOL_EXECUTION_COMPLETED,
                actor=context.actor,
                correlation_id=context.correlation_id,
                causation_id=context.causation_id,
                entity_ref=tool_name,
                payload={"tool": tool_name, "output": str(output)[:512]},
            )
        )

        # Write audit artifact
        audit.write_audit(
            AuditEntry(
                event_type="TOOL_EXECUTED",
                actor=context.actor,
                context=context.to_dict(),
                decision="APPROVED",
                provenance={"tool": tool_name, "output_preview": str(output)[:256]},
            )
        )

        return {"output": output, "verdict": "APPROVED"}

    def list_available_tools(self) -> list[str]:
        return list(self._registry.keys())


class UAWOSBaseAgentRuntime(IAgentRuntime):
    """
    Base governed agent runtime. Enforces policy evaluation and audit emission
    on every task execution. Framework adapters (LangGraph, SK) subclass this.
    """

    def __init__(
        self,
        policy_evaluator: IPolicyEvaluator | None = None,
        audit_provider: IAuditProvider | None = None,
        trace_provider: ITraceProvider | None = None,
        tool_executor: IToolExecutor | None = None,
    ):
        self._policy = policy_evaluator or UAWOSPolicyEvaluator()
        self._audit = audit_provider or UAWOSAuditProvider()
        self._tracer = trace_provider or UAWOSTraceProvider()
        self._tools = tool_executor or UAWOSLocalToolExecutor()

    # --- IAgentRuntime Implementation ---

    def register_agent(
        self,
        agent_id: str,
        agent_class: str,
        capabilities: list[str],
        context: UAWOSContext,
    ) -> bool:
        state = load_state(STATE_FILE, get_default_state)
        state["registered_agents"][agent_id] = {
            "agent_id": agent_id,
            "agent_class": agent_class,
            "capabilities": capabilities,
            "status": AgentStatus.REGISTERED.value,
            "registered_at": time.time(),
            "registered_by": context.actor,
        }
        save_state(STATE_FILE, state)

        self._tracer.emit_event(
            LifecycleEvent(
                event_type=EventCategory.AGENT_ASSIGNED,
                actor=context.actor,
                correlation_id=context.correlation_id,
                causation_id=context.causation_id,
                entity_ref=agent_id,
                payload={"agent_class": agent_class, "capabilities": capabilities},
            )
        )
        self._audit.write_audit(
            AuditEntry(
                event_type="AGENT_REGISTERED",
                actor=context.actor,
                context=context.to_dict(),
                decision="APPROVED",
                provenance={"agent_id": agent_id, "capabilities": capabilities},
            )
        )
        return True

    def execute_task(self, task_payload: dict, context: UAWOSContext) -> dict:
        """
        Governed task execution:
        1. Evaluate policy via OPA/OpenFGA
        2. Emit ActionRequested event
        3. Execute (overridden by framework adapters)
        4. Emit ActionCompleted / GovernanceEvaluated
        5. Write audit artifact
        """
        action_id = context.action_id or f"ACT-{uuid.uuid4().hex[:8].upper()}"
        context.action_id = action_id

        # Step 1 — Hard governance gate (Law 11)
        policy_result = self._policy.evaluate_policy(
            action_id,
            {
                "actor": context.actor,
                "actor_role": context.actor_role,
                "objective_id": context.objective_id,
                "workflow_id": context.workflow_id,
                **task_payload,
            },
        )

        # Step 2 — Emit ActionRequested event
        self._tracer.emit_event(
            LifecycleEvent(
                event_type=EventCategory.ACTION_REQUESTED,
                actor=context.actor,
                correlation_id=context.correlation_id,
                causation_id=context.causation_id,
                entity_ref=action_id,
                payload=task_payload,
            )
        )

        # Emit GovernanceEvaluated
        self._tracer.emit_event(
            LifecycleEvent(
                event_type=EventCategory.GOVERNANCE_EVALUATED,
                actor=context.actor,
                correlation_id=context.correlation_id,
                causation_id=action_id,
                entity_ref=action_id,
                payload={
                    "verdict": policy_result.verdict.value,
                    "reason": policy_result.reason,
                },
            )
        )

        # Hard stop on rejection
        if policy_result.verdict != PolicyVerdict.APPROVED:
            self._audit.write_audit(
                AuditEntry(
                    event_type="ACTION_BLOCKED",
                    actor=context.actor,
                    context=context.to_dict(),
                    decision=policy_result.verdict.value,
                    provenance={"reason": policy_result.reason},
                )
            )
            return {
                "status": "REJECTED",
                "reason": policy_result.reason,
                "verdict": policy_result.verdict.value,
            }

        # Step 3 — Execute (subclass provides framework-specific logic)
        output = self._do_execute(task_payload, context)

        # Step 4 — Emit completion event
        self._tracer.emit_event(
            LifecycleEvent(
                event_type=EventCategory.ACTION_COMPLETED,
                actor=context.actor,
                correlation_id=context.correlation_id,
                causation_id=action_id,
                entity_ref=action_id,
                payload={"output_preview": str(output)[:256]},
            )
        )

        # Step 5 — Write audit artifact
        self._audit.write_audit(
            AuditEntry(
                event_type="ACTION_COMPLETED",
                actor=context.actor,
                context=context.to_dict(),
                decision="APPROVED",
                provenance={"action_id": action_id, "output_preview": str(output)[:256]},
            )
        )

        return {"status": "APPROVED", "output": output, "action_id": action_id}

    def _do_execute(self, task_payload: dict, context: UAWOSContext) -> Any:
        """Override in framework adapters to provide execution logic."""
        return {"result": "Base runtime — no framework adapter connected."}

    def get_agent_status(self, agent_id: str) -> AgentStatus:
        try:
            state = load_state(STATE_FILE, get_default_state)
        except Exception:
            return AgentStatus.RETIRED
        agent = state.get("registered_agents", {}).get(agent_id)
        if not agent:
            return AgentStatus.RETIRED
        return AgentStatus(agent.get("status", AgentStatus.RETIRED.value))

    def suspend_agent(self, agent_id: str, reason: str, context: UAWOSContext) -> bool:
        try:
            state = load_state(STATE_FILE, get_default_state)
        except Exception:
            return False
        if agent_id not in state.get("registered_agents", {}):
            return False
        state["registered_agents"][agent_id]["status"] = AgentStatus.SUSPENDED.value
        state["registered_agents"][agent_id]["suspension_reason"] = reason
        save_state(STATE_FILE, state)

        self._tracer.emit_event(
            LifecycleEvent(
                event_type=EventCategory.WORKFLOW_FAILED,
                actor=context.actor,
                correlation_id=context.correlation_id,
                causation_id=context.causation_id,
                entity_ref=agent_id,
                payload={"reason": reason},
            )
        )
        self._audit.write_audit(
            AuditEntry(
                event_type="AGENT_SUSPENDED",
                actor=context.actor,
                context=context.to_dict(),
                decision="SUSPENDED",
                provenance={"agent_id": agent_id, "reason": reason},
            )
        )
        return True


class UAWOSBaseWorkflowRuntime(IWorkflowRuntime):
    """
    Base governed workflow runtime. Enforces policy gates, lifecycle event
    emission, and state checkpointing on every step. LangGraph adapter subclasses this.
    """

    # Hard-stop: maximum number of execution iterations before governance escalation
    MAX_ITERATIONS = 5

    def __init__(
        self,
        policy_evaluator: IPolicyEvaluator | None = None,
        audit_provider: IAuditProvider | None = None,
        trace_provider: ITraceProvider | None = None,
    ):
        self._policy = policy_evaluator or UAWOSPolicyEvaluator()
        self._audit = audit_provider or UAWOSAuditProvider()
        self._tracer = trace_provider or UAWOSTraceProvider()
        self._runtimes: dict[str, dict] = {}

    def compile_workflow(self, workflow_definition: dict) -> str:
        runtime_id = f"WF-{uuid.uuid4().hex[:8].upper()}"
        self._runtimes[runtime_id] = {
            "runtime_id": runtime_id,
            "definition": workflow_definition,
            "status": WorkflowStatus.READY.value,
            "iteration": 0,
            "checkpoints": [],
            "created_at": time.time(),
        }
        return runtime_id

    def run_step(
        self,
        runtime_id: str,
        step_id: str,
        state: dict,
        context: UAWOSContext,
    ) -> dict:
        if runtime_id not in self._runtimes:
            return {"error": f"Runtime '{runtime_id}' not found.", "status": "FAILED"}

        runtime = self._runtimes[runtime_id]

        # Iteration guard — RSK-RM-03
        runtime["iteration"] += 1
        if runtime["iteration"] > self.MAX_ITERATIONS:
            self._audit.write_audit(
                AuditEntry(
                    event_type="WORKFLOW_ITERATION_LIMIT",
                    actor=context.actor,
                    context=context.to_dict(),
                    decision="BLOCKED",
                    provenance={
                        "runtime_id": runtime_id,
                        "iterations": runtime["iteration"],
                        "limit": self.MAX_ITERATIONS,
                    },
                )
            )
            self._tracer.emit_event(
                LifecycleEvent(
                    event_type=EventCategory.WORKFLOW_FAILED,
                    actor=context.actor,
                    correlation_id=context.correlation_id,
                    causation_id=context.causation_id,
                    entity_ref=runtime_id,
                    payload={"reason": "MAX_ITERATIONS_EXCEEDED"},
                )
            )
            runtime["status"] = WorkflowStatus.FAILED.value
            return {"status": "FAILED", "reason": "Max iteration limit exceeded. Governance escalation triggered."}

        # Policy gate before step execution (Law 11)
        policy_result = self._policy.evaluate_policy(
            f"{runtime_id}:{step_id}",
            {"actor": context.actor, "actor_role": context.actor_role, "step_id": step_id},
        )
        if policy_result.verdict != PolicyVerdict.APPROVED:
            return {"status": "REJECTED", "reason": policy_result.reason}

        # Emit WorkflowStarted
        runtime["status"] = WorkflowStatus.EXECUTING.value
        self._tracer.emit_event(
            LifecycleEvent(
                event_type=EventCategory.WORKFLOW_STARTED,
                actor=context.actor,
                correlation_id=context.correlation_id,
                causation_id=context.causation_id,
                entity_ref=runtime_id,
                payload={"step_id": step_id, "iteration": runtime["iteration"]},
            )
        )

        # Execute step (framework adapter overrides this)
        result = self._do_run_step(runtime_id, step_id, state, context)

        # Checkpoint after each step
        self.checkpoint_state(runtime_id, {**state, **result})

        # Emit ActionCompleted
        self._tracer.emit_event(
            LifecycleEvent(
                event_type=EventCategory.ACTION_COMPLETED,
                actor=context.actor,
                correlation_id=context.correlation_id,
                causation_id=context.causation_id,
                entity_ref=f"{runtime_id}:{step_id}",
                payload={"result_preview": str(result)[:256]},
            )
        )

        return {"status": "OK", "result": result, "iteration": runtime["iteration"]}

    def _do_run_step(
        self,
        runtime_id: str,
        step_id: str,
        state: dict,
        context: UAWOSContext,
    ) -> dict:
        """Override in framework adapters (e.g. LangGraphWorkflowAdapter)."""
        return {"output": f"Base step {step_id} executed.", "state_snapshot": state}

    def get_workflow_state(self, runtime_id: str) -> dict:
        return self._runtimes.get(runtime_id, {})

    def checkpoint_state(self, runtime_id: str, state: dict) -> bool:
        if runtime_id not in self._runtimes:
            return False
        checkpoint = {
            "runtime_id": runtime_id,
            "state": state,
            "timestamp": time.time(),
        }
        self._runtimes[runtime_id]["checkpoints"].append(checkpoint)
        # Production: Write directly to uawos_db Postgres via UAWOSSqlCheckpointer
        return True


# ---------------------------------------------------------------------------
# Agent Registry — in-process (production: backed by uawos_db)
# ---------------------------------------------------------------------------


class UAWOSAgentRegistry:
    """Central registry for all UAWOS agents (WAAS Section 25)."""

    @staticmethod
    def register(
        agent_id: str,
        agent_class: str,
        capabilities: list[str],
        context: UAWOSContext,
    ) -> bool:
        runtime = UAWOSBaseAgentRuntime()
        return runtime.register_agent(agent_id, agent_class, capabilities, context)

    @staticmethod
    def get_status(agent_id: str) -> AgentStatus:
        try:
            state = load_state(STATE_FILE, get_default_state)
        except Exception:
            return AgentStatus.RETIRED
        agent = state.get("registered_agents", {}).get(agent_id)
        if not agent:
            return AgentStatus.RETIRED
        return AgentStatus(agent.get("status", AgentStatus.RETIRED.value))

    @staticmethod
    def list_agents() -> list[dict]:
        try:
            state = load_state(STATE_FILE, get_default_state)
        except Exception:
            return []
        return list(state.get("registered_agents", {}).values())


# ---------------------------------------------------------------------------
# Factory — create runtime instances
# ---------------------------------------------------------------------------


def create_agent_runtime(
    policy_evaluator: IPolicyEvaluator | None = None,
    audit_provider: IAuditProvider | None = None,
    trace_provider: ITraceProvider | None = None,
    tool_executor: IToolExecutor | None = None,
) -> UAWOSBaseAgentRuntime:
    """Factory for constructing a governed agent runtime."""
    return UAWOSBaseAgentRuntime(
        policy_evaluator=policy_evaluator,
        audit_provider=audit_provider,
        trace_provider=trace_provider,
        tool_executor=tool_executor,
    )


def create_workflow_runtime(
    policy_evaluator: IPolicyEvaluator | None = None,
    audit_provider: IAuditProvider | None = None,
    trace_provider: ITraceProvider | None = None,
) -> UAWOSBaseWorkflowRuntime:
    """Factory for constructing a governed workflow runtime."""
    return UAWOSBaseWorkflowRuntime(
        policy_evaluator=policy_evaluator,
        audit_provider=audit_provider,
        trace_provider=trace_provider,
    )


# ---------------------------------------------------------------------------
# Self-Tests (FR-091 to FR-100 — Agent Workforce verification)
# ---------------------------------------------------------------------------


def run_self_tests():
    print("Running Agent Runtime Interface self tests...")

    state_data = get_default_state()
    # Seed governance policies for tests
    state_data["policies"] = {
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

    uawos_db.db_save_state("uawos_governance_state", state_data)
    uawos_db.db_save_state("uawos_agent_runtime_state", state_data)

    ctx = UAWOSContext(
        objective_id="OBJ-001",
        workflow_id="WF-TEST-001",
        actor="Lead Engineer",
        actor_role="Lead Engineer",
    )

    # FR-AR-01: Context propagation
    child = ctx.child("ACT-001")
    assert child.correlation_id == ctx.correlation_id, "Correlation ID must propagate to child."
    # causation_id of child = parent's action_id (which was a fresh UUID set on ctx init)
    assert child.causation_id == ctx.action_id, "Child causation_id must equal parent action_id."
    assert child.action_id == "ACT-001", "Child action_id must be the explicit value."
    print("  [PASS] FR-AR-01: UAWOSContext child propagation verified.")

    # FR-AR-02: Policy evaluator (approved path)
    evaluator = UAWOSPolicyEvaluator()
    result = evaluator.evaluate_policy("ACT-VALID", {"actor": "Lead Engineer", "actor_role": "Lead Engineer"})
    assert result.verdict == PolicyVerdict.APPROVED, f"Expected APPROVED, got {result.verdict}"
    print("  [PASS] FR-AR-02: UAWOSPolicyEvaluator APPROVED path verified.")

    # FR-AR-03: Policy evaluator (rejected — GPLv3)
    result_rej = evaluator.evaluate_policy("ACT-GPL", {"uses_marker_library": True})
    assert result_rej.verdict == PolicyVerdict.REJECTED, "GPLv3 import must be blocked."
    print("  [PASS] FR-AR-03: UAWOSPolicyEvaluator REJECTED (GPLv3) path verified.")

    # FR-AR-04: Async policy evaluator
    async def _async_test():
        result_async = await evaluator.evaluate_policy_async("ACT-ASYNC", {"actor_role": "CEO", "category": "budget"})
        assert result_async.verdict == PolicyVerdict.APPROVED

    asyncio.run(_async_test())
    print("  [PASS] FR-AR-04: Async policy evaluator verified.")

    # FR-AR-05: Audit provider write/read
    audit = UAWOSAuditProvider()
    entry = AuditEntry(
        event_type="TEST_AUDIT",
        actor="Lead Engineer",
        context=ctx.to_dict(),
        decision="APPROVED",
        provenance={"test": True},
    )
    assert audit.write_audit(entry), "Audit write must succeed."
    print("  [PASS] FR-AR-05: UAWOSAuditProvider write verified.")

    # FR-AR-06: Trace provider emit/read
    tracer = UAWOSTraceProvider()
    evt = LifecycleEvent(
        event_type=EventCategory.WORKFLOW_STARTED,
        actor="Lead Engineer",
        correlation_id=ctx.correlation_id,
        causation_id=ctx.causation_id,
        entity_ref="WF-TEST-001",
    )
    assert tracer.emit_event(evt), "Event emit must succeed."
    lineage = tracer.get_lineage(ctx.correlation_id)
    assert len(lineage) >= 1, "Lineage must contain emitted event."
    print("  [PASS] FR-AR-06: UAWOSTraceProvider emit/lineage verified.")

    # FR-AR-07: Tool executor governance gate
    executor = UAWOSLocalToolExecutor()
    UAWOSLocalToolExecutor.register_tool("echo", lambda msg="": {"echo": msg})
    tool_ctx = UAWOSContext(actor="Lead Engineer", actor_role="Lead Engineer")
    tool_result = executor.execute_tool("echo", {"msg": "hello"}, tool_ctx)
    assert tool_result.get("verdict") == "APPROVED", "Tool execution must be approved."
    assert tool_result["output"]["echo"] == "hello"
    print("  [PASS] FR-AR-07: UAWOSLocalToolExecutor (APPROVED) verified.")

    # FR-AR-08: Tool executor rejects unlisted tools
    bad = executor.execute_tool("rm_rf_slash", {}, tool_ctx)
    assert "error" in bad
    print("  [PASS] FR-AR-08: UAWOSLocalToolExecutor (unknown tool rejected) verified.")

    # FR-AR-09: Agent registration
    runtime = create_agent_runtime()
    ok = runtime.register_agent("AGENT-PLANNER-01", "PlannerAgent", ["objective_decomposition", "plan_generation"], ctx)
    assert ok, "Agent registration must succeed."
    status = runtime.get_agent_status("AGENT-PLANNER-01")
    assert status == AgentStatus.REGISTERED
    print("  [PASS] FR-AR-09: IAgentRuntime.register_agent verified.")

    # FR-AR-10: Governed task execution (approved)
    task_result = runtime.execute_task(
        {"task": "analyze_objective", "actor_role": "Lead Engineer", "actor": "Lead Engineer"},
        ctx.child("ACT-TASK-001"),
    )
    assert task_result["status"] == "APPROVED"
    print("  [PASS] FR-AR-10: IAgentRuntime.execute_task (APPROVED) verified.")

    # FR-AR-11: Governed task execution (blocked — GPLv3)
    blocked_result = runtime.execute_task(
        {"uses_marker_library": True},
        ctx.child("ACT-TASK-BAD"),
    )
    assert blocked_result["status"] == "REJECTED"
    print("  [PASS] FR-AR-11: IAgentRuntime.execute_task (REJECTED — GPLv3) verified.")

    # FR-AR-12: Agent suspension
    suspended = runtime.suspend_agent("AGENT-PLANNER-01", "Low trust score.", ctx)
    assert suspended
    status_after = runtime.get_agent_status("AGENT-PLANNER-01")
    assert status_after == AgentStatus.SUSPENDED
    print("  [PASS] FR-AR-12: IAgentRuntime.suspend_agent verified.")

    # FR-AR-13: Workflow compile + step
    wf_runtime = create_workflow_runtime()
    rid = wf_runtime.compile_workflow({"nodes": ["prep", "exec", "review"]})
    assert rid.startswith("WF-")
    step_result = wf_runtime.run_step(rid, "prep", {"input": "test"}, ctx.child())
    assert step_result["status"] == "OK"
    print("  [PASS] FR-AR-13: IWorkflowRuntime compile + run_step verified.")

    # FR-AR-14: Checkpoint persistence
    assert wf_runtime.get_workflow_state(rid)["checkpoints"]
    print("  [PASS] FR-AR-14: IWorkflowRuntime checkpoint_state verified.")

    # FR-AR-15: Iteration limit guard
    for _ in range(6):
        wf_runtime.run_step(rid, "exec", {}, ctx.child())
    limit_result = wf_runtime.run_step(rid, "exec", {}, ctx.child())
    assert limit_result["status"] == "FAILED"
    print("  [PASS] FR-AR-15: IWorkflowRuntime MAX_ITERATIONS guard verified.")

    print("\nAll Agent Runtime Interface self tests completed successfully!")


if __name__ == "__main__":
    run_self_tests()
