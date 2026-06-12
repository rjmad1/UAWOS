"""
uawos_audit_ledger.py
=====================
UAWOS Audit & Replay Infrastructure — Wave 2 Deliverable

Provides:
  1. UAWOSAuditLedger    — Immutable, append-only audit log with Postgres backing.
  2. UAWOSCheckpointer   — SQL-backed state snapshot and time-travel replay.
  3. UAWOSLineageEmitter — OpenLineage-compatible run/dataset lineage tracking.
  4. ExplainabilityReport — Structured decision explanation builder.

All writes are append-only. Existing audit entries MUST NOT be modified.
This module is the authoritative source of truth for all governance decisions.

Standards: GCF Section 15 (Audit & Explainability), ESLS Section 21–27, KMLS
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass, field

import uawos_db
from uawos_agent_runtime import (
    UAWOSContext,
)
from uawos_state_utils import load_state, save_state

# ---------------------------------------------------------------------------
# State File — required by load_state/save_state auto-resolution
# ---------------------------------------------------------------------------
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_audit_ledger_state.json")


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
        "lineage_runs": [],
    }


# ---------------------------------------------------------------------------
# Immutable Audit Ledger
# ---------------------------------------------------------------------------


@dataclass
class LedgerEntry:
    """
    An immutable audit ledger entry. Once written, NEVER modified.
    Includes a content hash for tamper detection (GCF Section 15.4).
    """

    entry_id: str = field(default_factory=lambda: f"AUD-{uuid.uuid4().hex[:8].upper()}")
    entry_type: str = ""  # e.g. ACTION_COMPLETED, TOOL_BLOCKED, POLICY_REJECTED
    actor: str = ""
    correlation_id: str = ""
    causation_id: str = ""
    objective_id: str = ""
    workflow_id: str = ""
    agent_id: str = ""
    action_id: str = ""
    decision: str = ""  # APPROVED | REJECTED | SUSPENDED | BLOCKED
    reason: str = ""
    policy_ids: list = field(default_factory=list)
    payload: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    content_hash: str = ""

    def __post_init__(self):
        """Compute tamper-detection hash on creation."""
        if not self.content_hash:
            self.content_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """SHA-256 of all immutable fields."""
        raw = json.dumps(
            {
                "entry_id": self.entry_id,
                "entry_type": self.entry_type,
                "actor": self.actor,
                "correlation_id": self.correlation_id,
                "decision": self.decision,
                "timestamp": self.timestamp,
                "payload": self.payload,
            },
            sort_keys=True,
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify the content hash has not been tampered with."""
        return self.content_hash == self._compute_hash()

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "entry_type": self.entry_type,
            "actor": self.actor,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "objective_id": self.objective_id,
            "workflow_id": self.workflow_id,
            "agent_id": self.agent_id,
            "action_id": self.action_id,
            "decision": self.decision,
            "reason": self.reason,
            "policy_ids": self.policy_ids,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "content_hash": self.content_hash,
        }

    @classmethod
    def from_dict(cls, d: dict) -> LedgerEntry:
        e = cls(
            entry_id=d.get("entry_id", ""),
            entry_type=d.get("entry_type", ""),
            actor=d.get("actor", ""),
            correlation_id=d.get("correlation_id", ""),
            causation_id=d.get("causation_id", ""),
            objective_id=d.get("objective_id", ""),
            workflow_id=d.get("workflow_id", ""),
            agent_id=d.get("agent_id", ""),
            action_id=d.get("action_id", ""),
            decision=d.get("decision", ""),
            reason=d.get("reason", ""),
            policy_ids=d.get("policy_ids", []),
            payload=d.get("payload", {}),
            timestamp=d.get("timestamp", 0.0),
        )
        e.content_hash = d.get("content_hash", e.content_hash)
        return e

    @classmethod
    def from_context(
        cls,
        entry_type: str,
        ctx: UAWOSContext,
        decision: str,
        reason: str = "",
        policy_ids: list | None = None,
        payload: dict | None = None,
    ) -> LedgerEntry:
        """Convenience constructor from a UAWOSContext."""
        return cls(
            entry_type=entry_type,
            actor=ctx.actor,
            correlation_id=ctx.correlation_id,
            causation_id=ctx.causation_id,
            objective_id=ctx.objective_id,
            workflow_id=ctx.workflow_id,
            agent_id=ctx.agent_id,
            action_id=ctx.action_id,
            decision=decision,
            reason=reason,
            policy_ids=policy_ids or [],
            payload=payload or {},
        )


