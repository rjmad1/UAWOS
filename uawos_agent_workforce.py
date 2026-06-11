# uawos_agent_workforce.py
import json
import os

from uawos_state_utils import load_state, save_state

import uawos_db

STATE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "uawos_agent_workforce_state.json"
)


def get_default_state() -> dict:
    return {
        "agents": {
            "Planner Agent": {
                "id": "AGT-01",
                "name": "Planner Agent",
                "class": "Planner",
                "capabilities": ["plan_generation", "estimation"],
                "lifecycle_state": "active",
                "trust_score": 95.0,
            },
            "Orchestrator Agent": {
                "id": "AGT-02",
                "name": "Orchestrator Agent",
                "class": "Orchestrator",
                "capabilities": ["workflow_orchestration"],
                "lifecycle_state": "active",
                "trust_score": 94.0,
            },
            "Executor Agent": {
                "id": "AGT-03",
                "name": "Executor Agent",
                "class": "Executor",
                "capabilities": ["code_execution"],
                "lifecycle_state": "idle",
                "trust_score": 92.0,
            },
            "Reviewer Agent": {
                "id": "AGT-04",
                "name": "Reviewer Agent",
                "class": "Reviewer",
                "capabilities": ["code_review"],
                "lifecycle_state": "idle",
                "trust_score": 96.0,
            },
            "Governor Agent": {
                "id": "AGT-05",
                "name": "Governor Agent",
                "class": "Governor",
                "capabilities": ["policy_enforcement"],
                "lifecycle_state": "active",
                "trust_score": 99.0,
            },
            "Learner Agent": {
                "id": "AGT-06",
                "name": "Learner Agent",
                "class": "Learner",
                "capabilities": ["learning_optimization"],
                "lifecycle_state": "idle",
                "trust_score": 90.0,
            },
            "Knowledge Manager Agent": {
                "id": "AGT-07",
                "name": "Knowledge Manager Agent",
                "class": "Knowledge Manager",
                "capabilities": ["memory_indexing"],
                "lifecycle_state": "active",
                "trust_score": 93.0,
            },
        }
    }

# FR-091 to FR-100: Register Agent
def register_agent(
    name: str,
    agent_class: str,
    capabilities: list = None,
    lifecycle_state: str = "active",
) -> dict:
    """Register a new workforce agent (FR-091 to FR-097)."""
    state = load_state()
    valid_classes = [
        "Planner",
        "Orchestrator",
        "Executor",
        "Reviewer",
        "Governor",
        "Learner",
        "Knowledge Manager",
    ]
    if agent_class not in valid_classes:
        raise ValueError(
            f"Invalid Agent Class: {agent_class}. Must be one of {valid_classes}"
        )

    aid = f"AGT-{len(state['agents']) + 1:02d}"
    agent = {
        "id": aid,
        "name": name,
        "class": agent_class,
        "capabilities": capabilities,  # FR-098
        "lifecycle_state": lifecycle_state,  # FR-099
        "trust_score": 100.0,  # FR-100
    }
    state["agents"][name] = agent
    save_state(state)
    return state["agents"][name]


def update_agent_lifecycle(name: str, state_value: str) -> dict:
    """Manage agent lifecycle states (FR-099)."""
    state = load_state()
    agent = state["agents"].get(name)
    if not agent:
        raise ValueError(f"Agent {name} not found.")
    valid_states = ["active", "idle", "paused", "terminated"]
    if state_value not in valid_states:
        raise ValueError(f"Invalid lifecycle state: {state_value}")
    agent["lifecycle_state"] = state_value
    state["agents"][name] = agent
    save_state(state)
    return state["agents"][name]


