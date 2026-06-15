# application/use_cases/objective_use_cases.py
import re
import os
import time
from typing import List

from domains.objective.objective import Objective
from domains.objective.conflict_detector import detect_conflicts
from domains.objective.scoring import calculate_health, calculate_confidence
from infrastructure.storage.json_fallback_store import load_state, save_state
from shared.utilities.context import get_tenant_id

STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "uawos_objective_state.json"
)

def get_default_state() -> dict:
    return {"objectives": {}}



def create_objective(
    title: str,
    description: str,
    source_type: str = "text",
    source_uri: str = "",
    owner: str = "System Agent",
    sponsor: str = "CPO",
    priority: str = "Medium",
    dependencies: List[str] = None,
) -> dict:
    state = load_state()
    tenant_id = get_tenant_id()
    
    objective_id = f"OBJ-{len(state['objectives']) + 101:03d}"
    dependencies = dependencies or []
    
    obj = Objective(
        id=objective_id,
        title=title,
        description=description,
        source_type=source_type,
        source_uri=source_uri,
        owner=owner,
        sponsor=sponsor,
        priority=priority,
        dependencies=dependencies,
        tenant_id=tenant_id,
    )
    
    state["objectives"][objective_id] = obj.to_dict()
    save_state(state)
    
    recalculate_scores(objective_id)
    state = load_state()
    return state["objectives"][objective_id]


def update_objective(objective_id: str, updates: dict) -> dict:
    state = load_state()
    obj_dict = state["objectives"].get(objective_id)
    if not obj_dict:
        return {"error": f"Objective {objective_id} not found."}
        
    obj = Objective.from_dict(obj_dict)
    
    snapshot = {k: v for k, v in obj.to_dict().items() if k != "history"}
    obj.history.append({"timestamp": time.time(), "state": snapshot})
    
    for k, v in updates.items():
        if k in ["title", "description", "owner", "sponsor", "priority", "dependencies", "status"]:
            setattr(obj, k, v)
            
    obj.version += 1
    state["objectives"][objective_id] = obj.to_dict()
    save_state(state)
    
    recalculate_scores(objective_id)
    state = load_state()
    return state["objectives"][objective_id]


def archive_objective(objective_id: str) -> dict:
    return update_objective(objective_id, {"status": "archived"})


def restore_objective(objective_id: str) -> dict:
    return update_objective(objective_id, {"status": "active"})


def cancel_objective(objective_id: str) -> dict:
    return update_objective(objective_id, {"status": "cancelled"})


def pause_objective(objective_id: str) -> dict:
    return update_objective(objective_id, {"status": "paused"})


def resume_objective(objective_id: str) -> dict:
    return update_objective(objective_id, {"status": "active"})


def recalculate_scores(objective_id: str):
    state = load_state()
    obj_dict = state["objectives"].get(objective_id)
    if not obj_dict:
        return
        
    obj = Objective.from_dict(obj_dict)
    
    all_objs = {oid: Objective.from_dict(o) for oid, o in state["objectives"].items()}
    conflicts = detect_conflicts(all_objs)
    
    in_cycle = False
    has_conflict = False
    for c in conflicts:
        if objective_id in c["objectives"]:
            has_conflict = True
            if c["type"] == "Circular Dependency":
                in_cycle = True
                
    dep_statuses = []
    for dep_id in obj.dependencies:
        dep_dict = state["objectives"].get(dep_id)
        if dep_dict:
            dep_statuses.append(dep_dict.get("status", "active"))
            
    budget_verdict = "APPROVED"
    try:
        import application.use_cases.billing_use_cases as billing
        gov = billing.evaluate_cost_governance(objective_id)
        budget_verdict = gov.get("governance_verdict", "APPROVED")
    except Exception:
        pass
        
    has_outcomes = True
    try:
        import application.use_cases.outcome_use_cases as outcome_uc
        outcomes = outcome_uc.get_objective_outcomes(objective_id)
        if not outcomes:
            has_outcomes = False
    except Exception:
        pass
        
    obj.health_score = calculate_health(
        objective=obj,
        in_cycle=in_cycle,
        dependency_statuses=dep_statuses,
        budget_verdict=budget_verdict,
        has_outcomes=has_outcomes,
    )
    
    obj.confidence_score = calculate_confidence(
        objective=obj,
        has_conflict=has_conflict,
    )
    
    state["objectives"][objective_id] = obj.to_dict()
    save_state(state)


def create_objective_from_input(
    text: str, input_type: str, owner: str = "", sponsor: str = "", source_uri: str = ""
) -> dict:
    title = f"New Objective from {input_type.capitalize()}"
    description = text
    priority = "Medium"
    dependencies = []
    
    text_lower = text.lower()
    if any(w in text_lower for w in ["urgent", "critical", "immediate", "highest", "blocker"]):
        priority = "Critical"
    elif any(w in text_lower for w in ["high", "important", "soon"]):
        priority = "High"
    elif any(w in text_lower for w in ["low", "minor", "deferred"]):
        priority = "Low"
        
    dep_matches = re.findall(r"obj-\d+", text_lower)
    if dep_matches:
        dependencies = [m.upper() for m in dep_matches]
        
    parser_confidence = 70.0
    
    try:
        import uawos_dtase
        if uawos_dtase:
            analysis = uawos_dtase.analyze_unstructured_input(text)
            if analysis.get("status") == "Success":
                if analysis.get("title"):
                    title = analysis["title"]
                if analysis.get("description"):
                    description = analysis["description"]
                if analysis.get("priority") in ["Critical", "High", "Medium", "Low"]:
                    priority = analysis["priority"]
                if analysis.get("dependencies"):
                    dependencies = [d.upper() for d in analysis["dependencies"]]
                parser_confidence = int(analysis["traceability"].get("confidence_score", 0.95) * 100)
    except Exception:
        pass
        
    if not owner:
        owner = "System Agent"
    if not sponsor:
        sponsor = "CPO"
        
    obj_dict = create_objective(
        title=title,
        description=description,
        source_type=input_type,
        source_uri=source_uri,
        owner=owner,
        sponsor=sponsor,
        priority=priority,
        dependencies=dependencies,
    )
    
    state = load_state()
    state["objectives"][obj_dict["id"]]["confidence_score"] = float(parser_confidence)
    save_state(state)
    recalculate_scores(obj_dict["id"])
    
    return load_state()["objectives"][obj_dict["id"]]


def detect_objective_conflicts() -> list:
    state = load_state()
    all_objs = {oid: Objective.from_dict(o) for oid, o in state["objectives"].items()}
    return detect_conflicts(all_objs)
