# uawos_workflow.py
import os
import time

import uawos_db
from uawos_state_utils import load_state, save_state

from application.use_cases.workflow_use_cases import (
    create_workflow,
    generate_workflow,
    modify_workflow,
    pause_workflow,
    resume_workflow,
    terminate_workflow,
    simulate_workflow,
    execute_workflow,
    optimize_workflow,
    check_temporal_worker_queues,
)

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_workflow_state.json")


def get_default_state() -> dict:
    return {
        "workflows": {
            "WRK-101": {
                "id": "WRK-101",
                "plan_id": "PLN-101",
                "title": "Optimized Funnel Refactor Workflow",
                "tasks": [
                    "DB Index Setup",
                    "Cache Configuration",
                    "Verification Tests",
                ],
                "dependencies": [],
                "state": "active",  # active, paused, terminated, completed
                "version": 1,
                "history": [],
                "governed": True,
            }
        }
    }


# ----------------- VERIFICATION TESTS (FR-061 to FR-070) -----------------


def verify_fr_061():
    wf = generate_workflow("PLN-101")
    assert wf["id"].startswith("WRK-"), "Workflow generation failed."
    return True


def verify_fr_062():
    wf = modify_workflow("WRK-101", {"title": "Updated Workflow Title"})
    assert wf["version"] >= 2, "Workflow versioning failed."
    return True


def verify_fr_063():
    wf = load_state()["workflows"]["WRK-101"]
    assert wf["state"] in [
        "active",
        "paused",
        "terminated",
        "completed",
    ], "Workflow state invalid."
    return True


def verify_fr_064():
    wf = create_workflow("PLN-101", "T", ["task"], dependencies=["WRK-101"])
    assert "WRK-101" in wf["dependencies"], "Workflow dependencies failed."
    return True


def verify_fr_065():
    wf = create_workflow("PLN-101", "T", ["task"], governed=True)
    assert wf["governed"] is True, "Workflow governance failed."
    return True


def verify_fr_066():
    sim = simulate_workflow("WRK-101")
    assert "estimated_duration_seconds" in sim, "Workflow simulation failed."
    exec_wf = execute_workflow("WRK-101")
    assert exec_wf["state"] == "active", "Workflow execution failed."
    assert "execution_mode" in exec_wf, "Execution mode missing."
    return True


def verify_fr_067():
    opt = optimize_workflow("WRK-101")
    assert len(opt["tasks"]) > 0, "Workflow optimization failed."
    return True


def verify_fr_068():
    wf = pause_workflow("WRK-101")
    assert wf["state"] == "paused", "Workflow pause failed."
    return True


def verify_fr_069():
    wf = resume_workflow("WRK-101")
    assert wf["state"] == "active", "Workflow resume failed."
    return True


def verify_fr_070():
    wf = terminate_workflow("WRK-101")
    assert wf["state"] == "terminated", "Workflow termination failed."
    return True


def run_self_tests():
    print("Running Workflow Management self tests...")
    if uawos_db.DB_AVAILABLE:
        try:
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
        except Exception as e:
            print(f"Failed to seed dependencies in self-test setup: {e}")
    state = get_default_state()
    save_state(state)

    tests = [
        ("FR-061", verify_fr_061),
        ("FR-062", verify_fr_062),
        ("FR-063", verify_fr_063),
        ("FR-064", verify_fr_064),
        ("FR-065", verify_fr_065),
        ("FR-066", verify_fr_066),
        ("FR-067", verify_fr_067),
        ("FR-068", verify_fr_068),
        ("FR-069", verify_fr_069),
        ("FR-070", verify_fr_070),
    ]

    for code, fn in tests:
        try:
            fn()
            print(f"  [PASS] {code} verified.")
        except AssertionError as ae:
            print(f"  [FAIL] {code}: {ae}")
            raise ae

    print("All Workflow Engine self tests completed successfully!")


if __name__ == "__main__":
    run_self_tests()
