# uawos_planning.py
import uawos_db
import os
import json
import time

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_planning_state.json")

def get_default_state() -> dict:
    return {
        "plans": {
            "PLN-101": {
                "id": "PLN-101",
                "objective_id": "OBJ-101",
                "title": "Optimized Cache and Funnel Refactor Plan",
                "steps": ["Step 1: DB Query refactoring", "Step 2: Add cache headers", "Step 3: Setup conversion metrics"],
                "cost_estimate": 345.50,
                "duration_estimate": 7,  # days
                "resource_requirements": ["Database Expert", "Frontend Dev"],
                "success_probability": 0.95,
                "status": "approved",
                "version": 1,
                "history": [],
                "risks": ["Database downtime during index build"],
                "assumptions": ["Redis cache is available and running"],
                "is_alternative": False
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
                "is_alternative": True
            }
        }
    }

def load_state() -> dict:
    if uawos_db.DB_AVAILABLE:
        try:
            state = uawos_db.db_load_plans()
            if state and state.get("plans"):
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
            uawos_db.db_save_all_plans(state.get("plans", {}))
        except Exception as e:
            print(f"PostgreSQL save failed: {e}")
# Core API
def create_plan(
    objective_id: str,
    title: str,
    steps: list,
    cost_estimate: float,
    duration_estimate: int,
    resource_requirements: list,
    success_probability: float,
    risks: list = None,
    assumptions: list = None,
    is_alternative: bool = False
) -> dict:
    """Create a new plan. Enforces UCA Law 3 (No plan without an objective)."""
    state = load_state()
    
    # Enforce Law 3
    if not objective_id:
        raise ValueError("Constitutional Law 3 Violation: Plan must be linked to an Objective ID.")
        
    existing_ids = [int(k[4:]) for k in state["plans"].keys() if k.startswith("PLN-") and k[4:].isdigit()]
    next_id_num = max(existing_ids) + 1 if existing_ids else 201
    plan_id = f"PLN-{next_id_num}"
    
    plan = {
        "id": plan_id,
        "objective_id": objective_id,
        "title": title,
        "steps": steps,
        "cost_estimate": cost_estimate,  # FR-046
        "duration_estimate": duration_estimate,  # FR-047
        "resource_requirements": resource_requirements,  # FR-048
        "success_probability": success_probability,  # FR-045
        "status": "draft",
        "version": 1,  # FR-054
        "history": [],
        "risks": risks or ["General delivery risk"],  # FR-049
        "assumptions": assumptions or ["Required resources are available"],  # FR-050
        "is_alternative": is_alternative  # FR-056
    }
    
    state["plans"][plan_id] = plan
    save_state(state)
    return state["plans"][plan_id]

# FR-041 & FR-042: Automatic plan generation
def generate_plans(objective_id: str) -> list:
    """Automatically generate multiple plans for an objective."""
    p1 = create_plan(
        objective_id=objective_id,
        title=f"Plan A for {objective_id} (Optimized)",
        steps=["Step A1: Basic deployment", "Step A2: Verify"],
        cost_estimate=200.0,
        duration_estimate=5,
        resource_requirements=["Dev Agent"],
        success_probability=0.90,
        is_alternative=False
    )
    p2 = create_plan(
        objective_id=objective_id,
        title=f"Plan B for {objective_id} (Extended)",
        steps=["Step B1: Full regression tests", "Step B2: Canary deployment"],
        cost_estimate=450.0,
        duration_estimate=12,
        resource_requirements=["Dev Agent", "QA Agent"],
        success_probability=0.98,
        is_alternative=True
    )
    return [p1, p2]

# FR-043: Rank plans
def rank_plans(objective_id: str) -> list:
    """Rank plans descending based on a composite score of probability, cost, and duration."""
    state = load_state()
    plans = [p for p in state["plans"].values() if p["objective_id"] == objective_id]
    
    def score_plan(p):
        # High success probability is good, low cost is good, low duration is good
        prob = p["success_probability"]
        cost = p["cost_estimate"]
        dur = p["duration_estimate"]
        return prob * 100 - (cost / 10.0) - dur
        
    plans.sort(key=score_plan, reverse=True)
    return [p["id"] for p in plans]

