# uawos_action.py
import os
import time

import uawos_db
from uawos_state_utils import load_state, save_state

from application.use_cases.action_use_cases import (
    create_action,
    decompose_workflow,
    reassign_action,
    get_action_traceability,
    execute_agent_action_secure,
    MOCK_SERVICES_BASE_URL,
)

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_action_state.json")


def get_default_state() -> dict:
    return {
        "actions": {
            "ACT-101": {
                "id": "ACT-101",
                "workflow_id": "WRK-101",
                "name": "Analyze database slow queries",
                "owner": "Database Expert",
                "dependencies": [],
                "priority": "High",
                "budget": 200.0,
                "deadline": 1781049600,  # timestamp
                "status": "pending",  # pending, running, completed, failed
                "approval_required": True,
            }
        }
    }


# ----------------- VERIFICATION TESTS (FR-071 to FR-080) -----------------


def verify_fr_071():
    acts = decompose_workflow("WRK-101")
    assert len(acts) > 0, "Decomposition failed."
    return True


def verify_fr_072():
    act = load_state()["actions"]["ACT-101"]
    assert act["owner"] == "Database Expert", "Action owner failed."
    return True


def verify_fr_073():
    act = create_action("WRK-101", "Task X", "Dev", dependencies=["ACT-101"])
    assert "ACT-101" in act["dependencies"], "Dependencies failed."
    return True


def verify_fr_074():
    act = create_action("WRK-101", "Task Y", "Dev", priority="Critical")
    assert act["priority"] == "Critical", "Priority setting failed."
    return True


def verify_fr_075():
    act = create_action("WRK-101", "Task Z", "Dev", budget=120.0)
    assert act["budget"] == 120.0, "Budget mapping failed."
    return True


def verify_fr_076():
    act = create_action("WRK-101", "Task A", "Dev", deadline=123456)
    assert act["deadline"] == 123456, "Deadline setting failed."
    return True


def verify_fr_077():
    act = create_action("WRK-101", "Task B", "Dev", status="running")
    assert act["status"] == "running", "Execution status failed."
    return True


def verify_fr_078():
    trace = get_action_traceability("ACT-101")
    assert "traceability_chain" in trace, "Traceability verification failed."
    return True


def verify_fr_079():
    act = create_action("WRK-101", "Task C", "Dev", approval_required=True)
    assert act["approval_required"] is True, "Approval requirement failed."
    return True


def verify_fr_080():
    act = reassign_action("ACT-101", "Senior Engineer")
    assert act["owner"] == "Senior Engineer", "Reassignment failed."
    return True


def verify_fr_081():
    # Test safe command
    res_safe = execute_agent_action_secure("ACT-101", "echo 'hello'")
    assert res_safe["status"] in [
        "success",
        "blocked",
    ], "Command execution result invalid status."
    assert res_safe["action"]["status"] in [
        "completed",
        "failed",
    ], "Action status not updated correctly."

    # Test dangerous command
    res_unsafe = execute_agent_action_secure("ACT-101", "rm -rf /")
    assert res_unsafe["status"] == "blocked", "Dangerous command execution was not blocked."
    assert "Security Sandbox Block" in res_unsafe["reason"], "Blocked reason not captured."
    assert res_unsafe["action"]["status"] == "failed", "Action status not updated to failed on block."
    return True


def run_self_tests():
    print("Running Action Management self tests...")
    if uawos_db.DB_AVAILABLE:
        try:
            # Seed dependencies: OBJ-101 -> PLN-101 -> WRK-101
            uawos_db.db_save_objective(
                {
                    "id": "OBJ-101",
                    "title": "Default Objective for Testing",
                    "description": "Test objective description",
                    "source_type": "text",
                    "source_uri": "",
                    "owner": "Product Owner",
                    "sponsor": "CEO",
                    "priority": "High",
                    "status": "active",
                    "version": 1,
                    "health_score": 80.0,
                    "confidence_score": 90.0,
                    "dependencies": [],
                    "history": [],
                }
            )
            uawos_db.db_save_plan(
                {
                    "id": "PLN-101",
                    "objective_id": "OBJ-101",
                    "title": "Optimized Funnel Refactor Plan",
                    "steps": ["Step 1", "Step 2"],
                    "cost_estimate": 1000.0,
                    "duration_estimate": 120.0,
                    "resource_requirements": {},
                    "success_probability": 95.0,
                    "status": "approved",
                    "version": 1,
                    "risks": [],
                    "assumptions": [],
                    "is_alternative": False,
                    "history": [],
                }
            )
            uawos_db.db_save_workflow(
                {
                    "id": "WRK-101",
                    "plan_id": "PLN-101",
                    "title": "Optimized Funnel Refactor Workflow",
                    "tasks": [
                        "DB Index Setup",
                        "Cache Configuration",
                        "Verification Tests",
                    ],
                    "dependencies": [],
                    "state": "active",
                    "version": 1,
                    "governed": True,
                    "history": [],
                }
            )
        except Exception as e:
            print(f"Failed to seed dependencies in self-test setup: {e}")
    state = get_default_state()
    save_state(state)

    tests = [
        ("FR-071", verify_fr_071),
        ("FR-072", verify_fr_072),
        ("FR-073", verify_fr_073),
        ("FR-074", verify_fr_074),
        ("FR-075", verify_fr_075),
        ("FR-076", verify_fr_076),
        ("FR-077", verify_fr_077),
        ("FR-078", verify_fr_078),
        ("FR-079", verify_fr_079),
        ("FR-080", verify_fr_080),
        ("FR-081", verify_fr_081),
    ]

    for code, fn in tests:
        try:
            fn()
            print(f"  [PASS] {code} verified.")
        except AssertionError as ae:
            print(f"  [FAIL] {code}: {ae}")
            raise ae

    print("All Action Engine self tests completed successfully!")


if __name__ == "__main__":
    run_self_tests()
