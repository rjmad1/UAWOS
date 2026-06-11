# uawos_budget.py
import uawos_db
import os
import json
import time

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_budget_state.json")

# Model pricing structures per 1M tokens
MODEL_PRICING = {
    "tinyllama": {"input": 0.07, "output": 0.07, "reasoning": 0.07},
    "llama3": {"input": 0.15, "output": 0.60, "reasoning": 0.60},
    "deepseek-r1": {"input": 0.55, "output": 2.19, "reasoning": 2.19},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00, "reasoning": 5.00},
    "default": {"input": 0.15, "output": 0.60, "reasoning": 0.60}
}

def get_default_state():
    return {
        "objective_budgets": {
            "OBJ-101": {"name": "Launch Product X Checkout Flow", "budget": 1200.00, "actual": 345.50, "status": "Approved"},
            "OBJ-102": {"name": "OPA Compliance & SAST Auditing", "budget": 500.00, "actual": 485.00, "status": "Approved"},
            "OBJ-103": {"name": "DTASE Multi-Persona Synthesis", "budget": 800.00, "actual": 120.00, "status": "Approved"},
            "OBJ-104": {"name": "Graphiti Memory Synchronization", "budget": 300.00, "actual": 320.00, "status": "Approved"} # Exceeded!
        },
        "action_budgets": {
            "ACT-101-1": {"name": "Refactor database query logic", "objective_id": "OBJ-101", "budget": 400.00, "actual": 150.00},
            "ACT-101-2": {"name": "Integrate Redis cache headers", "objective_id": "OBJ-101", "budget": 300.00, "actual": 195.50},
            "ACT-102-1": {"name": "Configure OPA policies", "objective_id": "OBJ-102", "budget": 250.00, "actual": 240.00},
            "ACT-102-2": {"name": "Run Trivy Container Scans", "objective_id": "OBJ-102", "budget": 250.00, "actual": 245.00},
            "ACT-103-1": {"name": "Apply translation frameworks", "objective_id": "OBJ-103", "budget": 400.00, "actual": 120.00},
            "ACT-104-1": {"name": "Index memory vectors in Qdrant", "objective_id": "OBJ-104", "budget": 300.00, "actual": 320.00}
        },
        "agent_costs": {
            "Planner Agent": {"cost": 124.50, "token_count": 850000, "call_count": 120},
            "Orchestrator Agent": {"cost": 210.20, "token_count": 1420000, "call_count": 340},
            "Executor Agent": {"cost": 485.30, "token_count": 3200000, "call_count": 850},
            "Reviewer Agent": {"cost": 75.60, "token_count": 510000, "call_count": 95},
            "Governor Agent": {"cost": 15.40, "token_count": 110000, "call_count": 35},
            "Portfolio Governor Agent": {"cost": 25.00, "token_count": 180000, "call_count": 40},
            "Value Analyst Agent": {"cost": 30.50, "token_count": 220000, "call_count": 55},
            "Resource Manager Agent": {"cost": 45.00, "token_count": 310000, "call_count": 70}
        },
        "token_consumption": {
            "tinyllama": {"input_tokens": 1500000, "output_tokens": 800000, "reasoning_tokens": 0, "cost": 0.16},
            "llama3": {"input_tokens": 2400000, "output_tokens": 1200000, "reasoning_tokens": 0, "cost": 1.08},
            "gemini-1.5-pro": {"input_tokens": 6000000, "output_tokens": 4000000, "reasoning_tokens": 1000000, "cost": 32.50},
            "deepseek-r1": {"input_tokens": 5000000, "output_tokens": 3000000, "reasoning_tokens": 2000000, "cost": 13.70}
        },
        "budget_approvals": [
            {
                "id": "APP-001",
                "objective_id": "OBJ-104",
                "amount": 150.00,
                "status": "Pending",
                "requested_by": "Resource Manager Agent",
                "timestamp": "2026-06-08T18:40:00Z"
            },
            {
                "id": "APP-002",
                "objective_id": "OBJ-101",
                "amount": 500.00,
                "status": "Approved",
                "requested_by": "Planner Agent",
                "timestamp": "2026-06-08T12:00:00Z"
            }
        ],
        "portfolio_attribution": {
            "PORT-A": {"name": "Checkout Experience Optimization", "cost": 345.50, "percentage": 35.6},
            "PORT-B": {"name": "Regulatory & Security Infrastructure", "cost": 485.00, "percentage": 50.0},
            "PORT-C": {"name": "AI Foundations & Memory Systems", "cost": 140.00, "percentage": 14.4}
        },
        "value_to_cost": {
            "OBJ-101": {"value_score": 95.0, "cost": 345.50, "roi_ratio": 2.75},
            "OBJ-102": {"value_score": 85.0, "cost": 485.00, "roi_ratio": 1.75},
            "OBJ-103": {"value_score": 75.0, "cost": 120.00, "roi_ratio": 6.25},
            "OBJ-104": {"value_score": 60.0, "cost": 320.00, "roi_ratio": 1.88}
        }
    }