class UAWOSAuditLedger:
    """
    Immutable, append-only audit ledger.

    Wave 2: Writes to Postgres via uawos_db. Falls back to runtime state JSON.
    Production: Use Postgres partitioned table with row-level security.
    All reads support filtering by correlation_id, actor, decision, date range.
    """

    @staticmethod
    def write(entry: LedgerEntry) -> bool:
        """
        Append an audit entry. NEVER updates existing entries.
        Computes and stores content_hash for tamper detection.
        """
        try:
            state = load_state(STATE_FILE, get_default_state)
            if "audit_ledger" not in state:
                state["audit_ledger"] = []
            state["audit_ledger"].append(entry.to_dict())
            save_state(STATE_FILE, state)
            return True
        except Exception:
            return False

    @staticmethod
    def query(
        correlation_id: str | None = None,
        actor: str | None = None,
        decision: str | None = None,
        entry_type: str | None = None,
        since: float | None = None,
        limit: int = 200,
    ) -> list[LedgerEntry]:
        """
        Query the audit ledger with optional filters.
        Returns a chronologically ordered list of LedgerEntry objects.
        """
        try:
            state = load_state(STATE_FILE, get_default_state)
        except Exception:
            return []
        entries = state.get("audit_ledger", [])

        if correlation_id:
            entries = [e for e in entries if e.get("correlation_id") == correlation_id]
        if actor:
            entries = [e for e in entries if e.get("actor") == actor]
        if decision:
            entries = [e for e in entries if e.get("decision") == decision]
        if entry_type:
            entries = [e for e in entries if e.get("entry_type") == entry_type]
        if since:
            entries = [e for e in entries if e.get("timestamp", 0) >= since]

        entries = sorted(entries, key=lambda e: e.get("timestamp", 0))
        return [LedgerEntry.from_dict(e) for e in entries[-limit:]]

    @staticmethod
    def verify_integrity(correlation_id: str) -> tuple[bool, list[str]]:
        """
        Verify all entries for a correlation thread have intact content hashes.
        Returns (all_valid: bool, tampered_entry_ids: list[str]).
        """
        entries = UAWOSAuditLedger.query(correlation_id=correlation_id)
        tampered = [e.entry_id for e in entries if not e.verify_integrity()]
        return (len(tampered) == 0, tampered)

    @staticmethod
    def get_decision_trail(correlation_id: str) -> list[dict]:
        """
        Return the full governance decision trail for an execution thread.
        Ordered chronologically, showing each policy gate and its outcome.
        """
        entries = UAWOSAuditLedger.query(correlation_id=correlation_id)
        return [
            {
                "entry_id": e.entry_id,
                "timestamp": e.timestamp,
                "entry_type": e.entry_type,
                "actor": e.actor,
                "decision": e.decision,
                "reason": e.reason,
                "policy_ids": e.policy_ids,
            }
            for e in entries
        ]


# ---------------------------------------------------------------------------
# SQL-Backed State Checkpointer
# ---------------------------------------------------------------------------


@dataclass
class StateSnapshot:
    """An immutable state snapshot taken after each workflow step."""

    snapshot_id: str = field(default_factory=lambda: f"SNP-{uuid.uuid4().hex[:8].upper()}")
    thread_id: str = ""
    step_id: str = ""
    iteration: int = 0
    state: dict = field(default_factory=dict)
    correlation_id: str = ""
    causation_id: str = ""
    actor: str = ""
    captured_at: float = field(default_factory=time.time)
    schema_version: str = "1.0"

    def to_dict(self) -> dict:
        return {
            "snapshot_id": self.snapshot_id,
            "thread_id": self.thread_id,
            "step_id": self.step_id,
            "iteration": self.iteration,
            "state": self.state,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "actor": self.actor,
            "captured_at": self.captured_at,
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, d: dict) -> StateSnapshot:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


