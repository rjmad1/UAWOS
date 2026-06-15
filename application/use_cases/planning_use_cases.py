import os
import time
from typing import List, Dict

from domains.planning.plan import Plan
from infrastructure.storage.json_fallback_store import load_state, save_state

STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "uawos_planning_state.json"
)

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
    is_alternative: bool = False,
) -> dict:
    state = load_state()
    plan_id = f"PLN-{len(state['plans']) + 100:03d}"
    
    plan = Plan(
        id=plan_id,
        objective_id=objective_id,
        title=title,
        steps=steps,
        cost_estimate=cost_estimate,
        duration_estimate=duration_estimate,
        resource_requirements=resource_requirements,
        success_probability=success_probability,
        risks=risks or ["General delivery risk"],
        assumptions=assumptions or ["Required resources are available"],
        is_alternative=is_alternative,
    )

    state["plans"][plan_id] = plan.to_dict()
    save_state(state)
    return state["plans"][plan_id]


def generate_plans(objective_id: str) -> list:
    p1 = create_plan(
        objective_id=objective_id,
        title=f"Plan A for {objective_id} (Optimized)",
        steps=["Step A1: Basic deployment", "Step A2: Verify"],
        cost_estimate=200.0,
        duration_estimate=5,
        resource_requirements=["Dev Agent"],
        success_probability=0.90,
        is_alternative=False,
    )
    p2 = create_plan(
        objective_id=objective_id,
        title=f"Plan B for {objective_id} (Extended)",
        steps=["Step B1: Full regression tests", "Step B2: Canary deployment"],
        cost_estimate=450.0,
        duration_estimate=12,
        resource_requirements=["Dev Agent", "QA Agent"],
        success_probability=0.98,
        is_alternative=True,
    )
    return [p1, p2]


def rank_plans(objective_id: str) -> list:
    state = load_state()
    plans = [Plan.from_dict(p) for p in state["plans"].values() if p["objective_id"] == objective_id]
    plans.sort(key=lambda p: p.calculate_score(), reverse=True)
    return [p.id for p in plans]


def simulate_plan(plan_id: str) -> dict:
    state = load_state()
    plan_dict = state["plans"].get(plan_id)
    if not plan_dict:
        raise ValueError(f"Plan {plan_id} not found.")
    
    plan = Plan.from_dict(plan_dict)
    return plan.simulate()


def compare_plans(plan_id_1: str, plan_id_2: str) -> dict:
    state = load_state()
    p1_dict = state["plans"].get(plan_id_1)
    p2_dict = state["plans"].get(plan_id_2)
    if not p1_dict or not p2_dict:
        raise ValueError("One or both plans not found.")

    p1 = Plan.from_dict(p1_dict)
    p2 = Plan.from_dict(p2_dict)

    return {
        "compared": [plan_id_1, plan_id_2],
        "cost_difference": p1.cost_estimate - p2.cost_estimate,
        "duration_difference": p1.duration_estimate - p2.duration_estimate,
        "success_probability_difference": p1.success_probability - p2.success_probability,
    }


def approve_plan(plan_id: str) -> dict:
    return modify_plan(plan_id, {"status": "approved"})


def reject_plan(plan_id: str) -> dict:
    return modify_plan(plan_id, {"status": "rejected"})


def archive_plan(plan_id: str) -> dict:
    return modify_plan(plan_id, {"status": "archived"})


def modify_plan(plan_id: str, updates: dict) -> dict:
    state = load_state()
    plan_dict = state["plans"].get(plan_id)
    if not plan_dict:
        raise ValueError(f"Plan {plan_id} not found.")

    plan = Plan.from_dict(plan_dict)
    
    # Save to history
    snap = {k: v for k, v in plan.to_dict().items() if k != "history"}
    plan.history.append({"timestamp": time.time(), "state": snap})

    for k, v in updates.items():
        if k in [
            "title",
            "steps",
            "cost_estimate",
            "duration_estimate",
            "resource_requirements",
            "success_probability",
            "status",
            "risks",
            "assumptions",
        ]:
            setattr(plan, k, v)

    plan.version += 1
    state["plans"][plan_id] = plan.to_dict()
    save_state(state)
    return state["plans"][plan_id]


def trigger_replanning(objective_id: str, reason: str) -> dict:
    state = load_state()
    active_plans = [
        p for p in state["plans"].values() if p["objective_id"] == objective_id and p["status"] == "approved"
    ]

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
        success_probability=0.92,
    )
    return new_plan


def get_planning_traceability(plan_id: str) -> dict:
    state = load_state()
    plan_dict = state["plans"].get(plan_id)
    if not plan_dict:
        raise ValueError(f"Plan {plan_id} not found.")
    
    plan = Plan.from_dict(plan_dict)
    return {
        "plan_id": plan_id,
        "objective_id": plan.objective_id,
        "traceability_chain": f"OBJ -> {plan.objective_id} -> PLAN -> {plan_id} -> STEPS -> {', '.join(plan.steps)}",
    }


def route_action_to_agent(action_id: str, tenant_id: str = "default_tenant") -> str:
    """Dynamically route an action to the best-matching workforce agent based on required skills/capabilities."""
    import uawos_agent_workforce
    import infrastructure.database.db as db_module

    # 1. Fetch action details from DB (or state)
    actions_data = db_module.db_load_actions()
    actions = actions_data.get("actions", {})
    action = actions.get(action_id)

    # Heuristic required skill map based on action name or metadata
    req_skill = "code_execution"  # default
    action_name = action.get("name", "").lower() if action else ""
    if "plan" in action_name or "estimate" in action_name:
        req_skill = "plan_generation"
    elif "review" in action_name or "qa" in action_name:
        req_skill = "code_review"
    elif "policy" in action_name or "governance" in action_name:
        req_skill = "policy_enforcement"
    elif "index" in action_name or "knowledge" in action_name:
        req_skill = "memory_indexing"

    # Find agents matching the skill
    candidates = uawos_agent_workforce.get_agents_by_skill(req_skill)
    if candidates:
        # Route to candidate (optionally selecting the one with the highest trust score)
        best_candidate = candidates[0]
        max_trust = -1.0
        for cand in candidates:
            try:
                trust = uawos_agent_workforce.calculate_agent_trust(cand)
                if trust > max_trust:
                    max_trust = trust
                    best_candidate = cand
            except Exception:
                pass
        return best_candidate

    # Fallback to general Executor Agent
    return "Executor Agent"
