# uawos_outcome.py
import uawos_db
import os
import json
import time

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_outcome_state.json")

def get_default_state() -> dict:
    return {
        "outcomes": {
            "OUT-101": {
                "id": "OUT-101",
                "objective_id": "OBJ-101",
                "title": "Increase checkout conversion rate by 15%",
                "metric": "Checkout Conversion Rate",
                "unit": "percent",
                "weight": 0.6,
                "dependencies": [],
                "confidence_score": 90.0,
                "owner": "Product Owner",
                "baseline_state": 70.0,
                "target_state": 85.0,
                "current_state": 75.0,
                "forecasted_state": 83.5
            },
            "OUT-102": {
                "id": "OUT-102",
                "objective_id": "OBJ-101",
                "title": "Reduce shipping fee complaints by 50%",
                "metric": "Shipping Complaints Volume",
                "unit": "count/day",
                "weight": 0.4,
                "dependencies": ["OUT-101"],
                "confidence_score": 85.0,
                "owner": "Product Owner",
                "baseline_state": 20.0,
                "target_state": 10.0,
                "current_state": 18.0,
                "forecasted_state": 12.0
            }
        }
    }

def load_state() -> dict:
    if uawos_db.DB_AVAILABLE:
        try:
            state = uawos_db.db_load_outcomes()
            if state and state.get("outcomes"):
                with open(STATE_FILE, "w") as f:
                    json.dump(state, f, indent=2)
                return state
        except Exception as e:
            print(f"PostgreSQL load failed, falling back: {e}")

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
        print(f"Error saving local state cache: {e}")
    if uawos_db.DB_AVAILABLE:
        try:
            uawos_db.db_save_all_outcomes(state.get("outcomes", {}))
        except Exception as e:
            print(f"PostgreSQL save failed: {e}")
# Core API for creating Outcomes
def create_outcome(
    objective_id: str,
    title: str,
    metric: str,
    unit: str,
    weight: float = 1.0,
    baseline_state: float = 0.0,
    target_state: float = 100.0,
    owner: str = "System Agent",
    dependencies: list = None,
    confidence_score: float = 100.0,
    current_state: float = None
) -> dict:
    """Create a measurable outcome (FR-031, FR-032)."""
    state = load_state()
    
    # Enforce measurable requirements (FR-031)
    if not metric or not unit:
        raise ValueError("Measurable Outcomes require a defined metric and unit.")
        
    existing_ids = [int(k[4:]) for k in state["outcomes"].keys() if k.startswith("OUT-") and k[4:].isdigit()]
    next_id_num = max(existing_ids) + 1 if existing_ids else 201
    outcome_id = f"OUT-{next_id_num}"
    
    if dependencies is None:
        dependencies = []
    if current_state is None:
        current_state = baseline_state
        
    outcome = {
        "id": outcome_id,
        "objective_id": objective_id,
        "title": title,
        "metric": metric,
        "unit": unit,
        "weight": weight,  # FR-033
        "dependencies": dependencies,  # FR-034
        "confidence_score": confidence_score,  # FR-035
        "owner": owner,  # FR-037
        "baseline_state": baseline_state,  # FR-038
        "target_state": target_state,  # FR-039
        "current_state": current_state,  # FR-040
        "forecasted_state": current_state  # FR-036
    }
    
    state["outcomes"][outcome_id] = outcome
    save_state(state)
    recalculate_forecasts(outcome_id)
    return load_state()["outcomes"][outcome_id]

def get_objective_outcomes(objective_id: str) -> list:
    """Get all outcomes associated with a specific objective (FR-032)."""
    state = load_state()
    return [out for out in state["outcomes"].values() if out["objective_id"] == objective_id]

def update_outcome(outcome_id: str, updates: dict) -> dict:
    state = load_state()
    outcome = state["outcomes"].get(outcome_id)
    if not outcome:
        raise ValueError(f"Outcome {outcome_id} not found.")
        
    for k, v in updates.items():
        if k in ["title", "metric", "unit", "weight", "dependencies", "confidence_score", "owner", "baseline_state", "target_state", "current_state"]:
            outcome[k] = v
            
    state["outcomes"][outcome_id] = outcome
    save_state(state)
    recalculate_forecasts(outcome_id)
    return load_state()["outcomes"][outcome_id]

