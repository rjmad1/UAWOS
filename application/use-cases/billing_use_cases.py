# application/use-cases/billing_use_cases.py
import time
from typing import Dict

from domains.billing.billing import (
    MODEL_PRICING,
    ObjectiveBudget,
    ActionBudget,
    AgentCost,
    TokenConsumption,
    BudgetApproval,
    calculate_cost_run_rate,
    evaluate_cost_governance as domain_evaluate_cost_governance,
)
from infrastructure.storage.json_fallback_store import load_state, save_state
from shared.utilities.context import get_tenant_id


def allocate_objective_budget(objective_id: str, name: str, budget: float) -> dict:
    state = load_state()
    if objective_id not in state["objective_budgets"]:
        ob = ObjectiveBudget(name=name, budget=budget, actual=0.0, status="Pending")
    else:
        ob = ObjectiveBudget.from_dict(state["objective_budgets"][objective_id])
        ob.budget = budget
        ob.name = name
    state["objective_budgets"][objective_id] = ob.to_dict()
    save_state(state)
    return state["objective_budgets"][objective_id]


def allocate_action_budget(action_id: str, objective_id: str, name: str, budget: float) -> dict:
    state = load_state()
    ab = ActionBudget(name=name, objective_id=objective_id, budget=budget, actual=0.0)
    state["action_budgets"][action_id] = ab.to_dict()
    save_state(state)
    return state["action_budgets"][action_id]


def record_agent_cost(
    agent_name: str,
    model_name: str,
    input_tokens: int,
    output_tokens: int,
    reasoning_tokens: int = 0,
):
    state = load_state()
    
    pricing = MODEL_PRICING.get(model_name, MODEL_PRICING["default"])
    in_cost = (input_tokens / 1000000.0) * pricing["input"]
    out_cost = (output_tokens / 1000000.0) * pricing["output"]
    reason_cost = (reasoning_tokens / 1000000.0) * pricing["reasoning"]
    run_cost = round(in_cost + out_cost + reason_cost, 4)
    
    # Update Token Consumption
    if model_name not in state["token_consumption"]:
        tc = TokenConsumption()
    else:
        tc = TokenConsumption.from_dict(state["token_consumption"][model_name])
    tc.input_tokens += input_tokens
    tc.output_tokens += output_tokens
    tc.reasoning_tokens += reasoning_tokens
    tc.cost = round(tc.cost + run_cost, 2)
    state["token_consumption"][model_name] = tc.to_dict()
    
    # Update Agent Cost
    if agent_name not in state["agent_costs"]:
        ac = AgentCost()
    else:
        ac = AgentCost.from_dict(state["agent_costs"][agent_name])
    ac.cost = round(ac.cost + run_cost, 2)
    ac.token_count += input_tokens + output_tokens + reasoning_tokens
    ac.call_count += 1
    state["agent_costs"][agent_name] = ac.to_dict()
    
    # Add to default OBJ-103 DTASE or active objectives
    if "OBJ-103" in state["objective_budgets"]:
        ob = ObjectiveBudget.from_dict(state["objective_budgets"]["OBJ-103"])
        ob.actual = round(ob.actual + run_cost, 2)
        state["objective_budgets"]["OBJ-103"] = ob.to_dict()
        
    save_state(state)


def evaluate_cost_governance(objective_id: str, threshold_ratio: float = 0.9) -> dict:
    state = load_state()
    obj_dict = state["objective_budgets"].get(objective_id)
    if not obj_dict:
        return {"status": "Error", "message": f"Objective {objective_id} not found."}
        
    ob = ObjectiveBudget.from_dict(obj_dict)
    res = domain_evaluate_cost_governance(ob.budget, ob.actual, threshold_ratio)
    res["objective_id"] = objective_id
    return res


def submit_approval_request(objective_id: str, amount: float, requested_by: str) -> dict:
    state = load_state()
    req_id = f"APP-{len(state['budget_approvals']) + 1:03d}"
    req = BudgetApproval(
        id=req_id,
        objective_id=objective_id,
        amount=amount,
        status="Pending",
        requested_by=requested_by,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    state["budget_approvals"].append(req.to_dict())
    save_state(state)
    return req.to_dict()


def process_approval_request(approval_id: str, decision: str) -> dict:
    state = load_state()
    for req_dict in state["budget_approvals"]:
        req = BudgetApproval.from_dict(req_dict)
        if req.id == approval_id:
            req.status = decision
            req_dict.update(req.to_dict())
            if decision == "Approved":
                obj_id = req.objective_id
                if obj_id in state["objective_budgets"]:
                    ob = ObjectiveBudget.from_dict(state["objective_budgets"][obj_id])
                    ob.budget += req.amount
                    ob.status = "Approved"
                    state["objective_budgets"][obj_id] = ob.to_dict()
            save_state(state)
            return req_dict
    return {"error": f"Approval request {approval_id} not found."}


def get_summary() -> dict:
    state = load_state()
    
    # Map domain dictionaries to entities for cost forecasts
    objective_budgets = {oid: ObjectiveBudget.from_dict(o) for oid, o in state["objective_budgets"].items()}
    metrics = calculate_cost_run_rate(objective_budgets)
    
    # Calculate attribution
    total_cost = sum(o.actual for o in objective_budgets.values())
    attribution = state["portfolio_attribution"]
    for p_id, p_val in attribution.items():
        if p_id == "PORT-A":
            p_val["cost"] = state["objective_budgets"]["OBJ-101"]["actual"]
        elif p_id == "PORT-B":
            p_val["cost"] = state["objective_budgets"]["OBJ-102"]["actual"]
        elif p_id == "PORT-C":
            p_val["cost"] = (
                state["objective_budgets"]["OBJ-103"]["actual"] + state["objective_budgets"]["OBJ-104"]["actual"]
            )
        p_val["percentage"] = round((p_val["cost"] / total_cost) * 100, 1) if total_cost > 0 else 0.0
        
    # Calculate value-to-cost
    v_to_c = state["value_to_cost"]
    for obj_id, val_dict in v_to_c.items():
        obj = state["objective_budgets"].get(obj_id)
        if obj:
            val_dict["cost"] = obj["actual"]
            val_dict["roi_ratio"] = (
                round(val_dict["value_score"] / (obj["actual"] / 100.0), 2) if obj["actual"] > 0 else 0.0
            )
            
    return {
        "metrics": metrics,
        "objective_budgets": state["objective_budgets"],
        "action_budgets": state["action_budgets"],
        "agent_costs": state["agent_costs"],
        "token_consumption": state["token_consumption"],
        "budget_approvals": state["budget_approvals"],
        "portfolio_attribution": attribution,
        "value_to_cost": v_to_c,
    }
