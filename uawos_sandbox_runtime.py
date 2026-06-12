"""
uawos_sandbox_runtime.py
========================
UAWOS Sandbox Runtime — Wave 3 Deliverable

Provides:
  1. UAWOSSandboxToolExecutor — Governed IToolExecutor routing tool calls to
     isolated Docker containers via REST API (marker-service pattern).
  2. UAWOSSecretsManager     — Redacts and vaults credentials; prevents any
     secret from reaching LLM context or audit logs.
  3. ToolRegistry            — Central manifest of all registered tools,
     their sandbox endpoints, capability requirements, and license classifications.
  4. SandboxService          — Flask REST application template for packaging
     any callable as an isolated sandbox container.

All tool invocations are GOVERNANCE-GATED: policy evaluation, event emission,
and audit persistence happen BEFORE the sandbox receives the request.

No subprocess, shell, eval, or exec calls are permitted anywhere in this module.
All execution is via HTTP POST to container REST APIs.

Standards: GCF v1.0 (Law 11, Section 15), ESLS, Security Policy
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

import uawos_db
from uawos_agent_runtime import (
    AuditEntry,
    EventCategory,
    IAuditProvider,
    IPolicyEvaluator,
    IToolExecutor,
    ITraceProvider,
    LifecycleEvent,
    PolicyVerdict,
    UAWOSAuditProvider,
    UAWOSContext,
    UAWOSPolicyEvaluator,
    UAWOSTraceProvider,
)
from uawos_state_utils import load_state, save_state

# ---------------------------------------------------------------------------
# State File — required by load_state/save_state auto-resolution
# ---------------------------------------------------------------------------
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_sandbox_runtime_state.json")


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
        "tool_registry": {},
        "secrets_vault": {},
        "sandbox_executions": [],
    }


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class LicenseClass(str, Enum):
    """License classification per GCF Security Policy."""

    PERMISSIVE = "Permissive"  # MIT, Apache-2.0, BSD
    COPYLEFT = "Copyleft"  # GPLv3, AGPL — must run in isolated container
    PROPRIETARY = "Proprietary"  # Vendor SDK — sandbox required
    INTERNAL = "Internal"  # UAWOS-native — can run in-process


class SandboxMode(str, Enum):
    """How a tool is executed."""

    IN_PROCESS = "InProcess"  # Direct Python callable (Internal license only)
    CONTAINER = "Container"  # Docker REST API (marker-service pattern)
    REMOTE_API = "RemoteAPI"  # External SaaS endpoint


class ExecutionVerdict(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SANDBOXED = "SANDBOXED"
    ERROR = "ERROR"


# ---------------------------------------------------------------------------
# Tool Descriptor
# ---------------------------------------------------------------------------


@dataclass
class ToolDescriptor:
    """
    Canonical tool registration entry.
    Every tool callable within UAWOS must have a descriptor in the ToolRegistry.
    """

    tool_id: str = ""
    tool_name: str = ""
    description: str = ""
    version: str = "1.0"
    license_class: LicenseClass = LicenseClass.INTERNAL
    sandbox_mode: SandboxMode = SandboxMode.IN_PROCESS
    endpoint_url: str = ""  # For Container/RemoteAPI modes
    capabilities: list = field(default_factory=list)
    required_secrets: list = field(default_factory=list)
    max_timeout_sec: int = 30
    owner: str = ""
    registered_at: float = field(default_factory=time.time)
    status: str = "active"

    def to_dict(self) -> dict:
        return {
            "tool_id": self.tool_id,
            "tool_name": self.tool_name,
            "description": self.description,
            "version": self.version,
            "license_class": self.license_class.value,
            "sandbox_mode": self.sandbox_mode.value,
            "endpoint_url": self.endpoint_url,
            "capabilities": self.capabilities,
            "required_secrets": self.required_secrets,
            "max_timeout_sec": self.max_timeout_sec,
            "owner": self.owner,
            "registered_at": self.registered_at,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, d: dict) -> ToolDescriptor:
        return cls(
            tool_id=d.get("tool_id", ""),
            tool_name=d.get("tool_name", ""),
            description=d.get("description", ""),
            version=d.get("version", "1.0"),
            license_class=LicenseClass(d.get("license_class", "Internal")),
            sandbox_mode=SandboxMode(d.get("sandbox_mode", "InProcess")),
            endpoint_url=d.get("endpoint_url", ""),
            capabilities=d.get("capabilities", []),
            required_secrets=d.get("required_secrets", []),
            max_timeout_sec=d.get("max_timeout_sec", 30),
            owner=d.get("owner", ""),
            registered_at=d.get("registered_at", 0.0),
            status=d.get("status", "active"),
        )


# ---------------------------------------------------------------------------
# Secrets Manager
# ---------------------------------------------------------------------------

# Pattern to detect common secret-like strings before they leak into logs
_SECRET_PATTERNS = [
    re.compile(r"(sk-[a-zA-Z0-9]{20,})"),  # OpenAI API key
    re.compile(r"(ghp_[a-zA-Z0-9]{36,})"),  # GitHub PAT
    re.compile(r"(AKIA[0-9A-Z]{16})"),  # AWS Access Key
    re.compile(r"(xoxb-[a-zA-Z0-9\-]+)"),  # Slack Bot Token
    re.compile(r"(password\s*[:=]\s*\S+)", re.I),  # password=...
    re.compile(r"(api[_-]?key\s*[:=]\s*\S+)", re.I),  # api_key=...
    re.compile(r"(bearer\s+[a-zA-Z0-9._\-]+)", re.I),  # Bearer tokens
]


class UAWOSSecretsManager:
    """
    Secrets Manager for the UAWOS sandbox runtime.

    Responsibilities:
      1. Store secrets in an encrypted vault (Wave 3: in-memory + state; production: HashiCorp Vault)
      2. Inject secrets into sandbox container requests WITHOUT exposing them to LLM context
      3. Redact any detected secrets from audit logs, event payloads, and tool outputs
      4. Validate that required secrets exist before tool execution

    CRITICAL: Secrets MUST NEVER appear in:
      - Audit entries
      - Event payloads
      - LLM prompt context
      - State checkpoints
    """

    @staticmethod
    def store_secret(name: str, value: str, owner: str = "") -> bool:
        """Store a secret. The value is hashed for reference (never stored raw in state)."""
        try:
            state = load_state(STATE_FILE, get_default_state)
            state["secrets_vault"][name] = {
                "name": name,
                "value_hash": hashlib.sha256(value.encode()).hexdigest()[:16],
                "owner": owner,
                "stored_at": time.time(),
                # Wave 3: value is held in _runtime_secrets dict (in-memory only)
                # Production: value goes to HashiCorp Vault, never touches disk
            }
            save_state(STATE_FILE, state)
            UAWOSSecretsManager._runtime_secrets[name] = value
            return True
        except Exception:
            return False

    # In-memory secret cache (NEVER serialized to state file)
    _runtime_secrets: dict[str, str] = {}

    @staticmethod
    def get_secret(name: str) -> str | None:
        """Retrieve a secret value. Returns None if not found."""
        return UAWOSSecretsManager._runtime_secrets.get(name)

    @staticmethod
    def has_secret(name: str) -> bool:
        """Check if a secret exists."""
        return name in UAWOSSecretsManager._runtime_secrets

    @staticmethod
    def validate_requirements(required: list[str]) -> tuple[bool, list[str]]:
        """Check that all required secrets are available. Returns (ok, missing_names)."""
        missing = [s for s in required if not UAWOSSecretsManager.has_secret(s)]
        return (len(missing) == 0, missing)

    @staticmethod
    def redact(text: str) -> str:
        """
        Scrub any detected secret patterns from a string.
        Applied to all audit entries, event payloads, and tool outputs.
        """
        redacted = text
        for pattern in _SECRET_PATTERNS:
            redacted = pattern.sub("[REDACTED]", redacted)
        # Also redact any stored runtime secrets
        for name, value in UAWOSSecretsManager._runtime_secrets.items():
            if value and value in redacted:
                redacted = redacted.replace(value, f"[SECRET:{name}]")
        return redacted

    @staticmethod
    def redact_dict(d: dict) -> dict:
        """Deep-redact all string values in a dict."""
        result = {}
        for k, v in d.items():
            if isinstance(v, str):
                result[k] = UAWOSSecretsManager.redact(v)
            elif isinstance(v, dict):
                result[k] = UAWOSSecretsManager.redact_dict(v)
            elif isinstance(v, list):
                result[k] = [
                    UAWOSSecretsManager.redact(item)
                    if isinstance(item, str)
                    else UAWOSSecretsManager.redact_dict(item)
                    if isinstance(item, dict)
                    else item
                    for item in v
                ]
            else:
                result[k] = v
        return result

    @staticmethod
    def inject_into_request(
        tool: ToolDescriptor,
        request_payload: dict,
    ) -> dict:
        """
        Inject required secrets into the sandbox HTTP request body.
        The injected dict goes ONLY to the sandbox container — never to audit/events.
        """
        injected = dict(request_payload)
        for secret_name in tool.required_secrets:
            value = UAWOSSecretsManager.get_secret(secret_name)
            if value:
                injected[f"__secret_{secret_name}__"] = value
        return injected


# ---------------------------------------------------------------------------
# Tool Registry
# ---------------------------------------------------------------------------


class ToolRegistry:
    """
    Central registry of all tools available within the UAWOS runtime.
    Each tool has a ToolDescriptor that specifies its sandbox mode,
    license classification, endpoint URL, and secret requirements.
    """

    @staticmethod
    def register(tool: ToolDescriptor) -> bool:
        """Register a tool descriptor."""
        try:
            state = load_state(STATE_FILE, get_default_state)
            state["tool_registry"][tool.tool_id] = tool.to_dict()
            save_state(STATE_FILE, state)
            return True
        except Exception:
            return False

    @staticmethod
    def get(tool_id: str) -> ToolDescriptor | None:
        """Retrieve a tool descriptor by ID."""
        try:
            state = load_state(STATE_FILE, get_default_state)
            raw = state.get("tool_registry", {}).get(tool_id)
            return ToolDescriptor.from_dict(raw) if raw else None
        except Exception:
            return None

    @staticmethod
    def find_by_name(tool_name: str) -> ToolDescriptor | None:
        """Find a tool by name (first match)."""
        try:
            state = load_state(STATE_FILE, get_default_state)
            for raw in state.get("tool_registry", {}).values():
                if raw.get("tool_name") == tool_name:
                    return ToolDescriptor.from_dict(raw)
        except Exception:
            pass
        return None

    @staticmethod
    def list_tools(license_filter: LicenseClass | None = None) -> list[ToolDescriptor]:
        """List all registered tools, optionally filtered by license class."""
        try:
            state = load_state(STATE_FILE, get_default_state)
        except Exception:
            return []
        tools = [ToolDescriptor.from_dict(r) for r in state.get("tool_registry", {}).values()]
        if license_filter:
            tools = [t for t in tools if t.license_class == license_filter]
        return tools

    @staticmethod
    def deactivate(tool_id: str, reason: str = "") -> bool:
        """Deactivate a tool (security incident, license revocation, etc.)."""
        try:
            state = load_state(STATE_FILE, get_default_state)
            if tool_id in state.get("tool_registry", {}):
                state["tool_registry"][tool_id]["status"] = "deactivated"
                save_state(STATE_FILE, state)
                return True
        except Exception:
            pass
        return False


# ---------------------------------------------------------------------------
# Sandbox Execution Record
# ---------------------------------------------------------------------------


@dataclass
class SandboxExecution:
    """Immutable record of a sandbox tool execution."""

    execution_id: str = field(default_factory=lambda: f"SBX-{uuid.uuid4().hex[:8].upper()}")
    tool_id: str = ""
    tool_name: str = ""
    sandbox_mode: str = ""
    endpoint_url: str = ""
    correlation_id: str = ""
    causation_id: str = ""
    actor: str = ""
    verdict: str = ""  # APPROVED, REJECTED, ERROR
    request_hash: str = ""  # SHA-256 of redacted request
    response_hash: str = ""  # SHA-256 of redacted response
    duration_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "execution_id": self.execution_id,
            "tool_id": self.tool_id,
            "tool_name": self.tool_name,
            "sandbox_mode": self.sandbox_mode,
            "endpoint_url": self.endpoint_url,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "actor": self.actor,
            "verdict": self.verdict,
            "request_hash": self.request_hash,
            "response_hash": self.response_hash,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# Sandbox Tool Executor — the production IToolExecutor
# ---------------------------------------------------------------------------


class UAWOSSandboxToolExecutor(IToolExecutor):
    """
    Production IToolExecutor implementation (replaces UAWOSLocalToolExecutor).

    Execution flow:
      1. Resolve tool descriptor from ToolRegistry
      2. Validate license class → enforce container isolation for Copyleft/Proprietary
      3. Validate required secrets via SecretsManager
      4. Evaluate governance policy via IPolicyEvaluator
      5. Emit ToolExecutionStarted lifecycle event
      6. Route to appropriate execution mode:
         - InProcess:  call registered Python function
         - Container:  HTTP POST to sandbox REST API
         - RemoteAPI:  HTTP POST to external endpoint
      7. Redact secrets from response
      8. Emit ToolExecutionCompleted event + write audit entry
      9. Return redacted result

    All subprocess/shell/exec/eval calls are PROHIBITED.
    """

    # In-process callable registry (InProcess mode only)
    _callable_registry: dict[str, Callable] = {}

    def __init__(
        self,
        policy_evaluator: IPolicyEvaluator | None = None,
        audit_provider: IAuditProvider | None = None,
        trace_provider: ITraceProvider | None = None,
    ):
        self._policy = policy_evaluator or UAWOSPolicyEvaluator()
        self._audit = audit_provider or UAWOSAuditProvider()
        self._tracer = trace_provider or UAWOSTraceProvider()

    @classmethod
    def register_callable(cls, tool_id: str, fn: Callable) -> None:
        """Register a Python callable for InProcess execution."""
        cls._callable_registry[tool_id] = fn

    def execute_tool(
        self,
        tool_name: str,
        arguments: dict,
        context: UAWOSContext,
    ) -> dict:
        """Full governed tool execution pipeline."""

        # Step 1 — Resolve tool descriptor
        tool = ToolRegistry.find_by_name(tool_name)
        if not tool:
            return {
                "error": f"Tool '{tool_name}' not found in ToolRegistry.",
                "verdict": ExecutionVerdict.REJECTED.value,
            }

        if tool.status != "active":
            return {
                "error": f"Tool '{tool_name}' is deactivated.",
                "verdict": ExecutionVerdict.REJECTED.value,
            }

        # Step 2 — Enforce license isolation
        if tool.license_class in (LicenseClass.COPYLEFT, LicenseClass.PROPRIETARY):
            if tool.sandbox_mode == SandboxMode.IN_PROCESS:
                return {
                    "error": f"Tool '{tool_name}' has {tool.license_class.value} license but is configured for InProcess mode. "
                    f"Copyleft/Proprietary tools MUST run in Container or RemoteAPI mode.",
                    "verdict": ExecutionVerdict.REJECTED.value,
                }

        # Step 3 — Validate required secrets
        secrets_ok, missing = UAWOSSecretsManager.validate_requirements(tool.required_secrets)
        if not secrets_ok:
            return {
                "error": f"Missing required secrets: {missing}",
                "verdict": ExecutionVerdict.REJECTED.value,
            }

        # Step 4 — Governance gate (GCF Law 11)
        action_id = context.action_id or f"TOOL-{tool.tool_id}"
        policy_result = self._policy.evaluate_policy(
            action_id,
            {
                "actor": context.actor,
                "actor_role": context.actor_role,
                "tool_name": tool_name,
                "tool_id": tool.tool_id,
                "license_class": tool.license_class.value,
                "sandbox_mode": tool.sandbox_mode.value,
                "arguments": UAWOSSecretsManager.redact_dict(arguments),
            },
        )

        # Step 5 — Emit ToolExecutionStarted
        self._tracer.emit_event(
            LifecycleEvent(
                event_type=EventCategory.TOOL_EXECUTION_STARTED,
                actor=context.actor,
                correlation_id=context.correlation_id,
                causation_id=context.causation_id,
                entity_ref=tool.tool_id,
                payload={
                    "tool": tool_name,
                    "arguments": UAWOSSecretsManager.redact_dict(arguments),
                },
            )
        )

        if policy_result.verdict != PolicyVerdict.APPROVED:
            self._audit.write_audit(
                AuditEntry(
                    event_type="TOOL_BLOCKED",
                    actor=context.actor,
                    context=context.to_dict(),
                    decision=policy_result.verdict.value,
                    provenance={"reason": policy_result.reason, "tool_id": tool.tool_id},
                )
            )
            exec_record = SandboxExecution(
                tool_id=tool.tool_id,
                tool_name=tool_name,
                sandbox_mode=tool.sandbox_mode.value,
                correlation_id=context.correlation_id,
                causation_id=context.causation_id,
                actor=context.actor,
                verdict=ExecutionVerdict.REJECTED.value,
                error=policy_result.reason,
            )
            self._record_execution(exec_record)
            return {
                "error": "Governance policy blocked tool execution.",
                "verdict": ExecutionVerdict.REJECTED.value,
                "reason": policy_result.reason,
            }

        # Step 6 — Route to execution mode
        start_time = time.time()
        try:
            if tool.sandbox_mode == SandboxMode.IN_PROCESS:
                result = self._execute_in_process(tool, arguments, context)
            elif tool.sandbox_mode == SandboxMode.CONTAINER:
                result = self._execute_container(tool, arguments, context)
            elif tool.sandbox_mode == SandboxMode.REMOTE_API:
                result = self._execute_remote(tool, arguments, context)
            else:
                result = {"error": f"Unknown sandbox mode: {tool.sandbox_mode}"}
        except Exception as exc:
            result = {"error": str(exc)}
        elapsed_ms = (time.time() - start_time) * 1000

        # Step 7 — Redact secrets from result
        if isinstance(result, dict):
            result = UAWOSSecretsManager.redact_dict(result)

        # Step 8 — Emit ToolExecutionCompleted + audit
        self._tracer.emit_event(
            LifecycleEvent(
                event_type=EventCategory.TOOL_EXECUTION_COMPLETED,
                actor=context.actor,
                correlation_id=context.correlation_id,
                causation_id=context.causation_id,
                entity_ref=tool.tool_id,
                payload={
                    "tool": tool_name,
                    "output": str(result)[:512],
                    "elapsed_ms": elapsed_ms,
                },
            )
        )

        self._audit.write_audit(
            AuditEntry(
                event_type="TOOL_EXECUTED",
                actor=context.actor,
                context=context.to_dict(),
                decision="APPROVED",
                provenance={
                    "tool_id": tool.tool_id,
                    "sandbox_mode": tool.sandbox_mode.value,
                    "elapsed_ms": elapsed_ms,
                    "output_preview": UAWOSSecretsManager.redact(str(result)[:256]),
                },
            )
        )

        # Record execution
        exec_record = SandboxExecution(
            tool_id=tool.tool_id,
            tool_name=tool_name,
            sandbox_mode=tool.sandbox_mode.value,
            endpoint_url=tool.endpoint_url,
            correlation_id=context.correlation_id,
            causation_id=context.causation_id,
            actor=context.actor,
            verdict=ExecutionVerdict.APPROVED.value,
            request_hash=hashlib.sha256(
                json.dumps(UAWOSSecretsManager.redact_dict(arguments), sort_keys=True).encode()
            ).hexdigest()[:16],
            response_hash=hashlib.sha256(str(result).encode()).hexdigest()[:16],
            duration_ms=elapsed_ms,
        )
        self._record_execution(exec_record)

        return {"output": result, "verdict": ExecutionVerdict.APPROVED.value}

    def list_available_tools(self) -> list[str]:
        """Return names of all active registered tools."""
        return [t.tool_name for t in ToolRegistry.list_tools() if t.status == "active"]

    # --- Private execution methods ---

    def _execute_in_process(self, tool: ToolDescriptor, arguments: dict, context: UAWOSContext) -> dict:
        """Execute a registered Python callable (Internal license only)."""
        fn = self._callable_registry.get(tool.tool_id)
        if not fn:
            return {"error": f"No callable registered for tool '{tool.tool_id}'."}
        return fn(**arguments)

    def _execute_container(self, tool: ToolDescriptor, arguments: dict, context: UAWOSContext) -> dict:
        """
        Execute via Docker container REST API (marker-service pattern).
        Production: HTTP POST to tool.endpoint_url
        Wave 3: Simulation mode — returns a structured sandbox response.
        """
        # Inject secrets into the request payload (secrets go ONLY to container, not audit)
        injected_payload = UAWOSSecretsManager.inject_into_request(tool, arguments)

        # Production implementation:
        # import httpx
        # response = httpx.post(
        #     tool.endpoint_url,
        #     json=injected_payload,
        #     timeout=tool.max_timeout_sec,
        #     headers={
        #         "X-UAWOS-Correlation-Id": context.correlation_id,
        #         "X-UAWOS-Causation-Id":   context.causation_id,
        #         "X-UAWOS-Actor":          context.actor,
        #     },
        # )
        # return response.json()

        # Wave 3 simulation
        return {
            "sandbox_mode": "container",
            "endpoint": tool.endpoint_url,
            "tool_id": tool.tool_id,
            "simulated": True,
            "result": f"Container execution simulated for '{tool.tool_name}'.",
            "arguments_hash": hashlib.sha256(json.dumps(arguments, sort_keys=True).encode()).hexdigest()[:16],
        }

    def _execute_remote(self, tool: ToolDescriptor, arguments: dict, context: UAWOSContext) -> dict:
        """
        Execute via external SaaS API endpoint.
        Same pattern as container, but targets an external URL.
        """
        # Production: HTTP POST to tool.endpoint_url with injected secrets
        return {
            "sandbox_mode": "remote_api",
            "endpoint": tool.endpoint_url,
            "tool_id": tool.tool_id,
            "simulated": True,
            "result": f"Remote API execution simulated for '{tool.tool_name}'.",
        }

    def _record_execution(self, record: SandboxExecution) -> None:
        """Persist a sandbox execution record to the runtime state."""
        try:
            state = load_state(STATE_FILE, get_default_state)
            if "sandbox_executions" not in state:
                state["sandbox_executions"] = []
            state["sandbox_executions"].append(record.to_dict())
            save_state(STATE_FILE, state)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Sandbox Flask Service Template
# ---------------------------------------------------------------------------


def create_sandbox_service_template(tool_name: str) -> str:
    """
    Generate a Flask REST API template for packaging any tool as an
    isolated Docker sandbox container (following the marker-service pattern).

    Returns the Python source code as a string.
    """
    return f'''"""
{tool_name}_sandbox_service.py
Auto-generated UAWOS Sandbox Service Template
Pattern: marker-service REST API isolation
"""
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({{"status": "healthy", "service": "{tool_name} Sandbox API"}}), 200

@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json(force=True)

    # Extract arguments (secrets are injected by UAWOSSecretsManager)
    arguments = {{k: v for k, v in data.items() if not k.startswith("__secret_")}}
    secrets   = {{k: v for k, v in data.items() if k.startswith("__secret_")}}

    # Validate UAWOS correlation headers
    correlation_id = request.headers.get("X-UAWOS-Correlation-Id", "unknown")
    actor          = request.headers.get("X-UAWOS-Actor", "unknown")

    try:
        # === IMPLEMENT TOOL LOGIC HERE ===
        result = {{"tool": "{tool_name}", "status": "executed", "input": arguments}}
        # ================================

        return jsonify({{"success": True, "result": result, "correlation_id": correlation_id}}), 200
    except Exception as e:
        return jsonify({{"success": False, "error": str(e)}}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
'''


def generate_dockerfile_template(tool_name: str) -> str:
    """Generate a Dockerfile template for the sandbox service."""
    return f"""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY {tool_name}_sandbox_service.py .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "{tool_name}_sandbox_service:app"]
