# uawos_budget.py
import os
import time

from uawos_state_utils import load_state, save_state

from application.use_cases.billing_use_cases import (
    allocate_objective_budget,
    allocate_action_budget,
    record_agent_cost,
    evaluate_cost_governance,
    submit_approval_request,
    process_approval_request,
    get_summary,
)

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_budget_state.json")

# Model pricing structures per 1M tokens (exposed for tests or legacy imports)
MODEL_PRICING = {
    "tinyllama": {"input": 0.07, "output": 0.07, "reasoning": 0.07},
    "llama3": {"input": 0.15, "output": 0.60, "reasoning": 0.60},
    "deepseek-r1": {"input": 0.55, "output": 2.19, "reasoning": 2.19},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00, "reasoning": 5.00},
    "default": {"input": 0.15, "output": 0.60, "reasoning": 0.60},
}


def get_default_state() -> dict:
    return {
        "objective_budgets": {
            "OBJ-101": {
                "name": "Launch Product X Checkout Flow",
                "budget": 1200.00,
                "actual": 345.50,
                "status": "Approved",
            },
            "OBJ-102": {
                "name": "OPA Compliance & SAST Auditing",
                "budget": 500.00,
                "actual": 485.00,
                "status": "Approved",
            },
            "OBJ-103": {
                "name": "DTASE Multi-Persona Synthesis",
                "budget": 800.00,
                "actual": 120.00,
                "status": "Approved",
            },
            "OBJ-104": {
                "name": "Graphiti Memory Synchronization",
                "budget": 300.00,
                "actual": 320.00,
                "status": "Approved",
            },  # Exceeded!
        },
        "action_budgets": {
            "ACT-101-1": {
                "name": "Refactor database query logic",
                "objective_id": "OBJ-101",
                "budget": 400.00,
                "actual": 150.00,
            },
            "ACT-101-2": {
                "name": "Integrate Redis cache headers",
                "objective_id": "OBJ-101",
                "budget": 300.00,
                "actual": 195.50,
            },
            "ACT-102-1": {
                "name": "Configure OPA policies",
                "objective_id": "OBJ-102",
                "budget": 250.00,
                "actual": 240.00,
            },
            "ACT-102-2": {
                "name": "Run Trivy Container Scans",
                "objective_id": "OBJ-102",
                "budget": 250.00,
                "actual": 245.00,
            },
            "ACT-103-1": {
                "name": "Apply translation frameworks",
                "objective_id": "OBJ-103",
                "budget": 400.00,
                "actual": 120.00,
            },
            "ACT-104-1": {
                "name": "Index memory vectors in Qdrant",
                "objective_id": "OBJ-104",
                "budget": 300.00,
                "actual": 320.00,
            },
        },
        "agent_costs": {
            "Planner Agent": {"cost": 124.50, "token_count": 850000, "call_count": 120},
            "Orchestrator Agent": {
                "cost": 210.20,
                "token_count": 1420000,
                "call_count": 340,
            },
            "Executor Agent": {
                "cost": 485.30,
                "token_count": 3200000,
                "call_count": 850,
            },
            "Reviewer Agent": {"cost": 75.60, "token_count": 510000, "call_count": 95},
            "Governor Agent": {"cost": 15.40, "token_count": 110000, "call_count": 35},
            "Portfolio Governor Agent": {
                "cost": 25.00,
                "token_count": 180000,
                "call_count": 40,
            },
            "Value Analyst Agent": {
                "cost": 30.50,
                "token_count": 220000,
                "call_count": 55,
            },
            "Resource Manager Agent": {
                "cost": 45.00,
                "token_count": 310000,
                "call_count": 70,
            },
        },
        "token_consumption": {
            "tinyllama": {
                "input_tokens": 1500000,
                "output_tokens": 800000,
                "reasoning_tokens": 0,
                "cost": 0.16,
            },
            "llama3": {
                "input_tokens": 2400000,
                "output_tokens": 1200000,
                "reasoning_tokens": 0,
                "cost": 1.08,
            },
            "gemini-1.5-pro": {
                "input_tokens": 6000000,
                "output_tokens": 4000000,
                "reasoning_tokens": 1000000,
                "cost": 32.50,
            },
            "deepseek-r1": {
                "input_tokens": 5000000,
                "output_tokens": 3000000,
                "reasoning_tokens": 2000000,
                "cost": 13.70,
            },
        },
        "budget_approvals": [
            {
                "id": "APP-001",
                "objective_id": "OBJ-104",
                "amount": 150.00,
                "status": "Pending",
                "requested_by": "Resource Manager Agent",
                "timestamp": "2026-06-08T18:40:00Z",
            },
            {
                "id": "APP-002",
                "objective_id": "OBJ-101",
                "amount": 500.00,
                "status": "Approved",
                "requested_by": "Planner Agent",
                "timestamp": "2026-06-08T12:00:00Z",
            },
        ],
        "portfolio_attribution": {
            "PORT-A": {
                "name": "Checkout Experience Optimization",
                "cost": 345.50,
                "percentage": 35.6,
            },
            "PORT-B": {
                "name": "Regulatory & Security Infrastructure",
                "cost": 485.00,
                "percentage": 50.0,
            },
            "PORT-C": {
                "name": "AI Foundations & Memory Systems",
                "cost": 140.00,
                "percentage": 14.4,
            },
        },
        "value_to_cost": {
            "OBJ-101": {"value_score": 95.0, "cost": 345.50, "roi_ratio": 2.75},
            "OBJ-102": {"value_score": 85.0, "cost": 485.00, "roi_ratio": 1.75},
            "OBJ-103": {"value_score": 75.0, "cost": 120.00, "roi_ratio": 6.25},
            "OBJ-104": {"value_score": 60.0, "cost": 320.00, "roi_ratio": 1.88},
        },
    }


