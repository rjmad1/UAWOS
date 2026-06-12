"""
uawos_event_bus.py
==================
UAWOS Event Bus & Schema Registry — Wave 1 Deliverable

Provides:
  1. EventSchemaRegistry — validates all lifecycle events against canonical schemas.
  2. UAWOSEventBus — in-process pub/sub event bus (Wave 1 stub).
     Production upgrade: route publish() calls to Kafka/Redis.
  3. CorrelationManager — propagates and validates Correlation/Causation IDs.

Standards: ESLS (sections 4–6, 21–27), GCF Section 15, KMLS
"""

from __future__ import annotations

import contextlib
import os
import time
import uuid
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field

from uawos_agent_runtime import EventCategory, LifecycleEvent, UAWOSContext
from uawos_state_utils import load_state, save_state

# ---------------------------------------------------------------------------
# State File — required by load_state/save_state auto-resolution
# ---------------------------------------------------------------------------
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_event_bus_state.json")


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
# Event Schema Registry
# ---------------------------------------------------------------------------

# Canonical JSON Schema-style field requirements for each event category.
# Required keys per ESLS Section 4 (Event Characteristics):
_REQUIRED_FIELDS = {
    "all": [
        "event_id",
        "event_type",
        "event_version",
        "timestamp",
        "actor",
        "source",
        "correlation_id",
        "causation_id",
        "entity_ref",
    ]
}

_CATEGORY_PAYLOAD_SCHEMAS: dict[str, list[str]] = {
    EventCategory.OBJECTIVE_CREATED.value: ["objective_id"],
    EventCategory.PLAN_GENERATED.value: ["objective_id", "plan_id"],
    EventCategory.WORKFLOW_STARTED.value: ["step_id"],
    EventCategory.AGENT_ASSIGNED.value: ["agent_class", "capabilities"],
    EventCategory.ACTION_REQUESTED.value: [],
    EventCategory.GOVERNANCE_EVALUATED.value: ["verdict", "reason"],
    EventCategory.TOOL_EXECUTION_STARTED.value: ["tool", "arguments"],
    EventCategory.TOOL_EXECUTION_COMPLETED.value: ["tool", "output"],
    EventCategory.ACTION_COMPLETED.value: [],
    EventCategory.WORKFLOW_COMPLETED.value: [],
    EventCategory.WORKFLOW_FAILED.value: ["reason"],
}


class EventSchemaRegistry:
    """
    Validates lifecycle events against the canonical ESLS schemas.
    Rejects malformed events before they enter the event bus.
    """

    @staticmethod
    def validate(event: LifecycleEvent) -> tuple[bool, list[str]]:
        """
        Validate an event.
        Returns (is_valid: bool, errors: list[str]).
        """
        errors: list[str] = []
        event_dict = event.to_dict()

        # Check universal required fields (ESLS Section 4)
        for field_name in _REQUIRED_FIELDS["all"]:
            if not event_dict.get(field_name):
                errors.append(f"Missing required field: '{field_name}'")

        # Validate Correlation/Causation IDs are UUIDs
        for id_field in ("correlation_id", "causation_id"):
            val = event_dict.get(id_field, "")
            if val:
                try:
                    uuid.UUID(str(val))
                except ValueError:
                    errors.append(f"Field '{id_field}' must be a valid UUID.")

        # Validate event_type is a known category
        event_type = event_dict.get("event_type", "")
        if event_type not in _CATEGORY_PAYLOAD_SCHEMAS:
            errors.append(f"Unknown event_type: '{event_type}'")
        else:
            # Check payload-level required fields for this event type
            payload = event_dict.get("payload", {})
            for required_key in _CATEGORY_PAYLOAD_SCHEMAS[event_type]:
                if required_key not in payload:
                    errors.append(f"Payload missing required key '{required_key}' for event type '{event_type}'")

        return (len(errors) == 0, errors)

    @staticmethod
    def get_schema(event_type: str) -> dict:
        """Return the schema definition for a given event type."""
        return {
            "event_type": event_type,
            "required_fields": _REQUIRED_FIELDS["all"],
            "payload_required": _CATEGORY_PAYLOAD_SCHEMAS.get(event_type, []),
        }

    @staticmethod
    def list_schemas() -> list[dict]:
        """Return all registered event schemas."""
        return [EventSchemaRegistry.get_schema(et) for et in _CATEGORY_PAYLOAD_SCHEMAS]


# ---------------------------------------------------------------------------
# UAWOS Event Bus
# ---------------------------------------------------------------------------


@dataclass
class Subscription:
    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    handler: Callable[[LifecycleEvent], None] = field(default_factory=lambda: lambda e: None)
    subscriber_name: str = ""
    created_at: float = field(default_factory=time.time)