"""


# ---------------------------------------------------------------------------
# Self-Tests
# ---------------------------------------------------------------------------


def run_self_tests():
    print("Running Sandbox Runtime self tests...")

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
    uawos_db.db_save_state("uawos_sandbox_runtime_state", seed)
    uawos_db.db_save_state("uawos_governance_state", seed)
    uawos_db.db_save_state("uawos_agent_runtime_state", seed)
    UAWOSSecretsManager._runtime_secrets.clear()

    ctx = UAWOSContext(
        correlation_id=str(uuid.uuid4()),
        causation_id=str(uuid.uuid4()),
        objective_id="OBJ-SBX-001",
        workflow_id="WF-SBX-001",
        action_id=str(uuid.uuid4()),
        actor="Lead Engineer",
        actor_role="Lead Engineer",
    )

    # SM-01: Secrets Manager store + retrieve
    UAWOSSecretsManager.store_secret("OPENAI_API_KEY", "sk-abc123testvalue456", "test")
    assert UAWOSSecretsManager.has_secret("OPENAI_API_KEY")
    assert UAWOSSecretsManager.get_secret("OPENAI_API_KEY") == "sk-abc123testvalue456"
    print("  [PASS] SM-01: SecretsManager store/retrieve verified.")

    # SM-02: Redaction — secret patterns
    raw_text = "My API key is sk-abc123testvalue456 and bearer Token123"
    redacted = UAWOSSecretsManager.redact(raw_text)
    assert "sk-abc123testvalue456" not in redacted
    print("  [PASS] SM-02: SecretsManager.redact (secret patterns) verified.")

    # SM-03: Redaction — stored secrets
    raw_dict = {"key": "sk-abc123testvalue456", "nested": {"token": "sk-abc123testvalue456"}}
    redacted_dict = UAWOSSecretsManager.redact_dict(raw_dict)
    assert "sk-abc123testvalue456" not in str(redacted_dict)
    print("  [PASS] SM-03: SecretsManager.redact_dict (deep redaction) verified.")

    # SM-04: Secrets requirement validation
    ok, missing = UAWOSSecretsManager.validate_requirements(["OPENAI_API_KEY"])
    assert ok, f"Missing: {missing}"
    ok2, missing2 = UAWOSSecretsManager.validate_requirements(["MISSING_KEY"])
    assert not ok2
    assert "MISSING_KEY" in missing2
    print("  [PASS] SM-04: SecretsManager.validate_requirements verified.")

    # TR-01: ToolRegistry register
    tool_echo = ToolDescriptor(
        tool_id="TOOL-ECHO-001",
        tool_name="echo",
        description="Echo test tool",
        license_class=LicenseClass.INTERNAL,
        sandbox_mode=SandboxMode.IN_PROCESS,
        owner="test",
    )
    assert ToolRegistry.register(tool_echo)
    print("  [PASS] TR-01: ToolRegistry.register verified.")

    # TR-02: ToolRegistry lookup by name
    found = ToolRegistry.find_by_name("echo")
    assert found is not None
    assert found.tool_id == "TOOL-ECHO-001"
    print("  [PASS] TR-02: ToolRegistry.find_by_name verified.")

    # TR-03: ToolRegistry list with license filter
    tool_gpl = ToolDescriptor(
        tool_id="TOOL-MARKER-001",
        tool_name="marker_pdf_converter",
        description="PDF to Markdown (GPLv3 isolated)",
        license_class=LicenseClass.COPYLEFT,
        sandbox_mode=SandboxMode.CONTAINER,
        endpoint_url="http://localhost:8000/convert",
        owner="platform",
    )
    ToolRegistry.register(tool_gpl)
    all_tools = ToolRegistry.list_tools()
    assert len(all_tools) >= 2
    copyleft_tools = ToolRegistry.list_tools(LicenseClass.COPYLEFT)
    assert len(copyleft_tools) >= 1
    print("  [PASS] TR-03: ToolRegistry.list_tools with license filter verified.")

    # TR-04: Tool deactivation
    assert ToolRegistry.deactivate("TOOL-MARKER-001", "License audit")
    deactivated = ToolRegistry.get("TOOL-MARKER-001")
    assert deactivated.status == "deactivated"
    print("  [PASS] TR-04: ToolRegistry.deactivate verified.")

    # Re-activate for further tests
    state = load_state(STATE_FILE, get_default_state)
    state["tool_registry"]["TOOL-MARKER-001"]["status"] = "active"
    save_state(STATE_FILE, state)

    # SBX-01: Sandbox executor — InProcess tool execution
    executor = UAWOSSandboxToolExecutor()
    UAWOSSandboxToolExecutor.register_callable(
        "TOOL-ECHO-001",
        lambda msg="": {"echo": msg},
    )
    result = executor.execute_tool("echo", {"msg": "hello"}, ctx)
    assert result["verdict"] == "APPROVED"
    assert result["output"]["echo"] == "hello"
    print("  [PASS] SBX-01: Sandbox executor InProcess execution verified.")

    # SBX-02: Sandbox executor — Container tool (simulation)
    result_container = executor.execute_tool("marker_pdf_converter", {"file": "test.pdf"}, ctx)
    assert result_container["verdict"] == "APPROVED"
    assert result_container["output"]["simulated"] is True
    assert result_container["output"]["sandbox_mode"] == "container"
    print("  [PASS] SBX-02: Sandbox executor Container (simulated) verified.")

    # SBX-03: Sandbox executor — unknown tool rejected
    result_unknown = executor.execute_tool("nonexistent_tool", {}, ctx)
    assert result_unknown["verdict"] == "REJECTED"
    print("  [PASS] SBX-03: Sandbox executor unknown tool rejected.")

    # SBX-04: License enforcement — Copyleft tool in InProcess mode blocked
    tool_bad_license = ToolDescriptor(
        tool_id="TOOL-BAD-001",
        tool_name="bad_gpl_tool",
        license_class=LicenseClass.COPYLEFT,
        sandbox_mode=SandboxMode.IN_PROCESS,  # Violation!
    )
    ToolRegistry.register(tool_bad_license)
    result_blocked = executor.execute_tool("bad_gpl_tool", {}, ctx)
    assert result_blocked["verdict"] == "REJECTED"
    assert "Copyleft" in result_blocked["error"]
    print("  [PASS] SBX-04: Copyleft InProcess license violation blocked.")

    # SBX-05: Missing secrets prevent execution
    tool_needs_secret = ToolDescriptor(
        tool_id="TOOL-SECRET-001",
        tool_name="secret_tool",
        license_class=LicenseClass.INTERNAL,
        sandbox_mode=SandboxMode.IN_PROCESS,
        required_secrets=["NONEXISTENT_SECRET"],
    )
    ToolRegistry.register(tool_needs_secret)
    result_no_secret = executor.execute_tool("secret_tool", {}, ctx)
    assert result_no_secret["verdict"] == "REJECTED"
    assert "Missing required secrets" in result_no_secret["error"]
    print("  [PASS] SBX-05: Missing secrets prevent tool execution.")

    # SBX-06: Deactivated tool rejected
    ToolRegistry.deactivate("TOOL-BAD-001")
    result_deactivated = executor.execute_tool("bad_gpl_tool", {}, ctx)
    assert result_deactivated["verdict"] == "REJECTED"
    assert "deactivated" in result_deactivated["error"]
    print("  [PASS] SBX-06: Deactivated tool rejected.")

    # SBX-07: Execution records persisted
    state = load_state(STATE_FILE, get_default_state)
    records = state.get("sandbox_executions", [])
    assert len(records) >= 2  # At least echo + marker executions
    print(f"  [PASS] SBX-07: {len(records)} execution records persisted.")

    # SBX-08: list_available_tools
    available = executor.list_available_tools()
    assert "echo" in available
    print(f"  [PASS] SBX-08: list_available_tools returns {len(available)} tools.")

    # SBX-09: Secret injection into container request
    tool_with_secret = ToolDescriptor(
        tool_id="TOOL-INJECT-001",
        tool_name="inject_test",
        required_secrets=["OPENAI_API_KEY"],
    )
    injected = UAWOSSecretsManager.inject_into_request(tool_with_secret, {"prompt": "hello"})
    assert "__secret_OPENAI_API_KEY__" in injected
    assert injected["__secret_OPENAI_API_KEY__"] == "sk-abc123testvalue456"
    print("  [PASS] SBX-09: Secret injection into sandbox request verified.")

    # SBX-10: Service template generation
    template = create_sandbox_service_template("pdf_converter")
    assert "Flask" in template
    assert "@app.route" in template
    assert "pdf_converter" in template
    print("  [PASS] SBX-10: Sandbox service template generation verified.")

    # SBX-11: Dockerfile template generation
    dockerfile = generate_dockerfile_template("pdf_converter")
    assert "FROM python:3.11-slim" in dockerfile
    assert "gunicorn" in dockerfile
    print("  [PASS] SBX-11: Dockerfile template generation verified.")

    print("\nAll Sandbox Runtime self tests completed successfully!")


if __name__ == "__main__":
    run_self_tests()