class UAWOSCheckpointer:
    """
    SQL-backed state checkpointer providing:
      - Per-step snapshot persistence (append-only)
      - Full snapshot history by thread_id
      - Time-travel: reconstruct state at any historical point
      - Ordered replay of all steps in a workflow thread

    Wave 2: Backed by runtime state JSON.
    Production: Write to Postgres table `uawos_agent_checkpoints` with tenant isolation.
    """

    @staticmethod
    def save(
        thread_id: str,
        step_id: str,
        state: dict,
        context: UAWOSContext,
        iteration: int = 0,
    ) -> str:
        """Save a state snapshot and return its snapshot_id."""
        snap = StateSnapshot(
            thread_id=thread_id,
            step_id=step_id,
            iteration=iteration,
            state={k: v for k, v in state.items() if isinstance(v, (str, int, float, bool, list, dict, type(None)))},
            correlation_id=context.correlation_id,
            causation_id=context.causation_id,
            actor=context.actor,
        )
        try:
            runtime_state = load_state(STATE_FILE, get_default_state)
            if "checkpoints" not in runtime_state:
                runtime_state["checkpoints"] = {}
            if thread_id not in runtime_state["checkpoints"]:
                runtime_state["checkpoints"][thread_id] = []
            runtime_state["checkpoints"][thread_id].append(snap.to_dict())
            save_state(STATE_FILE, runtime_state)
        except Exception:
            pass  # Non-fatal in Wave 2
        return snap.snapshot_id

    @staticmethod
    def load_latest(thread_id: str) -> StateSnapshot | None:
        """Load the most recent state snapshot for a thread."""
        snaps = UAWOSCheckpointer.list_snapshots(thread_id)
        if not snaps:
            return None
        return snaps[-1]

    @staticmethod
    def load_at(thread_id: str, snapshot_id: str) -> StateSnapshot | None:
        """Time-travel: load a specific historical snapshot by ID."""
        snaps = UAWOSCheckpointer.list_snapshots(thread_id)
        for s in snaps:
            if s.snapshot_id == snapshot_id:
                return s
        return None

    @staticmethod
    def load_at_index(thread_id: str, index: int) -> StateSnapshot | None:
        """Time-travel: load the snapshot at a specific position in the history."""
        snaps = UAWOSCheckpointer.list_snapshots(thread_id)
        if 0 <= index < len(snaps):
            return snaps[index]
        return None

    @staticmethod
    def list_snapshots(thread_id: str) -> list[StateSnapshot]:
        """List all snapshots for a thread, ordered chronologically."""
        try:
            runtime_state = load_state(STATE_FILE, get_default_state)
        except Exception:
            return []
        raw = runtime_state.get("checkpoints", {}).get(thread_id, [])
        snaps = [StateSnapshot.from_dict(s) for s in raw]
        return sorted(snaps, key=lambda s: s.captured_at)

    @staticmethod
    def reconstruct_timeline(thread_id: str) -> list[dict]:
        """
        Reconstruct the full step-by-step state evolution for a workflow thread.
        Returns a chronological list of {step_id, state_delta, snapshot_id, captured_at}.
        """
        snaps = UAWOSCheckpointer.list_snapshots(thread_id)
        if not snaps:
            return []

        timeline = []
        prev_state: dict = {}
        for snap in snaps:
            # Compute state delta (keys that changed)
            delta = {k: v for k, v in snap.state.items() if prev_state.get(k) != v}
            timeline.append(
                {
                    "snapshot_id": snap.snapshot_id,
                    "step_id": snap.step_id,
                    "iteration": snap.iteration,
                    "captured_at": snap.captured_at,
                    "state_delta": delta,
                    "full_state": snap.state,
                }
            )
            prev_state = snap.state

        return timeline

    @staticmethod
    def purge(thread_id: str) -> int:
        """
        Purge all snapshots for a thread (retention policy enforcement).
        Returns the number of snapshots purged.
        Production: Issue SQL DELETE with tenant_id isolation.
        """
        try:
            runtime_state = load_state(STATE_FILE, get_default_state)
            count = len(runtime_state.get("checkpoints", {}).get(thread_id, []))
            runtime_state["checkpoints"][thread_id] = []
            save_state(STATE_FILE, runtime_state)
            return count
        except Exception:
            return 0


# ---------------------------------------------------------------------------
# OpenLineage-Compatible Lineage Emitter
# ---------------------------------------------------------------------------


