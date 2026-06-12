# uawos_workforce.py
import os
import time

from uawos_state_utils import load_state, save_state

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_workforce_state.json")


def get_default_state() -> dict:
    return {
        "entities": {
            "Lead Engineer": {
                "id": "WRK-H-01",
                "name": "Lead Engineer",
                "type": "human",
                "capacity": 100,
                "utilization": 80.0,
                "trust_score": 98.0,
                "performance_score": 95.0,
            },
            "Executor Agent": {
                "id": "WRK-A-01",
                "name": "Executor Agent",
                "type": "agent",
                "capacity": 100,
                "utilization": 45.0,
                "trust_score": 92.0,
                "performance_score": 90.0,
            },
        },
        "teams": {"Core Execution Team": ["Lead Engineer", "Executor Agent"]},
        "assignments": {},
        "delegations": [],
    }


# State handling via shared utilities


# Core API
def add_workforce_entity(name: str, entity_type: str, capacity: int = 100) -> dict:
    """Manage human (FR-081) or agent (FR-082) workforce entities."""
    state = load_state()
    prefix = "WRK-H-" if entity_type == "human" else "WRK-A-"
    eid = f"{prefix}{len(state['entities']) + 1:02d}"

    entity = {
        "id": eid,
        "name": name,
        "type": entity_type,
        "capacity": capacity,
        "utilization": 0.0,
        "trust_score": 100.0,
        "performance_score": 100.0,
    }
    state["entities"][name] = entity
    save_state(state)
    return state["entities"][name]


# FR-083: Manage Teams
def create_team(team_name: str, members: list) -> dict:
    state = load_state()
    state["teams"][team_name] = members
    save_state(state)
    return {"team": team_name, "members": members}


# FR-084: Agent Assignment
def assign_agent(action_id: str, agent_name: str) -> dict:
    state = load_state()
    entity = state["entities"].get(agent_name)
    if not entity or entity["type"] != "agent":
        raise ValueError(f"Agent {agent_name} not found.")
    state["assignments"][action_id] = agent_name
    save_state(state)
    return {"action_id": action_id, "assigned_to": agent_name}


# FR-085: Human Assignment
def assign_human(action_id: str, human_name: str) -> dict:
    state = load_state()
    entity = state["entities"].get(human_name)
    if not entity or entity["type"] != "human":
        raise ValueError(f"Human {human_name} not found.")
    state["assignments"][action_id] = human_name
    save_state(state)
    return {"action_id": action_id, "assigned_to": human_name}


# FR-086: Delegation
def delegate_task(from_entity: str, to_entity: str, task_name: str) -> dict:
    state = load_state()
    if from_entity not in state["entities"] or to_entity not in state["entities"]:
        raise ValueError("Entities for delegation do not exist.")
    delegation = {
        "from": from_entity,
        "to": to_entity,
        "task": task_name,
        "timestamp": int(time.time() if "time" in globals() else 0),
    }
    state["delegations"].append(delegation)
    save_state(state)
    return delegation


# FR-087: Workforce utilization tracking
def track_utilization(entity_name: str, util_pct: float) -> dict:
    state = load_state()
    entity = state["entities"].get(entity_name)
    if not entity:
        raise ValueError(f"Workforce entity {entity_name} not found.")
    entity["utilization"] = min(100.0, max(0.0, util_pct))
    state["entities"][entity_name] = entity
    save_state(state)
    return entity


# FR-088: Workforce capacity management
def manage_capacity(entity_name: str, capacity: int) -> dict:
    state = load_state()
    entity = state["entities"].get(entity_name)
    if not entity:
        raise ValueError(f"Workforce entity {entity_name} not found.")
    entity["capacity"] = max(0, capacity)
    state["entities"][entity_name] = entity
    save_state(state)
    return entity


# FR-089: Workforce trust scoring
def calculate_trust_score(entity_name: str) -> float:
    state = load_state()
    entity = state["entities"].get(entity_name)
    if not entity:
        raise ValueError(f"Workforce entity {entity_name} not found.")
    # Heuristics trust score
    trust = 100.0
    if entity["utilization"] > 95.0:  # Burnout penalty
        trust -= 5.0
    if entity["performance_score"] < 80.0:
        trust -= 15.0
    entity["trust_score"] = max(0.0, trust)
    state["entities"][entity_name] = entity
    save_state(state)
    return entity["trust_score"]


# FR-090: Workforce performance tracking
def track_performance(entity_name: str, rating: float) -> dict:
    state = load_state()
    entity = state["entities"].get(entity_name)
    if not entity:
        raise ValueError(f"Workforce entity {entity_name} not found.")
    entity["performance_score"] = min(100.0, max(0.0, rating))
    state["entities"][entity_name] = entity
    save_state(state)
    return entity


# ----------------- VERIFICATION TESTS (FR-081 to FR-090) -----------------


def verify_fr_081():
    h = add_workforce_entity("QA Engineer", "human")
    assert h["type"] == "human", "Human management failed."
    return True


def verify_fr_082():
    a = add_workforce_entity("QA Agent", "agent")
    assert a["type"] == "agent", "Agent management failed."
    return True


def verify_fr_083():
    team = create_team("Dev Team", ["Lead Engineer"])
    assert "Lead Engineer" in team["members"], "Team creation failed."
    return True


def verify_fr_084():
    ass = assign_agent("ACT-101", "Executor Agent")
    assert ass["assigned_to"] == "Executor Agent", "Agent assignment failed."
    return True


def verify_fr_085():
    ass = assign_human("ACT-101", "Lead Engineer")
    assert ass["assigned_to"] == "Lead Engineer", "Human assignment failed."
    return True


def verify_fr_086():
    dlg = delegate_task("Lead Engineer", "Executor Agent", "Build database script")
    assert dlg["to"] == "Executor Agent", "Delegation failed."
    return True


def verify_fr_087():
    entity = track_utilization("Executor Agent", 75.0)
    assert entity["utilization"] == 75.0, "Utilization tracking failed."
    return True


def verify_fr_088():
    entity = manage_capacity("Executor Agent", 80)
    assert entity["capacity"] == 80, "Capacity management failed."
    return True


def verify_fr_089():
    score = calculate_trust_score("Executor Agent")
    assert score > 0, "Trust score failed."
    return True


def verify_fr_090():
    entity = track_performance("Executor Agent", 92.5)
    assert entity["performance_score"] == 92.5, "Performance tracking failed."
    return True


def run_self_tests():
    print("Running Workforce Management self tests...")
    state = get_default_state()
    save_state(state)

    tests = [
        ("FR-081", verify_fr_081),
        ("FR-082", verify_fr_082),
        ("FR-083", verify_fr_083),
        ("FR-084", verify_fr_084),
        ("FR-085", verify_fr_085),
        ("FR-086", verify_fr_086),
        ("FR-087", verify_fr_087),
        ("FR-088", verify_fr_088),
        ("FR-089", verify_fr_089),
        ("FR-090", verify_fr_090),
    ]

    for code, fn in tests:
        try:
            fn()
            print(f"  [PASS] {code} verified.")
        except AssertionError as ae:
            print(f"  [FAIL] {code}: {ae}")
            raise ae

    print("All Workforce Engine self tests completed successfully!")


if __name__ == "__main__":
    run_self_tests()