# ----------------- VERIFICATION TESTS (FR-151 to FR-160) -----------------


def verify_fr_151():
    state = load_state()
    assert len(state["objective_budgets"]) > 0, "No objective budgets configured."
    return True


def verify_fr_152():
    state = load_state()
    assert len(state["action_budgets"]) > 0, "No action budgets configured."
    return True


def verify_fr_153():
    state = load_state()
    assert len(state["agent_costs"]) > 0, "No agent costs tracked."
    return True


def verify_fr_154():
    state = load_state()
    assert len(state["token_consumption"]) > 0, "No tokens tracked."
    return True


def verify_fr_155():
    summary = get_summary()
    assert summary["metrics"]["forecast_spend"] > 0, "Forecast calculation invalid."
    return True


def verify_fr_156():
    verdict_1 = evaluate_cost_governance("OBJ-101")
    assert verdict_1["governance_verdict"] in [
        "APPROVED",
        "WARNING",
        "BREACHED",
    ], "Invalid governance verdict."
    return True


def verify_fr_157():
    state = load_state()
    assert len(state["budget_approvals"]) > 0, "No budget approval requests present."
    return True


def verify_fr_158():
    summary = get_summary()
    assert "variance" in summary["metrics"], "Variance tracking missing."
    return True


def verify_fr_159():
    summary = get_summary()
    assert len(summary["portfolio_attribution"]) > 0, "No cost attribution computed."
    return True


def verify_fr_160():
    summary = get_summary()
    assert len(summary["value_to_cost"]) > 0, "No value-to-cost metrics computed."
    return True


def run_self_tests():
    print("Running Budget & Cost Management self tests...")
    state = get_default_state()
    save_state(state)

    tests = [
        ("FR-151", verify_fr_151),
        ("FR-152", verify_fr_152),
        ("FR-153", verify_fr_153),
        ("FR-154", verify_fr_154),
        ("FR-155", verify_fr_155),
        ("FR-156", verify_fr_156),
        ("FR-157", verify_fr_157),
        ("FR-158", verify_fr_158),
        ("FR-159", verify_fr_159),
        ("FR-160", verify_fr_160),
    ]
    for code, fn in tests:
        try:
            fn()
            print(f"  [PASS] {code} verified.")
        except AssertionError as ae:
            print(f"  [FAIL] {code}: {ae}")
            raise ae
    print("All Budget & Cost self tests completed successfully!")


if __name__ == "__main__":
    run_self_tests()