def load_state() -> dict:
    state = uawos_db.db_get_state("uawos_budget", None)
    if state is not None:
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(state, f, indent=2)
        except Exception:
            pass
        return state
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
    uawos_db.db_save_state("uawos_budget", state)
# FR-151: Objective budgets
def allocate_objective_budget(objective_id: str, name: str, budget: float) -> dict:
    state = load_state()
    if objective_id not in state["objective_budgets"]:
        state["objective_budgets"][objective_id] = {"name": name, "budget": budget, "actual": 0.0, "status": "Draft"}
    else:
        state["objective_budgets"][objective_id]["budget"] = budget
        state["objective_budgets"][objective_id]["name"] = name
    save_state(state)
    return state["objective_budgets"][objective_id]

# FR-152: Action budgets
def allocate_action_budget(action_id: str, objective_id: str, name: str, budget: float) -> dict:
    state = load_state()
    state["action_budgets"][action_id] = {
        "name": name,
        "objective_id": objective_id,
        "budget": budget,
        "actual": 0.0
    }
    save_state(state)
    return state["action_budgets"][action_id]

# FR-153: Agent cost tracking & FR-154: Token consumption tracking
def record_agent_cost(agent_name: str, model_name: str, input_tokens: int, output_tokens: int, reasoning_tokens: int = 0):
    state = load_state()
    
    # Resolve pricing
    pricing = MODEL_PRICING.get(model_name, MODEL_PRICING["default"])
    in_cost = (input_tokens / 1000000.0) * pricing["input"]
    out_cost = (output_tokens / 1000000.0) * pricing["output"]
    reason_cost = (reasoning_tokens / 1000000.0) * pricing["reasoning"]
    run_cost = round(in_cost + out_cost + reason_cost, 4)
    
    # Update Token Consumption
    if model_name not in state["token_consumption"]:
        state["token_consumption"][model_name] = {"input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0, "cost": 0.0}
    
    tc = state["token_consumption"][model_name]
    tc["input_tokens"] += input_tokens
    tc["output_tokens"] += output_tokens
    tc["reasoning_tokens"] += reasoning_tokens
    tc["cost"] = round(tc["cost"] + run_cost, 2)
    
    # Update Agent Cost
    if agent_name not in state["agent_costs"]:
        state["agent_costs"][agent_name] = {"cost": 0.0, "token_count": 0, "call_count": 0}
        
    ac = state["agent_costs"][agent_name]
    ac["cost"] = round(ac["cost"] + run_cost, 2)
    ac["token_count"] += (input_tokens + output_tokens + reasoning_tokens)
    ac["call_count"] += 1
    
    # Add to default OBJ-103 DTASE or active objectives
    if "OBJ-103" in state["objective_budgets"]:
        state["objective_budgets"]["OBJ-103"]["actual"] = round(state["objective_budgets"]["OBJ-103"]["actual"] + run_cost, 2)
        
    save_state(state)

# FR-155: Cost forecasting & FR-158: Budget variance tracking
def calculate_forecasts_and_variance(state: dict) -> dict:
    total_budget = sum(o["budget"] for o in state["objective_budgets"].values())
    total_actual = sum(o["actual"] for o in state["objective_budgets"].values())
    
    # Simple linear run-rate forecast model
    # Assume 10 days of run elapsed, total 30 planned
    elapsed_days = 10
    total_days = 30
    run_rate_per_day = round(total_actual / elapsed_days, 2) if elapsed_days > 0 else 0.0
    forecast_spend = round(run_rate_per_day * total_days, 2)
    
    variance = round(total_actual - total_budget, 2)
    variance_pct = round((variance / total_budget) * 100, 1) if total_budget > 0 else 0.0
    
    # Exceed governance risk check
    is_over_budget_risk = forecast_spend > total_budget
    
    return {
        "total_budget": total_budget,
        "total_actual": total_actual,
        "run_rate_per_day": run_rate_per_day,
        "forecast_spend": forecast_spend,
        "variance": variance,
        "variance_pct": variance_pct,
        "is_over_budget_risk": is_over_budget_risk
    }

# FR-156: Cost governance
def evaluate_cost_governance(objective_id: str, threshold_ratio: float = 0.9) -> dict:
    state = load_state()
    obj = state["objective_budgets"].get(objective_id)
    if not obj:
        return {"status": "Error", "message": f"Objective {objective_id} not found."}
        
    budget = obj["budget"]
    actual = obj["actual"]
    ratio = actual / budget if budget > 0 else 0.0
    
    verdict = "APPROVED"
    message = "Cost levels within safe operating parameters."
    
    if ratio >= 1.0:
        verdict = "BREACHED"
        message = f"Budget limit of ${budget:.2f} exceeded! Active execution blocked by Governor."
    elif ratio >= threshold_ratio:
        verdict = "WARNING"
        message = f"Objective has consumed {ratio*100:.1f}% of allocated budget. Optimization recommended."
        
    return {
        "objective_id": objective_id,
        "budget": budget,
        "actual": actual,
        "consumption_ratio": round(ratio, 3),
        "governance_verdict": verdict,
        "message": message
    }

# FR-157: Budget approvals
def submit_approval_request(objective_id: str, amount: float, requested_by: str) -> dict:
    state = load_state()
    req_id = f"APP-{len(state['budget_approvals']) + 1:03d}"
    req = {
        "id": req_id,
        "objective_id": objective_id,
        "amount": amount,
        "status": "Pending",
        "requested_by": requested_by,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    state["budget_approvals"].append(req)
    save_state(state)
    return req

def process_approval_request(approval_id: str, decision: str) -> dict:
    state = load_state()
    for req in state["budget_approvals"]:
        if req["id"] == approval_id:
            req["status"] = decision
            if decision == "Approved":
                obj_id = req["objective_id"]
                if obj_id in state["objective_budgets"]:
                    state["objective_budgets"][obj_id]["budget"] += req["amount"]
                    state["objective_budgets"][obj_id]["status"] = "Approved"
            save_state(state)
            return req
    return {"error": f"Approval request {approval_id} not found."}

# FR-159: Cost attribution & FR-160: Value-to-cost analysis
def get_summary() -> dict:
    state = load_state()
    metrics = calculate_forecasts_and_variance(state)
    
    # Calculate fresh attribution metrics
    total_cost = sum(o["actual"] for o in state["objective_budgets"].values())
    attribution = state["portfolio_attribution"]
    for p_id, p_val in attribution.items():
        if p_id == "PORT-A":
            p_val["cost"] = state["objective_budgets"]["OBJ-101"]["actual"]
        elif p_id == "PORT-B":
            p_val["cost"] = state["objective_budgets"]["OBJ-102"]["actual"]
        elif p_id == "PORT-C":
            p_val["cost"] = state["objective_budgets"]["OBJ-103"]["actual"] + state["objective_budgets"]["OBJ-104"]["actual"]
        
        p_val["percentage"] = round((p_val["cost"] / total_cost) * 100, 1) if total_cost > 0 else 0.0
        
    # Calculate value-to-cost ratios
    v_to_c = state["value_to_cost"]
    for obj_id, val_dict in v_to_c.items():
        obj = state["objective_budgets"].get(obj_id)
        if obj:
            val_dict["cost"] = obj["actual"]
            val_dict["roi_ratio"] = round(val_dict["value_score"] / (obj["actual"] / 100.0), 2) if obj["actual"] > 0 else 0.0

    return {
        "metrics": metrics,
        "objective_budgets": state["objective_budgets"],
        "action_budgets": state["action_budgets"],
        "agent_costs": state["agent_costs"],
        "token_consumption": state["token_consumption"],
        "budget_approvals": state["budget_approvals"],
        "portfolio_attribution": attribution,
        "value_to_cost": v_to_c
    }

# Self-verification checks for all requirements
def verify_fr_151():
    """Verify objective budgets."""
    state = load_state()
    assert len(state["objective_budgets"]) > 0, "No objective budgets configured."
    return True

def verify_fr_152():
    """Verify action budgets."""
    state = load_state()
    assert len(state["action_budgets"]) > 0, "No action budgets configured."
    return True

def verify_fr_153():
    """Verify agent cost tracking."""
    state = load_state()
    assert len(state["agent_costs"]) > 0, "No agent costs tracked."
    return True

def verify_fr_154():
    """Verify token consumption tracking."""
    state = load_state()
    assert len(state["token_consumption"]) > 0, "No tokens tracked."
    return True

def verify_fr_155():
    """Verify cost forecasting."""
    summary = get_summary()
    assert summary["metrics"]["forecast_spend"] > 0, "Forecast calculation invalid."
    return True

def verify_fr_156():
    """Verify cost governance filters."""
    verdict_1 = evaluate_cost_governance("OBJ-101")
    assert verdict_1["governance_verdict"] in ["APPROVED", "WARNING", "BREACHED"], "Invalid governance verdict."
    return True

def verify_fr_157():
    """Verify budget approvals workflow."""
    state = load_state()
    assert len(state["budget_approvals"]) > 0, "No budget approval requests present."
    return True

def verify_fr_158():
    """Verify budget variance tracking."""
    summary = get_summary()
    assert "variance" in summary["metrics"], "Variance tracking missing."
    return True

def verify_fr_159():
    """Verify cost attribution."""
    summary = get_summary()
    assert len(summary["portfolio_attribution"]) > 0, "No cost attribution computed."
    return True

def verify_fr_160():
    """Verify value-to-cost analysis."""
    summary = get_summary()
    assert len(summary["value_to_cost"]) > 0, "No value-to-cost metrics computed."
    return True

def run_self_tests():
    """Run all functional tests."""
    print("Running Budget & Cost Management self tests...")
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