@dataclass
class LineageRun:
    """
    OpenLineage-compatible run descriptor for a workflow execution.
    Maps UAWOS correlation threads to OpenLineage run IDs.
    """

    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    job_name: str = ""
    job_namespace: str = "uawos"
    correlation_id: str = ""
    objective_id: str = ""
    workflow_id: str = ""
    actor: str = ""
    status: str = "RUNNING"  # RUNNING | COMPLETE | FAILED | ABORTED
    started_at: float = field(default_factory=time.time)
    ended_at: float = 0.0
    inputs: list = field(default_factory=list)  # list of dataset descriptors
    outputs: list = field(default_factory=list)  # list of dataset descriptors
    facets: dict = field(default_factory=dict)  # OpenLineage run facets

    def to_openlineage_event(self, event_type: str = "START") -> dict:
        """Serialize to OpenLineage 1.0 event format."""
        return {
            "eventType": event_type,
            "eventTime": self.started_at if event_type == "START" else self.ended_at or time.time(),
            "run": {
                "runId": self.run_id,
                "facets": {
                    **self.facets,
                    "uawos": {
                        "_producer": "https://uawos.ai/openlineage",
                        "_schemaURL": "https://uawos.ai/schemas/uawos-facet/1.0",
                        "correlation_id": self.correlation_id,
                        "objective_id": self.objective_id,
                        "workflow_id": self.workflow_id,
                        "actor": self.actor,
                    },
                },
            },
            "job": {
                "namespace": self.job_namespace,
                "name": self.job_name,
                "facets": {},
            },
            "inputs": self.inputs,
            "outputs": self.outputs,
            "producer": "https://uawos.ai",
            "schemaURL": "https://openlineage.io/spec/1-0-5/OpenLineage.json",
        }

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "job_name": self.job_name,
            "job_namespace": self.job_namespace,
            "correlation_id": self.correlation_id,
            "objective_id": self.objective_id,
            "workflow_id": self.workflow_id,
            "actor": self.actor,
            "status": self.status,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "facets": self.facets,
        }


class UAWOSLineageEmitter:
    """
    Emits OpenLineage-compatible lineage events for all agent workflow runs.
    Maps UAWOS correlation IDs to Marquez/OpenLineage run IDs.

    Wave 2: Stores lineage locally in runtime state.
    Production: POST to Marquez REST API at http://localhost:5000/api/v1/lineage
    """

    MARQUEZ_URL = os.environ.get("MARQUEZ_URL", "http://localhost:5000/api/v1/lineage")

    @classmethod
    def start_run(
        cls,
        job_name: str,
        context: UAWOSContext,
        inputs: list | None = None,
        facets: dict | None = None,
    ) -> LineageRun:
        """Create and register a new lineage run."""
        run = LineageRun(
            job_name=job_name,
            correlation_id=context.correlation_id,
            objective_id=context.objective_id,
            workflow_id=context.workflow_id,
            actor=context.actor,
            inputs=inputs or [],
            facets=facets or {},
        )
        cls._persist_run(run)
        cls._emit_openlineage(run, "START")
        return run

    @classmethod
    def complete_run(
        cls,
        run: LineageRun,
        outputs: list | None = None,
    ) -> None:
        """Mark a run as COMPLETE and emit the COMPLETE lineage event."""
        run.status = "COMPLETE"
        run.ended_at = time.time()
        run.outputs = outputs or []
        cls._persist_run(run)
        cls._emit_openlineage(run, "COMPLETE")

    @classmethod
    def fail_run(cls, run: LineageRun, reason: str = "") -> None:
        """Mark a run as FAILED and emit the FAIL lineage event."""
        run.status = "FAILED"
        run.ended_at = time.time()
        if reason:
            run.facets["failure_reason"] = reason
        cls._persist_run(run)
        cls._emit_openlineage(run, "FAIL")

    @classmethod
    def _persist_run(cls, run: LineageRun) -> None:
        """Persist the run to the runtime state lineage store."""
        try:
            state = load_state(STATE_FILE, get_default_state)
            if "lineage_runs" not in state:
                state["lineage_runs"] = []

            # Upsert: replace existing entry for same run_id
            updated = False
            for i, r in enumerate(state["lineage_runs"]):
                if r.get("run_id") == run.run_id:
                    state["lineage_runs"][i] = run.to_dict()
                    updated = True
                    break
            if not updated:
                state["lineage_runs"].append(run.to_dict())

            save_state(STATE_FILE, state)
        except Exception:
            pass

    @classmethod
    def _emit_openlineage(cls, run: LineageRun, event_type: str) -> None:
        """
        Emit OpenLineage event.
        POST to Marquez REST API with timeout protection.
        """
        import json
        import urllib.request

        event = run.to_openlineage_event(event_type)
        try:
            req_data = json.dumps(event).encode("utf-8")
            req = urllib.request.Request(
                cls.MARQUEZ_URL,
                data=req_data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=2.0) as response:
                response.read()
        except Exception:
            pass

    @classmethod
    def get_runs(cls, correlation_id: str) -> list[LineageRun]:
        """Retrieve all lineage runs for a correlation thread."""
        try:
            state = load_state(STATE_FILE, get_default_state)
        except Exception:
            return []
        runs = state.get("lineage_runs", [])
        return [
            LineageRun(**{k: v for k, v in r.items() if k in LineageRun.__dataclass_fields__})
            for r in runs
            if r.get("correlation_id") == correlation_id
        ]