def calculate_agent_trust(name: str) -> float:
    """Track and compute agent trust score dynamically (FR-100) based on historical task outcomes in PostgreSQL."""
    state = load_state()
    agent = state["agents"].get(name)
    if not agent:
        raise ValueError(f"Agent {name} not found.")

    trust = 95.0

    # Try dynamic calculation via Postgres uawos_actions
    try:
        import uawos_db
        if uawos_db.DB_AVAILABLE:
            conn = uawos_db.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM uawos_actions WHERE owner = %s;", (name,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            if rows:
                total = len(rows)
                completed = sum(1 for r in rows if r[0] in ["success", "completed", "passed"])
                success_rate = completed / total
                trust = round(success_rate * 100.0, 1)
            else:
                # Default trust if no actions yet
                trust = 95.0
    except Exception:
        pass

    if agent["lifecycle_state"] == "terminated":
        trust = 10.0

    agent["trust_score"] = trust
    state["agents"][name] = agent
    save_state(state)
    return trust


def get_active_agents() -> list:
    """Get list of active agent classes."""
    state = load_state()
    return [
        agent["class"]
        for agent in state["agents"].values()
        if agent.get("lifecycle_state") in ["active", "idle", "paused"]
    ]


# ----------------- VERIFICATION TESTS (FR-091 to FR-100) -----------------


def verify_fr_091():
    agent = register_agent("Custom Planner", "Planner", ["planning"])
    assert agent["class"] == "Planner", "Planner Agent type unsupported."
    return True


def verify_fr_092():
    agent = register_agent("Custom Orchestrator", "Orchestrator", ["orchestration"])
    assert agent["class"] == "Orchestrator", "Orchestrator Agent type unsupported."
    return True


def verify_fr_093():
    agent = register_agent("Custom Executor", "Executor", ["executing"])
    assert agent["class"] == "Executor", "Executor Agent type unsupported."
    return True


def verify_fr_094():
    agent = register_agent("Custom Reviewer", "Reviewer", ["reviewing"])
    assert agent["class"] == "Reviewer", "Reviewer Agent type unsupported."
    return True


def verify_fr_095():
    agent = register_agent("Custom Governor", "Governor", ["governing"])
    assert agent["class"] == "Governor", "Governor Agent type unsupported."
    return True


def verify_fr_096():
    agent = register_agent("Custom Learner", "Learner", ["learning"])
    assert agent["class"] == "Learner", "Learner Agent type unsupported."
    return True


def verify_fr_097():
    agent = register_agent("Custom KM", "Knowledge Manager", ["indexing"])
    assert (
        agent["class"] == "Knowledge Manager"
    ), "Knowledge Manager Agent type unsupported."
    return True


def verify_fr_098():
    agent = register_agent("Capability Agent", "Executor", ["git_push", "docker_build"])
    assert "git_push" in agent["capabilities"], "Agent capabilities mapping failed."
    return True


def verify_fr_099():
    agent = update_agent_lifecycle("Executor Agent", "paused")
    assert agent["lifecycle_state"] == "paused", "Agent lifecycle update failed."
    return True


def verify_fr_100():
    trust = calculate_agent_trust("Governor Agent")
    assert trust > 0.0, "Agent trust scoring failed."
    return True


def run_self_tests():
    print("Running Agent Workforce self tests...")
    state = get_default_state()
    save_state(state)

    tests = [
        ("FR-091", verify_fr_091),
        ("FR-092", verify_fr_092),
        ("FR-093", verify_fr_093),
        ("FR-094", verify_fr_094),
        ("FR-095", verify_fr_095),
        ("FR-096", verify_fr_096),
        ("FR-097", verify_fr_097),
        ("FR-098", verify_fr_098),
        ("FR-099", verify_fr_099),
        ("FR-100", verify_fr_100),
    ]

    for code, fn in tests:
        try:
            fn()
            print(f"  [PASS] {code} verified.")
        except AssertionError as ae:
            print(f"  [FAIL] {code}: {ae}")
            raise ae

    print("All Agent Workforce Engine self tests completed successfully!")


if __name__ == "__main__":
    run_self_tests()
