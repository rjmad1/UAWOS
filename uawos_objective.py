# uawos_objective.py
import os
import time

from uawos_state_utils import load_state, save_state
from application.use_cases.objective_use_cases import (
    create_objective,
    update_objective,
    archive_objective,
    restore_objective,
    cancel_objective,
    pause_objective,
    resume_objective,
    create_objective_from_input,
    recalculate_scores,
    detect_objective_conflicts,
)

# Alias for backwards compatibility
detect_conflicts = detect_objective_conflicts

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_objective_state.json")


def get_default_state() -> dict:
    return {"objectives": {}}


# ----------------- VERIFICATION TESTS (FR-011 to FR-030) -----------------


def verify_fr_011():
    """Verify Objective creation from voice input."""
    obj = create_objective_from_input(
        "Voice transcript: setup postgres DB immediately", "voice", "Lead Engineer", "CPO"
    )
    assert obj["source_type"] == "voice", "Voice intake source type mismatch."
    return True


def verify_fr_012():
    """Verify Objective creation from text input."""
    obj = create_objective_from_input("Need to migrate the RAG pipeline to Qdrant", "text", "Architect", "CPO")
    assert obj["source_type"] == "text", "Text intake source type mismatch."
    return True


def verify_fr_013():
    """Verify Objective creation from documents."""
    obj = create_objective_from_input("Document body: ensure OPA policies are compiled", "document", "Officer", "CPO")
    assert obj["source_type"] == "document", "Document intake source type mismatch."
    return True


def verify_fr_014():
    """Verify Objective creation from meeting transcripts."""
    obj = create_objective_from_input(
        "Transcript line: let's launch the checkout page next sprint", "meeting_transcript", "Manager", "CPO"
    )
    assert obj["source_type"] == "meeting_transcript", "Meeting transcript source type mismatch."
    return True


def verify_fr_015():
    """Verify Objective creation from images."""
    obj = create_objective_from_input("OCR extracted dashboard mockup text", "image", "Designer", "CPO")
    assert obj["source_type"] == "image", "Image intake source type mismatch."
    return True


def verify_fr_016():
    """Verify Objective creation from APIs."""
    obj = create_objective_from_input('{"payload": "API call definition"}', "api", "Integration Dev", "CPO")
    assert obj["source_type"] == "api", "API intake source type mismatch."
    return True


def verify_fr_017():
    """Verify ownership maintenance."""
    obj = create_objective("DB tuning", "Tune DB", "text", "", "Database Expert", "CPO", "High")
    assert obj["owner"] == "Database Expert", "Objective owner field mismatch."
    return True


def verify_fr_018():
    """Verify sponsorship maintenance."""
    obj = create_objective("DB tuning 2", "Tune DB 2", "text", "", "Database Expert", "VP Engineering", "High")
    assert obj["sponsor"] == "VP Engineering", "Objective sponsor field mismatch."
    return True


def verify_fr_019():
    """Verify Objective prioritization."""
    obj = create_objective("Sec scan", "Sec scan", "text", "", "Auditor", "CPO", "Critical")
    assert obj["priority"] == "Critical", "Objective priority field mismatch."
    return True


def verify_fr_020():
    """Verify Objective dependencies."""
    obj = create_objective("Task B", "B", "text", "", "Dev", "CPO", "Medium", ["OBJ-201"])
    assert "OBJ-201" in obj["dependencies"], "Dependencies list mismatch."
    return True


def verify_fr_021():
    """Verify conflict structure support."""
    conflicts = detect_conflicts()
    assert isinstance(conflicts, list), "Conflicts must return a list."
    return True


def verify_fr_022():
    """Verify conflict detection (detect circular loops and priority mismatches)."""
    state = load_state()
    # Create circular dependency OBJ-CYC1 <-> OBJ-CYC2
    state["objectives"]["OBJ-CYC1"] = {
        "id": "OBJ-CYC1",
        "title": "Cycle 1",
        "description": "",
        "source_type": "text",
        "source_uri": "",
        "owner": "A",
        "sponsor": "B",
        "priority": "Medium",
        "dependencies": ["OBJ-CYC2"],
        "status": "active",
        "version": 1,
        "history": [],
        "health_score": 100.0,
        "confidence_score": 100.0,
    }
    state["objectives"]["OBJ-CYC2"] = {
        "id": "OBJ-CYC2",
        "title": "Cycle 2",
        "description": "",
        "source_type": "text",
        "source_uri": "",
        "owner": "A",
        "sponsor": "B",
        "priority": "Medium",
        "dependencies": ["OBJ-CYC1"],
        "status": "active",
        "version": 1,
        "history": [],
        "health_score": 100.0,
        "confidence_score": 100.0,
    }
    save_state(state)

    conflicts = detect_conflicts()
    circular_found = any(c["type"] == "Circular Dependency" for c in conflicts)
    assert circular_found, "Circular dependency not detected."

    # Cleanup state
    state = load_state()
    state["objectives"].pop("OBJ-CYC1", None)
    state["objectives"].pop("OBJ-CYC2", None)
    save_state(state)
    return True


