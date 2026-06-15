# uawos_planning.py
import os
import time

import uawos_db
from uawos_state_utils import load_state, save_state

from application.use_cases.planning_use_cases import (
    create_plan,
    generate_plans,
    rank_plans,
    simulate_plan,
    compare_plans,
    approve_plan,
    reject_plan,
    archive_plan,
    modify_plan,
    trigger_replanning,
    get_planning_traceability,
    route_action_to_agent,
)

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_planning_state.json")


def get_default_state() -> dict:
    return {
        "plans": {
            "PLN-101": {
                "id": "PLN-101",
                "objective_id": "OBJ-101",
                "title": "Optimized Cache and Funnel Refactor Plan",
                "steps": [
                    "Step 1: DB Query refactoring",
                    "Step 2: Add cache headers",
                    "Step 3: Setup conversion metrics",
                ],
                "cost_estimate": 345.50,
                "duration_estimate": 7,  # days
                "resource_requirements": ["Database Expert", "Frontend Dev"],
                "success_probability": 0.95,
                "status": "approved",
                "version": 1,
                "history": [],
                "risks": ["Database downtime during index build"],
                "assumptions": ["Redis cache is available and running"],
                "is_alternative": False,
            },
            "PLN-102": {
                "id": "PLN-102",
                "objective_id": "OBJ-101",
                "title": "Full Funnel Rebuild Plan (Alternative)",
                "steps": ["Step 1: Build brand new React checkout page", "Step 2: Migrate payment gateway"],
                "cost_estimate": 1500.00,
                "duration_estimate": 21,
                "resource_requirements": ["React Developer", "QA Engineer", "Architect"],
                "success_probability": 0.80,
                "status": "draft",
                "version": 1,
                "history": [],
                "risks": ["High integration overhead", "High regression risk"],
                "assumptions": ["API specs remain unchanged"],
                "is_alternative": True,
            },
        }
    }


# ----------------- VERIFICATION TESTS (FR-041 to FR-060) -----------------


def verify_fr_041():
    plans = generate_plans("OBJ-101")
    assert len(plans) > 0, "No plans generated."
    return True


def verify_fr_042():
    plans = generate_plans("OBJ-101")
    assert len(plans) >= 2, "Multiple plans should be generated."
    return True


def verify_fr_043():
    ranked = rank_plans("OBJ-101")
    assert len(ranked) > 0, "Ranking failed."
    return True


def verify_fr_044():
    sim = simulate_plan("PLN-101")
    assert "simulated_cost" in sim, "Simulation failed."
    return True


def verify_fr_045():
    sim = simulate_plan("PLN-101")
    assert sim["simulated_success_probability"] > 0, "Success estimation failed."
    return True


def verify_fr_046():
    plan = create_plan("OBJ-101", "T", ["step"], 150.0, 5, ["Dev"], 0.9)
    assert plan["cost_estimate"] == 150.0, "Cost estimate failed."
    return True


def verify_fr_047():
    plan = create_plan("OBJ-101", "T", ["step"], 150.0, 5, ["Dev"], 0.9)
    assert plan["duration_estimate"] == 5, "Duration estimate failed."
    return True


def verify_fr_048():
    plan = create_plan("OBJ-101", "T", ["step"], 150.0, 5, ["Dev"], 0.9)
    assert "Dev" in plan["resource_requirements"], "Resource requirements failed."
    return True


def verify_fr_049():
    plan = create_plan("OBJ-101", "T", ["step"], 150.0, 5, ["Dev"], 0.9, risks=["Risk X"])
    assert "Risk X" in plan["risks"], "Risks identification failed."
    return True


def verify_fr_050():
    plan = create_plan("OBJ-101", "T", ["step"], 150.0, 5, ["Dev"], 0.9, assumptions=["Assump X"])
    assert "Assump X" in plan["assumptions"], "Assumptions identification failed."
    return True


def verify_fr_051():
    plan = approve_plan("PLN-102")
    assert plan["status"] == "approved", "Approval failed."
    return True


def verify_fr_052():
    plan = modify_plan("PLN-101", {"title": "Updated Plan title"})
    assert plan["title"] == "Updated Plan title", "Modification failed."
    return True


def verify_fr_053():
    plan = reject_plan("PLN-101")
    assert plan["status"] == "rejected", "Rejection failed."
    return True


def verify_fr_054():
    plan = modify_plan("PLN-101", {"title": "New Mod Title"})
    assert plan["version"] >= 2, "Versioning failed."
    return True


def verify_fr_055():
    plan = archive_plan("PLN-101")
    assert plan["status"] == "archived", "Archival failed."
    return True


def verify_fr_056():
    plans = generate_plans("OBJ-101")
    assert any(p["is_alternative"] for p in plans), "Alternative plans not supported."
    return True


def verify_fr_057():
    comp = compare_plans("PLN-101", "PLN-102")
    assert "cost_difference" in comp, "Comparison failed."
    return True


def verify_fr_058():
    rp = trigger_replanning("OBJ-101", "System Drift")
    assert "Replanned strategy" in rp["title"], "Replanning failed."
    return True


def verify_fr_059():
    rp = trigger_replanning("OBJ-101", "Governance Cost Warning")
    assert "Replanned strategy" in rp["title"], "Governance replanning failed."
    return True


def verify_fr_060():
    trace = get_planning_traceability("PLN-101")
    assert "traceability_chain" in trace, "Traceability failed."
    return True


def run_self_tests():
    print("Running Planning Engine self tests...")
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
        except Exception as e:
            print(f"Failed to seed objective OBJ-101: {e}")
    state = get_default_state()
    save_state(state)

    tests = [
        ("FR-041", verify_fr_041),
        ("FR-042", verify_fr_042),
        ("FR-043", verify_fr_043),
        ("FR-044", verify_fr_044),
        ("FR-045", verify_fr_045),
        ("FR-046", verify_fr_046),
        ("FR-047", verify_fr_047),
        ("FR-048", verify_fr_048),
        ("FR-049", verify_fr_049),
        ("FR-050", verify_fr_050),
        ("FR-051", verify_fr_051),
        ("FR-052", verify_fr_052),
        ("FR-053", verify_fr_053),
        ("FR-054", verify_fr_054),
        ("FR-055", verify_fr_055),
        ("FR-056", verify_fr_056),
        ("FR-057", verify_fr_057),
        ("FR-058", verify_fr_058),
        ("FR-059", verify_fr_059),
        ("FR-060", verify_fr_060),
    ]

    for code, fn in tests:
        try:
            fn()
            print(f"  [PASS] {code} verified.")
        except AssertionError as ae:
            print(f"  [FAIL] {code}: {ae}")
            raise ae

    print("All Planning Engine self tests completed successfully!")


if __name__ == "__main__":
    run_self_tests()