def recalculate_forecasts(outcome_id: str):
    """Estimate outcome forecasting based on progress trends (FR-036)."""
    state = load_state()
    outcome = state["outcomes"].get(outcome_id)
    if not outcome:
        return
        
    # Heuristic forecasting: project current progress slightly forward
    base = outcome["baseline_state"]
    curr = outcome["current_state"]
    target = outcome["target_state"]
    
    diff = target - base
    progress = curr - base
    
    if diff == 0:
        forecast = target
    else:
        # Forecast 10% progress increment as estimate
        ratio = progress / diff
        forecast = base + diff * min(1.0, ratio + 0.1)
        
    outcome["forecasted_state"] = round(forecast, 2)
    state["outcomes"][outcome_id] = outcome
    save_state(state)

# ----------------- VERIFICATION TESTS (FR-031 to FR-040) -----------------

def verify_fr_031():
    """Verify system requires measurable outcomes."""
    try:
        create_outcome("OBJ-101", "Invalid Outcome", "", "") # Missing metric/unit
        assert False, "Should have raised ValueError for missing metric/unit."
    except ValueError:
        pass
    return True

def verify_fr_032():
    """Verify system supports multiple outcomes per objective."""
    outcomes = get_objective_outcomes("OBJ-101")
    assert len(outcomes) >= 2, "Should support multiple outcomes per objective."
    return True

def verify_fr_033():
    """Verify system supports outcome weighting."""
    out = create_outcome("OBJ-101", "Weighted Outcome", "Conversion Rate", "percent", weight=0.75)
    assert out["weight"] == 0.75, "Outcome weight not preserved."
    return True

def verify_fr_034():
    """Verify system supports outcome dependencies."""
    out = create_outcome("OBJ-101", "Dependent Outcome", "Conversion Rate", "percent", dependencies=["OUT-101"])
    assert "OUT-101" in out["dependencies"], "Outcome dependency not preserved."
    return True

def verify_fr_035():
    """Verify system supports outcome confidence scores."""
    out = create_outcome("OBJ-101", "Confident Outcome", "Conversion Rate", "percent", confidence_score=88.5)
    assert out["confidence_score"] == 88.5, "Outcome confidence score not preserved."
    return True

def verify_fr_036():
    """Verify system supports outcome forecasting."""
    out = create_outcome("OBJ-101", "Forecasted Outcome", "Click rate", "ratio", baseline_state=0.0, target_state=100.0, current_state=50.0)
    assert out["forecasted_state"] > 50.0, "Outcome forecast not calculated."
    return True

def verify_fr_037():
    """Verify system supports outcome ownership."""
    out = create_outcome("OBJ-101", "Owned Outcome", "Conversion Rate", "percent", owner="Design Lead")
    assert out["owner"] == "Design Lead", "Outcome owner not preserved."
    return True

def verify_fr_038():
    """Verify system supports outcome baselines."""
    out = create_outcome("OBJ-101", "Baseline Outcome", "Conversion Rate", "percent", baseline_state=12.5)
    assert out["baseline_state"] == 12.5, "Outcome baseline not preserved."
    return True

def verify_fr_039():
    """Verify system supports outcome target states."""
    out = create_outcome("OBJ-101", "Target Outcome", "Conversion Rate", "percent", target_state=95.0)
    assert out["target_state"] == 95.0, "Outcome target state not preserved."
    return True

def verify_fr_040():
    """Verify system supports outcome current states."""
    out = create_outcome("OBJ-101", "Current State Outcome", "Conversion Rate", "percent", baseline_state=0.0, target_state=100.0, current_state=42.0)
    assert out["current_state"] == 42.0, "Outcome current state not preserved."
    return True

def run_self_tests():
    print("Running Outcome Management self tests...")
    if uawos_db.DB_AVAILABLE:
        try:
            uawos_db.db_save_objective({
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
                "history": []
            })
        except Exception as e:
            print(f"Failed to seed objective OBJ-101: {e}")
    state = get_default_state()
    save_state(state)
    
    tests = [
        ("FR-031", verify_fr_031),
        ("FR-032", verify_fr_032),
        ("FR-033", verify_fr_033),
        ("FR-034", verify_fr_034),
        ("FR-035", verify_fr_035),
        ("FR-036", verify_fr_036),
        ("FR-037", verify_fr_037),
        ("FR-038", verify_fr_038),
        ("FR-039", verify_fr_039),
        ("FR-040", verify_fr_040),
    ]
    
    for code, fn in tests:
        try:
            fn()
            print(f"  [PASS] {code} verified.")
        except AssertionError as ae:
            print(f"  [FAIL] {code}: {ae}")
            raise ae
            
    print("All Outcome Engine self tests completed successfully!")

if __name__ == "__main__":
    run_self_tests()