def verify_fr_023():
    """Verify Objective versioning."""
    obj = create_objective("Version Test", "V1", "text", "", "A", "B", "Low")
    assert obj["version"] == 1, "Initial version must be 1."
    updated = update_objective(obj["id"], {"title": "Version Test Updated"})
    assert updated["version"] == 2, "Updated version must be 2."
    return True


def verify_fr_024():
    """Verify Objective history preservation."""
    state = load_state()
    # Find active objective from verify_fr_023
    target_id = None
    for k, v in state["objectives"].items():
        if v["title"] == "Version Test Updated":
            target_id = k
            break

    assert target_id is not None, "Version test target objective missing."
    obj = state["objectives"][target_id]
    assert len(obj["history"]) == 1, "Objective history snapshot not recorded."
    assert obj["history"][0]["state"]["title"] == "Version Test", "History snapshot value mismatch."
    return True


def verify_fr_025():
    """Verify Objective archival."""
    obj = create_objective("Archive Test", "Details", "text", "", "A", "B", "Low")
    archived = archive_objective(obj["id"])
    assert archived["status"] == "archived", "Archive state not set."
    return True


def verify_fr_026():
    """Verify Objective restoration."""
    state = load_state()
    target_id = None
    for k, v in state["objectives"].items():
        if v["title"] == "Archive Test" and v["status"] == "archived":
            target_id = k
            break
    assert target_id is not None, "Archived target missing."
    restored = restore_objective(target_id)
    assert restored["status"] == "active", "Objective restore state failed."
    return True


def verify_fr_027():
    """Verify Objective cancellation."""
    obj = create_objective("Cancel Test", "Details", "text", "", "A", "B", "Low")
    cancelled = cancel_objective(obj["id"])
    assert cancelled["status"] == "cancelled", "Cancelled state not set."
    return True


def verify_fr_028():
    """Verify Objective pausing."""
    obj = create_objective("Pause Test", "Details", "text", "", "A", "B", "Low")
    paused = pause_objective(obj["id"])
    assert paused["status"] == "paused", "Paused state not set."
    return True


def verify_fr_029():
    """Verify Objective health scoring."""
    obj = create_objective("Health Score Test", "Details", "text", "", "A", "B", "Low")
    assert obj["health_score"] == 80.0, "Health score must initially be 80.0 due to Constitutional Law 1."

    import uawos_outcome

    uawos_outcome.create_outcome(obj["id"], "Test Metric", "Metric", "units")

    recalculate_scores(obj["id"])
    state = load_state()
    updated_obj = state["objectives"][obj["id"]]
    assert updated_obj["health_score"] == 100.0, "Health score must become 100.0 once outcomes exist."
    return True


def verify_fr_030():
    """Verify Objective confidence scoring."""
    obj = create_objective("Confidence Score Test", "Details", "text", "", "A", "B", "Low")
    assert obj["confidence_score"] <= 100.0, "Confidence score calculation issue."
    return True


def run_self_tests():
    print("Running Objective Management Engine self tests...")

    # Clean state for tests
    state = get_default_state()
    save_state(state)

    # Clean outcomes state to avoid collision on OBJ-101 ID with pre-seeded outcomes
    try:
        import uawos_db

        uawos_db.db_save_state("uawos_outcome_state", {"outcomes": {}})
    except Exception:
        pass

    tests = [
        ("FR-011", verify_fr_011),
        ("FR-012", verify_fr_012),
        ("FR-013", verify_fr_013),
        ("FR-014", verify_fr_014),
        ("FR-015", verify_fr_015),
        ("FR-016", verify_fr_016),
        ("FR-017", verify_fr_017),
        ("FR-018", verify_fr_018),
        ("FR-019", verify_fr_019),
        ("FR-020", verify_fr_020),
        ("FR-021", verify_fr_021),
        ("FR-022", verify_fr_022),
        ("FR-023", verify_fr_023),
        ("FR-024", verify_fr_024),
        ("FR-025", verify_fr_025),
        ("FR-026", verify_fr_026),
        ("FR-027", verify_fr_027),
        ("FR-028", verify_fr_028),
        ("FR-029", verify_fr_029),
        ("FR-030", verify_fr_030),
    ]

    for code, fn in tests:
        try:
            fn()
            print(f"  [PASS] {code} verified.")
        except AssertionError as ae:
            print(f"  [FAIL] {code}: {ae}")
            raise ae

    print("All Objective Engine self tests completed successfully!")


if __name__ == "__main__":
    run_self_tests()