# FR-044: Simulate plan
def simulate_plan(plan_id: str) -> dict:
    """Simulate execution pathway to predict success, cost, and duration shifts."""
    state = load_state()
    plan = state["plans"].get(plan_id)
    if not plan:
        raise ValueError(f"Plan {plan_id} not found.")
        
    # Heuristic simulation: shift metrics slightly to model risk
    success_probability = round(plan["success_probability"] * 0.98, 2)
    cost = round(plan["cost_estimate"] * 1.05, 2)
    duration = plan["duration_estimate"] + 1
    
    return {
        "plan_id": plan_id,
        "simulated_success_probability": success_probability,
        "simulated_cost": cost,
        "simulated_duration": duration,
        "verdict": "Within acceptable limits" if success_probability > 0.7 else "High risk"
    }

# FR-057: Plan comparison
def compare_plans(plan_id_1: str, plan_id_2: str) -> dict:
    state = load_state()
    p1 = state["plans"].get(plan_id_1)
    p2 = state["plans"].get(plan_id_2)
    if not p1 or not p2:
        raise ValueError("One or both plans not found.")
        
    return {
        "compared": [plan_id_1, plan_id_2],
        "cost_difference": p1["cost_estimate"] - p2["cost_estimate"],
        "duration_difference": p1["duration_estimate"] - p2["duration_estimate"],
        "success_probability_difference": p1["success_probability"] - p2["success_probability"]
    }

# FR-051 to FR-053: Lifecycle Transitions
def approve_plan(plan_id: str) -> dict:
    return modify_plan(plan_id, {"status": "approved"})

def reject_plan(plan_id: str) -> dict:
    return modify_plan(plan_id, {"status": "rejected"})

def archive_plan(plan_id: str) -> dict:
    return modify_plan(plan_id, {"status": "archived"})

def modify_plan(plan_id: str, updates: dict) -> dict:
    """Modify a plan and increment its version (FR-052, FR-054)."""
    state = load_state()
    plan = state["plans"].get(plan_id)
    if not plan:
        raise ValueError(f"Plan {plan_id} not found.")
        
    # Save to history
    snap = {k: v for k, v in plan.items() if k != "history"}
    plan["history"].append({
        "timestamp": time.time(),
        "state": snap
    })
    
    for k, v in updates.items():
        if k in ["title", "steps", "cost_estimate", "duration_estimate", "resource_requirements", "success_probability", "status", "risks", "assumptions"]:
            plan[k] = v
            
    plan["version"] += 1
    state["plans"][plan_id] = plan
    save_state(state)
    return state["plans"][plan_id]

# FR-058 & FR-059: Automatic and governance-driven replanning
def trigger_replanning(objective_id: str, reason: str) -> dict:
    """Replanning triggers creation of a new draft plan with updated criteria."""
    state = load_state()
    active_plans = [p for p in state["plans"].values() if p["objective_id"] == objective_id and p["status"] == "approved"]
    
    for ap in active_plans:
        modify_plan(ap["id"], {"status": "archived"})
        
    # Generate new plan
    new_plan = create_plan(
        objective_id=objective_id,
        title=f"Replanned strategy due to: {reason}",
        steps=["Step R1: Address constraints", "Step R2: Resume execution"],
        cost_estimate=250.0,
        duration_estimate=6,
        resource_requirements=["Replanning Agent"],
        success_probability=0.92
    )
    return new_plan

# FR-060: Traceability
def get_planning_traceability(plan_id: str) -> dict:
    state = load_state()
    plan = state["plans"].get(plan_id)
    if not plan:
        raise ValueError(f"Plan {plan_id} not found.")
    return {
        "plan_id": plan_id,
        "objective_id": plan["objective_id"],
        "traceability_chain": f"OBJ -> {plan['objective_id']} -> PLAN -> {plan_id} -> STEPS -> {', '.join(plan['steps'])}"
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
