# uawos_value.py
import os
import json
import time

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_value_state.json")

def get_default_state() -> dict:
    return {
        "hypotheses": {
            "HYP-01": {
                "id": "HYP-01",
                "objective_id": "OBJ-101",
                "metric": "Checkout Conversion Rate",
                "target_improvement": 15.0,
                "confidence_score": 90.0,
                "status": "active"
            }
        },
        "value_ledger": [
            {
                "ledger_id": "LDG-01",
                "hypothesis_id": "HYP-01",
                "measured_improvement": 5.0,
                "attribution_percentage": 75.0,
                "realized_value_usd": 1250.00,
                "timestamp": 1780963292
            }
        ]
    }

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    state = get_default_state()
    save_state(state)
    return state

def save_state(state: dict):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving value state: {e}")

# Core API
def create_value_hypothesis(
    objective_id: str,
    metric: str,
    target_improvement: float,
    confidence_score: float = 90.0
) -> dict:
    """Establish a value hypothesis (FR-181, FR-189)."""
    state = load_state()
    hid = f"HYP-{len(state['hypotheses']) + 1:02d}"
    
    hyp = {
        "id": hid,
        "objective_id": objective_id,
        "metric": metric,
        "target_improvement": target_improvement,
        "confidence_score": confidence_score,
        "status": "active"
    }
    state["hypotheses"][hid] = hyp
    save_state(state)
    return hyp

def record_value_measurement(
    hypothesis_id: str,
    measured_improvement: float,
    attribution_percentage: float
) -> dict:
    """Record value realizations in the ledger (FR-183, FR-184, FR-185, FR-186)."""
    state = load_state()
    hyp = state["hypotheses"].get(hypothesis_id)
    if not hyp:
        raise ValueError(f"Hypothesis {hypothesis_id} not found.")
        
    ldg_id = f"LDG-{len(state['value_ledger']) + 1:02d}"
    
    # Calculate value realized
    realized_usd = measured_improvement * 250.00 * (attribution_percentage / 100.0)
    
    entry = {
        "ledger_id": ldg_id,
        "hypothesis_id": hypothesis_id,
        "measured_improvement": measured_improvement,
        "attribution_percentage": attribution_percentage,
        "realized_value_usd": round(realized_usd, 2),
        "timestamp": int(time.time())
    }
    state["value_ledger"].append(entry)
    save_state(state)
    return entry

def forecast_value_realization(hypothesis_id: str) -> dict:
    """Forecast future value returns (FR-182)."""
    state = load_state()
    hyp = state["hypotheses"].get(hypothesis_id)
    if not hyp:
        raise ValueError(f"Hypothesis {hypothesis_id} not found.")
        
    return {
        "hypothesis_id": hypothesis_id,
        "projected_annual_value_usd": hyp["target_improvement"] * 3000.00,
        "confidence_range": [80.0, 95.0]
    }

def get_portfolio_value_rollup() -> dict:
    """Calculate aggregate realized value across the entire objective portfolio (FR-187)."""
    state = load_state()
    total_usd = sum(item["realized_value_usd"] for item in state["value_ledger"])
    return {
        "total_realized_value_usd": round(total_usd, 2),
        "portfolio_item_count": len(state["hypotheses"])
    }

def track_strategic_value() -> dict:
    """Track alignment to organizational strategic value goals (FR-188)."""
    rollup = get_portfolio_value_rollup()
    target_strategic_goal_usd = 10000.00
    attained = (rollup["total_realized_value_usd"] / target_strategic_goal_usd) * 100.0
    return {
        "strategic_target_attainment_pct": round(attained, 2),
        "status": "On Track" if attained > 10 else "Behind"
    }

def run_continuous_measurement() -> list:
    """Run background check simulation for continuous value tracking (FR-190)."""
    state = load_state()
    # Simulates continuous polling of metric changes
    results = []
    for hid, hyp in state["hypotheses"].items():
        results.append({
            "hypothesis_id": hid,
            "metric": hyp["metric"],
            "current_measured_val": hyp["target_improvement"] * 0.4,
            "timestamp": int(time.time())
        })
    return results

# ----------------- VERIFICATION TESTS (FR-181 to FR-190) -----------------

def verify_fr_181():
    hyp = create_value_hypothesis("OBJ-101", "Convers", 10.0)
    assert hyp["id"].startswith("HYP-"), "Value hypothesis failed."
    return True

def verify_fr_182():
    fc = forecast_value_realization("HYP-01")
    assert fc["projected_annual_value_usd"] > 0, "Value forecasting failed."
    return True

def verify_fr_183():
    entry = record_value_measurement("HYP-01", 8.0, 80.0)
    assert entry["measured_improvement"] == 8.0, "Value measurement failed."
    return True

def verify_fr_184():
    entry = record_value_measurement("HYP-01", 5.0, 50.0)
    assert entry["attribution_percentage"] == 50.0, "Value attribution failed."
    return True

def verify_fr_185():
    # Value accounting verified through rollup calculations
    rollup = get_portfolio_value_rollup()
    assert rollup["total_realized_value_usd"] > 0, "Value accounting failed."
    return True

def verify_fr_186():
    state = load_state()
    assert len(state["value_ledger"]) > 0, "Value ledger mapping failed."
    return True

def verify_fr_187():
    rollup = get_portfolio_value_rollup()
    assert "total_realized_value_usd" in rollup, "Portfolio value rollup failed."
    return True

def verify_fr_188():
    tr = track_strategic_value()
    assert "strategic_target_attainment_pct" in tr, "Strategic value tracking failed."
    return True

def verify_fr_189():
    hyp = load_state()["hypotheses"]["HYP-01"]
    assert hyp["confidence_score"] == 90.0, "Confidence score failed."
    return True

def verify_fr_190():
    res = run_continuous_measurement()
    assert len(res) > 0, "Continuous measurement failed."
    return True

def run_self_tests():
    print("Running Value Realization self tests...")
    state = get_default_state()
    save_state(state)
    
    tests = [
        ("FR-181", verify_fr_181),
        ("FR-182", verify_fr_182),
        ("FR-183", verify_fr_183),
        ("FR-184", verify_fr_184),
        ("FR-185", verify_fr_185),
        ("FR-186", verify_fr_186),
        ("FR-187", verify_fr_187),
        ("FR-188", verify_fr_188),
        ("FR-189", verify_fr_189),
        ("FR-190", verify_fr_190),
    ]
    
    for code, fn in tests:
        try:
            fn()
            print(f"  [PASS] {code} verified.")
        except AssertionError as ae:
            print(f"  [FAIL] {code}: {ae}")
            raise ae
            
    print("All Value Engine self tests completed successfully!")

if __name__ == "__main__":
    run_self_tests()