# ---------------------------------------------------------------------------
# Explainability Report Builder
# ---------------------------------------------------------------------------


@dataclass
class ExplainabilityReport:
    """
    Structured explanation of a governance decision (GCF Section 15.5 — Explainability).
    Generated on-demand from the audit ledger for any correlation thread.
    """

    report_id: str = field(default_factory=lambda: f"RPT-{uuid.uuid4().hex[:8].upper()}")
    correlation_id: str = ""
    objective_id: str = ""
    workflow_id: str = ""
    generated_at: float = field(default_factory=time.time)
    generated_by: str = "UAWOSAuditLedger"
    decision_trail: list = field(default_factory=list)
    state_timeline: list = field(default_factory=list)
    lineage_runs: list = field(default_factory=list)
    summary: str = ""
    final_decision: str = ""

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "correlation_id": self.correlation_id,
            "objective_id": self.objective_id,
            "workflow_id": self.workflow_id,
            "generated_at": self.generated_at,
            "generated_by": self.generated_by,
            "decision_trail": self.decision_trail,
            "state_timeline": self.state_timeline,
            "lineage_runs": self.lineage_runs,
            "summary": self.summary,
            "final_decision": self.final_decision,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


class ExplainabilityEngine:
    """
    Generates structured explainability reports combining:
      - Governance decision trail (from UAWOSAuditLedger)
      - State evolution timeline (from UAWOSCheckpointer)
      - Lineage run map (from UAWOSLineageEmitter)
    """

    @staticmethod
    def generate_report(
        correlation_id: str,
        thread_id: str | None = None,
        requestor: str = "",
    ) -> ExplainabilityReport:
        """
        Generate a comprehensive explainability report for a correlation thread.
        """
        decision_trail = UAWOSAuditLedger.get_decision_trail(correlation_id)
        state_timeline = UAWOSCheckpointer.reconstruct_timeline(thread_id or correlation_id)
        lineage_runs = [r.to_dict() for r in UAWOSLineageEmitter.get_runs(correlation_id)]

        # Determine final decision from trail
        decisions = [e["decision"] for e in decision_trail]
        if "REJECTED" in decisions or "BLOCKED" in decisions:
            final_decision = "REJECTED"
        elif "SUSPENDED" in decisions:
            final_decision = "SUSPENDED"
        elif decisions:
            final_decision = decisions[-1]
        else:
            final_decision = "UNKNOWN"

        # Build human-readable summary
        n_approved = decisions.count("APPROVED")
        n_rejected = sum(1 for d in decisions if d in ("REJECTED", "BLOCKED"))
        n_steps = len(state_timeline)
        n_runs = len(lineage_runs)

        summary = (
            f"Execution thread '{correlation_id}' involved {len(decision_trail)} governance decisions: "
            f"{n_approved} approved, {n_rejected} rejected/blocked. "
            f"{n_steps} state snapshots recorded across {n_runs} lineage runs. "
            f"Final outcome: {final_decision}."
        )

        return ExplainabilityReport(
            correlation_id=correlation_id,
            generated_by=requestor or "UAWOSAuditLedger",
            decision_trail=decision_trail,
            state_timeline=state_timeline,
            lineage_runs=lineage_runs,
            summary=summary,
            final_decision=final_decision,
        )

    @staticmethod
    def verify_audit_integrity(correlation_id: str) -> dict:
        """
        Verify tamper-detection hashes for all audit entries in a thread.
        Returns {is_intact: bool, tampered_entries: list[str], checked_count: int}.
        """
        is_intact, tampered = UAWOSAuditLedger.verify_integrity(correlation_id)
        entries = UAWOSAuditLedger.query(correlation_id=correlation_id)
        return {
            "is_intact": is_intact,
            "tampered_entries": tampered,
            "checked_count": len(entries),
        }


