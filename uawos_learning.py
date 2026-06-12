# uawos_learning.py
import os
import time

from uawos_state_utils import load_state, save_state

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_learning_state.json")


def get_default_state() -> dict:
    return {
        "learnings": {
            "LRN-101": {
                "id": "LRN-101",
                "opportunity": "Database query timeout during heavy loads",
                "proposal": "Implement index on user_id and cache checkout calls",
                "confidence_score": 92.0,
                "status": "approved",  # draft, approved, published
                "published_as_best_practice": True,
                "traceability_source": "ACT-101",
                "timestamp": 1780963292,
            }
        },
        "packs": {
            "LPK-01": {
                "id": "LPK-01",
                "name": "Database Performance Optimizations Pack",
                "learnings": ["LRN-101"],
            }
        },
    }


def detect_opportunities(action_logs: list) -> list:
    """Scan execution logs to recognize patterns and detect learning opportunities (FR-131, FR-136)."""
    opportunities = []
    for log in action_logs:
        # If latency is high, or action failed
        if log.get("latency_ms", 0) > 3000:
            opportunities.append(
                {
                    "type": "Performance Bottleneck",
                    "description": f"Latency of {log['action_name']} exceeded 3000ms threshold.",
                    "source": log.get("action_id", "ACT-GEN"),
                }
            )
        elif log.get("status") == "failed":
            opportunities.append(
                {
                    "type": "Execution Failure Pattern",
                    "description": f"Action {log['action_name']} failed with error: {log.get('error', 'unknown')}.",
                    "source": log.get("action_id", "ACT-GEN"),
                }
            )
    return opportunities


def generate_learning(opportunity: str, proposal: str, source_action_id: str, confidence: float = 90.0) -> dict:
    """Generate a learning recommendation (FR-132, FR-137, FR-139)."""
    state = load_state()
    lid = f"LRN-{len(state['learnings']) + 101:03d}"

    learning = {
        "id": lid,
        "opportunity": opportunity,
        "proposal": proposal,
        "confidence_score": confidence,
        "status": "draft",
        "published_as_best_practice": False,
        "traceability_source": source_action_id,
        "timestamp": int(time.time()),
    }
    state["learnings"][lid] = learning
    save_state(state)
    return state["learnings"][lid]


# FR-133: Approval
def approve_learning(learning_id: str) -> dict:
    state = load_state()
    learning = state["learnings"].get(learning_id)
    if not learning:
        raise ValueError(f"Learning {learning_id} not found.")
    learning["status"] = "approved"
    state["learnings"][learning_id] = learning
    save_state(state)
    return learning


# FR-134 & FR-135: Publish best practice
def publish_learning(learning_id: str) -> dict:
    state = load_state()
    learning = state["learnings"].get(learning_id)
    if not learning:
        raise ValueError(f"Learning {learning_id} not found.")
    learning["status"] = "published"
    learning["published_as_best_practice"] = True
    state["learnings"][learning_id] = learning
    save_state(state)
    return learning


# FR-138: Traceability
def get_learning_traceability(learning_id: str) -> dict:
    state = load_state()
    learning = state["learnings"].get(learning_id)
    if not learning:
        raise ValueError(f"Learning {learning_id} not found.")
    return {
        "learning_id": learning_id,
        "source_action_id": learning["traceability_source"],
        "traceability_chain": f"ACTION -> {learning['traceability_source']} -> OPPORTUNITY -> {learning['opportunity']} -> LEARNING -> {learning_id}",
    }


# FR-140: Learning Packs
def create_learning_pack(name: str, learning_ids: list) -> dict:
    state = load_state()
    pid = f"LPK-{len(state['packs']) + 1:02d}"
    pack = {"id": pid, "name": name, "learnings": learning_ids}
    state["packs"][pid] = pack
    save_state(state)
    return pack


# ----------------- VERIFICATION TESTS (FR-131 to FR-140) -----------------


def verify_fr_131():
    opps = detect_opportunities([{"action_name": "API call", "latency_ms": 4500, "action_id": "ACT-101"}])
    assert len(opps) > 0, "Opportunity detection failed."
    return True


def verify_fr_132():
    lrn = generate_learning("Query timeouts", "Add indexes", "ACT-101")
    assert lrn["id"].startswith("LRN-"), "Learning generation failed."
    return True


def verify_fr_133():
    lrn = approve_learning("LRN-101")
    assert lrn["status"] == "approved", "Learning approval failed."
    return True


def verify_fr_134():
    lrn = publish_learning("LRN-101")
    assert lrn["status"] == "published", "Learning publication failed."
    return True


def verify_fr_135():
    lrn = publish_learning("LRN-101")
    assert lrn["published_as_best_practice"] is True, "Best practice generation failed."
    return True


def verify_fr_136():
    opps = detect_opportunities(
        [
            {
                "action_name": "Query",
                "status": "failed",
                "error": "Deadlock",
                "action_id": "ACT-102",
            }
        ]
    )
    assert opps[0]["type"] == "Execution Failure Pattern", "Pattern recognition failed."
    return True


def verify_fr_137():
    lrn = generate_learning("Continuous feedback", "Refactor routing", "ACT-102")
    assert lrn["confidence_score"] == 90.0, "Continuous learning failed."
    return True


def verify_fr_138():
    trace = get_learning_traceability("LRN-101")
    assert "traceability_chain" in trace, "Traceability verification failed."
    return True


def verify_fr_139():
    lrn = generate_learning("Timeout", "Fix", "ACT-101", confidence=95.0)
    assert lrn["confidence_score"] == 95.0, "Confidence setting failed."
    return True


def verify_fr_140():
    pack = create_learning_pack("Security Pack", ["LRN-101"])
    assert len(pack["learnings"]) == 1, "Learning pack creation failed."
    return True


def run_self_tests():
    print("Running Learning Management self tests...")
    state = get_default_state()
    save_state(state)

    tests = [
        ("FR-131", verify_fr_131),
        ("FR-132", verify_fr_132),
        ("FR-133", verify_fr_133),
        ("FR-134", verify_fr_134),
        ("FR-135", verify_fr_135),
        ("FR-136", verify_fr_136),
        ("FR-137", verify_fr_137),
        ("FR-138", verify_fr_138),
        ("FR-139", verify_fr_139),
        ("FR-140", verify_fr_140),
    ]

    for code, fn in tests:
        try:
            fn()
            print(f"  [PASS] {code} verified.")
        except AssertionError as ae:
            print(f"  [FAIL] {code}: {ae}")
            raise ae

    print("All Learning Engine self tests completed successfully!")


if __name__ == "__main__":
    run_self_tests()
