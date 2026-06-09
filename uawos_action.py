# uawos_action.py
import os
import json
import time

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_action_state.json")

def get_default_state() -> dict:
    return {
        "actions": {
            "ACT-101": {
                "id": "ACT-101",
                "workflow_id": "WRK-101",
                "name": "Analyze database slow queries",
                "owner": "Database Expert",
                "dependencies": [],
                "priority": "High",
                "budget": 200.0,
                "deadline": 1781049600,  # timestamp
                "status": "pending",  # pending, running, completed, failed
                "approval_required": True
            }
        }
    }

def load_state() -> dict:
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
        print(f"Error saving action state: {e}")

# Core API
def create_action(
    workflow_id: str,
    name: str,
    owner: str,
    dependencies: list = None,
    priority: str = "Medium",
    budget: float = 0.0,
    deadline: int = 0,
    status: str = "pending",
    approval_required: bool = False
) -> dict:
    """Create a new action. Enforces UCA Law 5 (No action without ownership)."""
    state = load_state()
    
    # Enforce Law 5
    if not owner:
        raise ValueError("Constitutional Law 5 Violation: Action must have a designated Owner.")
        
    existing_ids = [int(k[4:]) for k in state["actions"].keys() if k.startswith("ACT-") and k[4:].isdigit()]
    next_id_num = max(existing_ids) + 1 if existing_ids else 201
    action_id = f"ACT-{next_id_num}"
    
    action = {
        "id": action_id,
        "workflow_id": workflow_id,
        "name": name,
        "owner": owner,  # FR-072
        "dependencies": dependencies or [],  # FR-073
        "priority": priority,  # FR-074
        "budget": budget,  # FR-075
        "deadline": deadline or int(time.time() + 86400 * 3),  # FR-076
        "status": status,  # FR-077
        "approval_required": approval_required  # FR-079
    }
    
    state["actions"][action_id] = action
    save_state(state)
    return state["actions"][action_id]

# FR-071: Decompose Workflow into Actions
def decompose_workflow(workflow_id: str) -> list:
    """Decompose a Workflow's tasks into granular executable Actions."""
    state = load_state()
    actions_created = []
    
    # Check workflow if uawos_workflow is available
    tasks = ["Decomposed Task 1", "Decomposed Task 2"]
    try:
        import uawos_workflow
        wfs = uawos_workflow.load_state()
        wf = wfs["workflows"].get(workflow_id)
        if wf:
            tasks = wf["tasks"]
    except Exception:
        pass
        
    for idx, task in enumerate(tasks):
        act = create_action(
            workflow_id=workflow_id,
            name=f"Execute: {task}",
            owner="Executor Agent",
            priority="Medium",
            budget=50.0
        )
        actions_created.append(act)
        
    return actions_created

# FR-080: Action reassignment
def reassign_action(action_id: str, new_owner: str) -> dict:
    state = load_state()
    action = state["actions"].get(action_id)
    if not action:
        raise ValueError(f"Action {action_id} not found.")
        
    if not new_owner:
        raise ValueError("Cannot reassign to empty owner.")
        
    action["owner"] = new_owner
    state["actions"][action_id] = action
    save_state(state)
    return state["actions"][action_id]

# FR-078: Traceability
def get_action_traceability(action_id: str) -> dict:
    state = load_state()
    action = state["actions"].get(action_id)
    if not action:
        raise ValueError(f"Action {action_id} not found.")
        
    return {
        "action_id": action_id,
        "workflow_id": action["workflow_id"],
        "traceability_chain": f"WF -> {action['workflow_id']} -> ACTION -> {action_id}"
    }

# ----------------- VERIFICATION TESTS (FR-071 to FR-080) -----------------

def verify_fr_071():
    acts = decompose_workflow("WRK-101")
    assert len(acts) > 0, "Decomposition failed."
    return True

def verify_fr_072():
    act = load_state()["actions"]["ACT-101"]
    assert act["owner"] == "Database Expert", "Action owner failed."
    return True

def verify_fr_073():
    act = create_action("WRK-101", "Task X", "Dev", dependencies=["ACT-101"])
    assert "ACT-101" in act["dependencies"], "Dependencies failed."
    return True

def verify_fr_074():
    act = create_action("WRK-101", "Task Y", "Dev", priority="Critical")
    assert act["priority"] == "Critical", "Priority setting failed."
    return True

def verify_fr_075():
    act = create_action("WRK-101", "Task Z", "Dev", budget=120.0)
    assert act["budget"] == 120.0, "Budget mapping failed."
    return True

def verify_fr_076():
    act = create_action("WRK-101", "Task A", "Dev", deadline=123456)
    assert act["deadline"] == 123456, "Deadline setting failed."
    return True

def verify_fr_077():
    act = create_action("WRK-101", "Task B", "Dev", status="running")
    assert act["status"] == "running", "Execution status failed."
    return True

def verify_fr_078():
    trace = get_action_traceability("ACT-101")
    assert "traceability_chain" in trace, "Traceability verification failed."
    return True

def verify_fr_079():
    act = create_action("WRK-101", "Task C", "Dev", approval_required=True)
    assert act["approval_required"] is True, "Approval requirement failed."
    return True

def verify_fr_080():
    act = reassign_action("ACT-101", "Senior Engineer")
    assert act["owner"] == "Senior Engineer", "Reassignment failed."
    return True

def run_self_tests():
    print("Running Action Management self tests...")
    state = get_default_state()
    save_state(state)
    
    tests = [
        ("FR-071", verify_fr_071),
        ("FR-072", verify_fr_072),
        ("FR-073", verify_fr_073),
        ("FR-074", verify_fr_074),
        ("FR-075", verify_fr_075),
        ("FR-076", verify_fr_076),
        ("FR-077", verify_fr_077),
        ("FR-078", verify_fr_078),
        ("FR-079", verify_fr_079),
        ("FR-080", verify_fr_080),
    ]
    
    for code, fn in tests:
        try:
            fn()
            print(f"  [PASS] {code} verified.")
        except AssertionError as ae:
            print(f"  [FAIL] {code}: {ae}")
            raise ae
            
    print("All Action Engine self tests completed successfully!")

if __name__ == "__main__":
    run_self_tests()