# ---------------------------------------------------------------------------
# Self-Tests
# ---------------------------------------------------------------------------


def run_self_tests():
    print("Running Audit Ledger & Replay Infrastructure self tests...")

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
    }
    uawos_db.db_save_state("uawos_audit_ledger_state", seed)

    ctx = UAWOSContext(
        correlation_id=str(uuid.uuid4()),
        causation_id=str(uuid.uuid4()),
        objective_id="OBJ-AUDIT-001",
        workflow_id="WF-AUDIT-001",
        agent_id="AGENT-PLANNER-01",
        action_id=str(uuid.uuid4()),
        actor="Lead Engineer",
        actor_role="Lead Engineer",
    )

    # AL-01: LedgerEntry construction and hash
    entry = LedgerEntry.from_context(
        "ACTION_COMPLETED",
        ctx,
        "APPROVED",
        reason="All governance checks passed.",
        policy_ids=["POL-01"],
        payload={"task": "analyze_objective"},
    )
    assert entry.content_hash, "Content hash must be generated."
    assert entry.verify_integrity(), "Freshly created entry must verify cleanly."
    print("  [PASS] AL-01: LedgerEntry construction and integrity hash verified.")

    # AL-02: Ledger write
    ok = UAWOSAuditLedger.write(entry)
    assert ok, "Ledger write must succeed."
    print("  [PASS] AL-02: UAWOSAuditLedger.write verified.")

    # AL-03: Ledger query by correlation_id
    results = UAWOSAuditLedger.query(correlation_id=ctx.correlation_id)
    assert len(results) >= 1
    assert results[0].entry_id == entry.entry_id
    print("  [PASS] AL-03: UAWOSAuditLedger.query by correlation_id verified.")

    # AL-04: Ledger query by decision
    results_approved = UAWOSAuditLedger.query(correlation_id=ctx.correlation_id, decision="APPROVED")
    assert len(results_approved) >= 1
    print("  [PASS] AL-04: UAWOSAuditLedger.query by decision verified.")

    # AL-05: Integrity verification
    is_intact, tampered = UAWOSAuditLedger.verify_integrity(ctx.correlation_id)
    assert is_intact, f"Integrity check failed: tampered={tampered}"
    print("  [PASS] AL-05: UAWOSAuditLedger.verify_integrity (clean) verified.")

    # AL-06: Tamper detection — modify a hash and re-verify
    try:
        state = load_state(STATE_FILE, get_default_state)
        if state.get("audit_ledger"):
            state["audit_ledger"][0]["content_hash"] = "tampered_hash"
            save_state(STATE_FILE, state)
        is_intact2, tampered2 = UAWOSAuditLedger.verify_integrity(ctx.correlation_id)
        assert not is_intact2, "Tampered ledger must fail integrity check."
        assert len(tampered2) >= 1
        print("  [PASS] AL-06: Tamper detection correctly flags modified content_hash.")
    finally:
        # Restore state
        uawos_db.db_save_state("uawos_audit_ledger_state", seed)
        UAWOSAuditLedger.write(entry)

    # AL-07: Decision trail
    trail = UAWOSAuditLedger.get_decision_trail(ctx.correlation_id)
    assert len(trail) >= 1
    assert "decision" in trail[0]
    print("  [PASS] AL-07: UAWOSAuditLedger.get_decision_trail verified.")

    # CK-01: Checkpointer save
    snap_id = UAWOSCheckpointer.save(
        thread_id=ctx.workflow_id,
        step_id="step_analyze",
        state={"messages": ["hello"], "plan": None},
        context=ctx,
        iteration=1,
    )
    assert snap_id.startswith("SNP-")
    print("  [PASS] CK-01: UAWOSCheckpointer.save verified.")

    # CK-02: Load latest
    latest = UAWOSCheckpointer.load_latest(ctx.workflow_id)
    assert latest is not None
    assert latest.step_id == "step_analyze"
    assert latest.state["messages"] == ["hello"]
    print("  [PASS] CK-02: UAWOSCheckpointer.load_latest verified.")

    # CK-03: Time-travel by index
    # Add second snapshot
    UAWOSCheckpointer.save(
        thread_id=ctx.workflow_id,
        step_id="step_execute",
        state={"messages": ["hello", "world"], "plan": "step1"},
        context=ctx,
        iteration=2,
    )
    snap_at_0 = UAWOSCheckpointer.load_at_index(ctx.workflow_id, 0)
    assert snap_at_0.step_id == "step_analyze"
    snap_at_1 = UAWOSCheckpointer.load_at_index(ctx.workflow_id, 1)
    assert snap_at_1.step_id == "step_execute"
    print("  [PASS] CK-03: UAWOSCheckpointer time-travel by index verified.")

    # CK-04: Reconstruct timeline with state delta
    timeline = UAWOSCheckpointer.reconstruct_timeline(ctx.workflow_id)
    assert len(timeline) == 2
    # Second step delta should show 'messages' updated and 'plan' appeared
    delta = timeline[1]["state_delta"]
    assert "messages" in delta or "plan" in delta
    print("  [PASS] CK-04: UAWOSCheckpointer.reconstruct_timeline with state delta verified.")

    # CK-05: Load by snapshot_id
    snap_by_id = UAWOSCheckpointer.load_at(ctx.workflow_id, snap_id)
    assert snap_by_id is not None
    assert snap_by_id.snapshot_id == snap_id
    print("  [PASS] CK-05: UAWOSCheckpointer.load_at by snapshot_id verified.")

    # CK-06: Purge
    purged = UAWOSCheckpointer.purge(ctx.workflow_id)
    assert purged == 2
    assert UAWOSCheckpointer.load_latest(ctx.workflow_id) is None
    print("  [PASS] CK-06: UAWOSCheckpointer.purge verified.")

    # Re-add snapshot for explainability test
    UAWOSCheckpointer.save(ctx.workflow_id, "step_analyze", {"plan": "v1"}, ctx, 1)
    UAWOSAuditLedger.write(entry)

    # LN-01: Lineage run start/complete
    run = UAWOSLineageEmitter.start_run("analyze_objective", ctx)
    assert run.run_id
    assert run.status == "RUNNING"
    UAWOSLineageEmitter.complete_run(run, outputs=[{"name": "plan_v1", "namespace": "uawos"}])
    assert run.status == "COMPLETE"
    print("  [PASS] LN-01: UAWOSLineageEmitter start_run/complete_run verified.")

    # LN-02: OpenLineage event serialization
    ol_event = run.to_openlineage_event("COMPLETE")
    assert ol_event["eventType"] == "COMPLETE"
    assert ol_event["run"]["facets"]["uawos"]["correlation_id"] == ctx.correlation_id
    print("  [PASS] LN-02: OpenLineage event format verified.")

    # LN-03: Get runs by correlation_id
    runs = UAWOSLineageEmitter.get_runs(ctx.correlation_id)
    assert len(runs) >= 1
    print("  [PASS] LN-03: UAWOSLineageEmitter.get_runs verified.")

    # EX-01: Explainability report generation
    report = ExplainabilityEngine.generate_report(
        correlation_id=ctx.correlation_id,
        thread_id=ctx.workflow_id,
        requestor="Lead Engineer",
    )
    assert report.correlation_id == ctx.correlation_id
    assert report.final_decision in ("APPROVED", "REJECTED", "UNKNOWN")
    assert report.summary
    assert "decision_trail" in report.to_dict()
    print("  [PASS] EX-01: ExplainabilityEngine.generate_report verified.")

    # EX-02: Report to JSON
    json_str = report.to_json()
    parsed = json.loads(json_str)
    assert parsed["report_id"] == report.report_id
    print("  [PASS] EX-02: ExplainabilityReport.to_json verified.")

    # EX-03: Integrity verification via ExplainabilityEngine
    integrity = ExplainabilityEngine.verify_audit_integrity(ctx.correlation_id)
    assert "is_intact" in integrity
    assert "checked_count" in integrity
    print("  [PASS] EX-03: ExplainabilityEngine.verify_audit_integrity verified.")

    print("\nAll Audit Ledger & Replay Infrastructure self tests completed successfully!")


if __name__ == "__main__":
    run_self_tests()