class UAWOSEventBus:
    """
    In-process pub/sub event bus with schema validation.

    Wave 1: In-process dict-based subscriptions + state-file persistence.
    Production upgrade (Wave 1+): Replace _publish_to_broker() with
      Kafka producer or Redis Streams XADD call.

    All published events:
      1. Are schema-validated before acceptance.
      2. Are persisted to the event_log in runtime state.
      3. Are dispatched synchronously to registered handlers.
    """

    _subscriptions: dict[str, list[Subscription]] = defaultdict(list)
    _event_history: list[dict] = []

    @classmethod
    def subscribe(
        cls,
        event_type: str,
        handler: Callable[[LifecycleEvent], None],
        subscriber_name: str = "",
    ) -> str:
        """Register a handler for a given event type. Returns subscription_id."""
        sub = Subscription(
            event_type=event_type,
            handler=handler,
            subscriber_name=subscriber_name,
        )
        cls._subscriptions[event_type].append(sub)
        return sub.subscription_id

    @classmethod
    def unsubscribe(cls, event_type: str, subscription_id: str) -> bool:
        """Remove a subscription by ID."""
        subs = cls._subscriptions.get(event_type, [])
        original_count = len(subs)
        cls._subscriptions[event_type] = [s for s in subs if s.subscription_id != subscription_id]
        return len(cls._subscriptions[event_type]) < original_count

    @classmethod
    def publish(cls, event: LifecycleEvent, validate: bool = True) -> tuple[bool, list[str]]:
        """
        Publish a lifecycle event.
          1. Validate schema.
          2. Persist to PostgreSQL event table with state-file fallback.
          3. Dispatch to subscribers.
          4. Publish to external broker.
        """
        if validate:
            is_valid, errors = EventSchemaRegistry.validate(event)
            if not is_valid:
                return False, errors

        # Persist to relational DB
        try:
            import uawos_db

            uawos_db.db_save_event(event.to_dict())
        except Exception:
            pass

        # Persist to runtime state (fallback)
        state = load_state(STATE_FILE, get_default_state)
        if "event_log" not in state:
            state["event_log"] = []
        state["event_log"].append(event.to_dict())
        save_state(STATE_FILE, state)
        cls._event_history.append(event.to_dict())

        # Dispatch to in-process subscribers
        event_type = event.event_type.value
        for sub in cls._subscriptions.get(event_type, []):
            with contextlib.suppress(Exception):
                sub.handler(event)

        # Publish to external Kafka broker
        cls._publish_to_broker(event)

        return True, []

    @classmethod
    def _publish_to_broker(cls, event: LifecycleEvent) -> None:
        """
        Publish event to Kafka broker with graceful fallback simulation.
        """
        import json
        import os

        # Try confluent-kafka first
        try:
            from confluent_kafka import Producer

            conf = {"bootstrap.servers": os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")}
            producer = Producer(conf)
            topic = event.event_type.value
            producer.produce(topic, json.dumps(event.to_dict()).encode("utf-8"))
            producer.flush(1.0)
            return
        except Exception:
            pass

        # Try kafka-python next
        try:
            from kafka import KafkaProducer

            producer = KafkaProducer(bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"))
            topic = event.event_type.value
            producer.send(topic, json.dumps(event.to_dict()).encode("utf-8"))
            producer.flush(timeout=1.0)
            return
        except Exception:
            pass

    @classmethod
    def get_history(
        cls,
        correlation_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Retrieve event history from PostgreSQL, optionally filtered by correlation_id or event_type."""
        try:
            import uawos_db

            db_events = uawos_db.db_get_events(correlation_id=correlation_id, event_type=event_type, limit=limit)
            if db_events:
                return db_events
        except Exception:
            pass

        # Fallback to local memory history
        events = cls._event_history
        if correlation_id:
            events = [e for e in events if e.get("correlation_id") == correlation_id]
        if event_type:
            events = [e for e in events if e.get("event_type") == event_type]
        return events[-limit:]

    @classmethod
    def replay(cls, correlation_id: str) -> list[LifecycleEvent]:
        """
        Replay all events for a correlation thread in chronological order (ESLS-04).
        Returns sorted LifecycleEvent instances.
        """
        db_events = []
        try:
            import uawos_db

            db_events = uawos_db.db_get_events(correlation_id=correlation_id)
        except Exception:
            pass

        if not db_events:
            try:
                state = load_state(STATE_FILE, get_default_state)
            except Exception:
                state = {"event_log": []}
            db_events = [e for e in state.get("event_log", []) if e.get("correlation_id") == correlation_id]

        db_events.sort(key=lambda e: e.get("timestamp", 0))

        result = []
        for e in db_events:
            try:
                evt = LifecycleEvent()
                for k, v in e.items():
                    if hasattr(evt, k):
                        if k == "event_type":
                            with contextlib.suppress(ValueError):
                                setattr(evt, k, EventCategory(v))
                        else:
                            setattr(evt, k, v)
                result.append(evt)
            except Exception:
                pass
        return result

    @classmethod
    def clear_subscriptions(cls) -> None:
        """Test helper — clear all subscriptions."""
        cls._subscriptions.clear()
        cls._event_history.clear()


# ---------------------------------------------------------------------------
# Correlation Manager
# ---------------------------------------------------------------------------


class CorrelationManager:
    """
    Manages propagation of Correlation and Causation IDs across the
    full UAWOS execution chain (ESLS Section 21).

    Usage pattern:
      ctx = CorrelationManager.new_root(objective_id="OBJ-001", actor="Lead Engineer")
      child_ctx = CorrelationManager.derive_child(ctx, action_id="ACT-TASK-001")
    """

    @staticmethod
    def new_root(
        objective_id: str = "",
        workflow_id: str = "",
        actor: str = "",
        actor_role: str = "",
    ) -> UAWOSContext:
        """Create a new root execution context."""
        return UAWOSContext(
            correlation_id=str(uuid.uuid4()),
            causation_id=str(uuid.uuid4()),
            objective_id=objective_id,
            workflow_id=workflow_id,
            action_id=str(uuid.uuid4()),
            actor=actor,
            actor_role=actor_role,
        )

    @staticmethod
    def derive_child(parent: UAWOSContext, action_id: str = "") -> UAWOSContext:
        """
        Derive a child context. The Correlation ID propagates unchanged.
        The Causation ID is set to the parent's action_id.
        """
        return parent.child(action_id or str(uuid.uuid4()))

    @staticmethod
    def inject_into_headers(ctx: UAWOSContext) -> dict:
        """
        Serialize context into HTTP-style headers for cross-service propagation.
        Production: inject into gRPC metadata or HTTP headers.
        """
        return {
            "X-UAWOS-Correlation-Id": ctx.correlation_id,
            "X-UAWOS-Causation-Id": ctx.causation_id,
            "X-UAWOS-Objective-Id": ctx.objective_id,
            "X-UAWOS-Workflow-Id": ctx.workflow_id,
            "X-UAWOS-Agent-Id": ctx.agent_id,
            "X-UAWOS-Action-Id": ctx.action_id,
            "X-UAWOS-Actor": ctx.actor,
            "X-UAWOS-Actor-Role": ctx.actor_role,
        }

    @staticmethod
    def extract_from_headers(headers: dict) -> UAWOSContext:
        """
        Reconstruct a UAWOSContext from HTTP-style propagation headers.
        """
        return UAWOSContext(
            correlation_id=headers.get("X-UAWOS-Correlation-Id", str(uuid.uuid4())),
            causation_id=headers.get("X-UAWOS-Causation-Id", str(uuid.uuid4())),
            objective_id=headers.get("X-UAWOS-Objective-Id", ""),
            workflow_id=headers.get("X-UAWOS-Workflow-Id", ""),
            agent_id=headers.get("X-UAWOS-Agent-Id", ""),
            action_id=headers.get("X-UAWOS-Action-Id", ""),
            actor=headers.get("X-UAWOS-Actor", ""),
            actor_role=headers.get("X-UAWOS-Actor-Role", ""),
        )

    @staticmethod
    def validate(ctx: UAWOSContext) -> tuple[bool, list[str]]:
        """Validate that a context has all mandatory fields populated."""
        errors = []
        if not ctx.correlation_id:
            errors.append("Correlation ID is missing.")
        if not ctx.causation_id:
            errors.append("Causation ID is missing.")
        if not ctx.actor:
            errors.append("Actor is missing.")
        return (len(errors) == 0, errors)


# ---------------------------------------------------------------------------
# Self-Tests
# ---------------------------------------------------------------------------


def run_self_tests():
    print("Running Event Bus & Correlation Manager self tests...")

    import uawos_db

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
    uawos_db.db_save_state("uawos_governance_state", seed)
    uawos_db.db_save_state("uawos_event_bus_state", seed)
    UAWOSEventBus.clear_subscriptions()

    # EB-01: Valid schema passes validation
    ctx = CorrelationManager.new_root("OBJ-001", "WF-001", "Lead Engineer", "Lead Engineer")
    evt = LifecycleEvent(
        event_type=EventCategory.GOVERNANCE_EVALUATED,
        actor="Lead Engineer",
        source="uawos_test",
        correlation_id=ctx.correlation_id,
        causation_id=ctx.causation_id,
        entity_ref="ACT-001",
        payload={"verdict": "APPROVED", "reason": "All checks passed."},
    )
    is_valid, errors = EventSchemaRegistry.validate(evt)
    assert is_valid, f"Validation failed: {errors}"
    print("  [PASS] EB-01: EventSchemaRegistry valid event verified.")

    # EB-02: Missing required field fails validation
    bad_evt = LifecycleEvent(
        event_type=EventCategory.GOVERNANCE_EVALUATED,
        actor="",  # missing
        source="",  # missing
        correlation_id="",  # missing
        causation_id="",  # missing
        entity_ref="",  # missing
        payload={"verdict": "APPROVED", "reason": "test"},
    )
    is_valid2, errors2 = EventSchemaRegistry.validate(bad_evt)
    assert not is_valid2
    assert any("actor" in e.lower() or "correlation" in e.lower() for e in errors2)
    print("  [PASS] EB-02: EventSchemaRegistry invalid event rejected.")

    # EB-03: Payload schema check
    missing_payload_evt = LifecycleEvent(
        event_type=EventCategory.GOVERNANCE_EVALUATED,
        actor="Lead Engineer",
        source="uawos_test",
        correlation_id=ctx.correlation_id,
        causation_id=ctx.causation_id,
        entity_ref="ACT-002",
        payload={},  # missing "verdict" and "reason"
    )
    is_valid3, errors3 = EventSchemaRegistry.validate(missing_payload_evt)
    assert not is_valid3
    print("  [PASS] EB-03: Payload schema missing key rejected.")

    # EB-04: Event Bus publish + subscribe
    received = []
    sub_id = UAWOSEventBus.subscribe(
        EventCategory.GOVERNANCE_EVALUATED.value,
        lambda e: received.append(e.event_type),
        "test-subscriber",
    )
    ok, errs = UAWOSEventBus.publish(evt)
    assert ok, f"Publish failed: {errs}"
    assert len(received) == 1
    print("  [PASS] EB-04: EventBus publish + subscribe dispatch verified.")

    # EB-05: Unsubscribe
    UAWOSEventBus.unsubscribe(EventCategory.GOVERNANCE_EVALUATED.value, sub_id)
    UAWOSEventBus.publish(evt)
    assert len(received) == 1  # No new event delivered
    print("  [PASS] EB-05: EventBus unsubscribe verified.")

    # EB-06: Event history retrieval by correlation_id
    history = UAWOSEventBus.get_history(correlation_id=ctx.correlation_id)
    assert len(history) >= 1
    print("  [PASS] EB-06: EventBus get_history by correlation_id verified.")

    # EB-07: Event replay (ESLS-04)
    replayed = UAWOSEventBus.replay(ctx.correlation_id)
    assert len(replayed) >= 1
    print("  [PASS] EB-07: EventBus.replay (ESLS replayability) verified.")

    # EB-08: Schema registry listing
    schemas = EventSchemaRegistry.list_schemas()
    assert len(schemas) == 11  # 11 canonical event types
    print(f"  [PASS] EB-08: EventSchemaRegistry lists all {len(schemas)} canonical event schemas.")

    # EB-09: CorrelationManager new_root
    root_ctx = CorrelationManager.new_root("OBJ-002", "WF-002", "CEO", "CEO")
    assert root_ctx.correlation_id
    assert root_ctx.objective_id == "OBJ-002"
    print("  [PASS] EB-09: CorrelationManager.new_root verified.")

    # EB-10: CorrelationManager derive_child
    child_ctx = CorrelationManager.derive_child(root_ctx, "ACT-CHILD")
    assert child_ctx.correlation_id == root_ctx.correlation_id
    # child causation_id == parent action_id (not parent causation_id)
    assert child_ctx.causation_id == root_ctx.action_id, (
        f"Expected causation={root_ctx.action_id!r}, got {child_ctx.causation_id!r}"
    )
    assert child_ctx.action_id == "ACT-CHILD"
    print("  [PASS] EB-10: CorrelationManager.derive_child verified.")

    # EB-11: Header injection/extraction round-trip
    headers = CorrelationManager.inject_into_headers(root_ctx)
    reconstructed = CorrelationManager.extract_from_headers(headers)
    assert reconstructed.correlation_id == root_ctx.correlation_id
    assert reconstructed.actor == root_ctx.actor
    print("  [PASS] EB-11: CorrelationManager header inject/extract round-trip verified.")

    # EB-12: Context validation
    is_valid_ctx, ctx_errors = CorrelationManager.validate(root_ctx)
    assert is_valid_ctx, f"Errors: {ctx_errors}"
    print("  [PASS] EB-12: CorrelationManager.validate (valid context) verified.")

    # EB-13: Context validation — missing actor
    empty_ctx = UAWOSContext()
    empty_ctx.actor = ""
    is_valid_empty, empty_errors = CorrelationManager.validate(empty_ctx)
    assert not is_valid_empty
    print("  [PASS] EB-13: CorrelationManager.validate (missing actor) verified.")

    print("\nAll Event Bus & Correlation Manager self tests completed successfully!")


if __name__ == "__main__":
    run_self_tests()
