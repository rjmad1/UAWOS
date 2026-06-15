# application/use_cases/outcome_use_cases.py
import os
from typing import List
from domains.outcome.outcome import Outcome
from infrastructure.storage.json_fallback_store import load_state, save_state

STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "uawos_outcome_state.json"
)

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
                "forecasted_state": 83.5,
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
                "forecasted_state": 12.0,
            },
        }
    }



def create_outcome(
    objective_id: str,
    title: str,
    metric: str,
    unit: str,
    weight: float = 1.0,
    dependencies: List[str] = None,
    confidence_score: float = 90.0,
    owner: str = "Product Owner",
    baseline_state: float = 0.0,
    target_state: float = 100.0,
    current_state: float = 0.0,
) -> dict:
    if not metric or not unit:
        raise ValueError("metric and unit are required for a measurable Outcome.")
        
    state = load_state()
    outcome_id = f"OUT-{len(state['outcomes']) + 101:03d}"
    dependencies = dependencies or []
    
    out = Outcome(
        id=outcome_id,
        objective_id=objective_id,
        title=title,
        metric=metric,
        unit=unit,
        weight=weight,
        dependencies=dependencies,
        confidence_score=confidence_score,
        owner=owner,
        baseline_state=baseline_state,
        target_state=target_state,
        current_state=current_state,
    )
    
    out.forecasted_state = out.calculate_forecast()
    state["outcomes"][outcome_id] = out.to_dict()
    save_state(state)
    
    # Recalculate forecasts
    recalculate_forecasts(outcome_id)
    return load_state()["outcomes"][outcome_id]


def get_objective_outcomes(objective_id: str) -> list:
    state = load_state()
    return [out for out in state["outcomes"].values() if out["objective_id"] == objective_id]


def update_outcome(outcome_id: str, updates: dict) -> dict:
    state = load_state()
    out_dict = state["outcomes"].get(outcome_id)
    if not out_dict:
        raise ValueError(f"Outcome {outcome_id} not found.")
        
    out = Outcome.from_dict(out_dict)
    
    for k, v in updates.items():
        if k in [
            "title",
            "metric",
            "unit",
            "weight",
            "dependencies",
            "confidence_score",
            "owner",
            "baseline_state",
            "target_state",
            "current_state",
        ]:
            setattr(out, k, v)
            
    state["outcomes"][outcome_id] = out.to_dict()
    save_state(state)
    
    recalculate_forecasts(outcome_id)
    return load_state()["outcomes"][outcome_id]


def recalculate_forecasts(outcome_id: str):
    state = load_state()
    out_dict = state["outcomes"].get(outcome_id)
    if not out_dict:
        return
        
    out = Outcome.from_dict(out_dict)
    out.forecasted_state = out.calculate_forecast()
    
    state["outcomes"][outcome_id] = out.to_dict()
    save_state(state)
