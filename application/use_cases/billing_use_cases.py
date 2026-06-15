# application/use_cases/billing_use_cases.py
import os
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

STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "uawos_budget_state.json"
)

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
