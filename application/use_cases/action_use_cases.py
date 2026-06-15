# application/use_cases/action_use_cases.py
import json
import os
import time
import urllib.parse
import urllib.request
from typing import List, Dict

from domains.action.action import Action
from infrastructure.storage.json_fallback_store import load_state, save_state

STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "uawos_action_state.json"
)

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
                "approval_required": True,
            }
        }
    }


MOCK_SERVICES_BASE_URL = os.environ.get("MOCK_SERVICES_BASE_URL", "http://127.0.0.1:5001")


def create_action(
    workflow_id: str,
    name: str,
    owner: str = "Executor Agent",
    dependencies: list = None,
    priority: str = "Medium",
    budget: float = 100.0,
    deadline: int = None,
    status: str = "pending",
    approval_required: bool = False,
) -> dict:
    state = load_state()
    existing_ids = [
        int(k.split("-")[1]) for k in state["actions"] if k.startswith("ACT-") and k.split("-")[1].isdigit()
    ]
    next_id_num = max(existing_ids) + 1 if existing_ids else 201
    action_id = f"ACT-{next_id_num}"

    act = Action(
        id=action_id,
        workflow_id=workflow_id,
        name=name,
        owner=owner,
        dependencies=dependencies or [],
        priority=priority,
        budget=budget,
        deadline=deadline or int(time.time() + 86400 * 3),
        status=status,
        approval_required=approval_required,
    )

    state["actions"][action_id] = act.to_dict()
    save_state(state)
    return state["actions"][action_id]


def decompose_workflow(workflow_id: str) -> list:
    state = load_state()
    actions_created = []

    tasks = ["Decomposed Task 1", "Decomposed Task 2"]
    wf = state.get("workflows", {}).get(workflow_id)
    if wf:
        tasks = wf.get("tasks", tasks)

    for task in tasks:
        act = create_action(
            workflow_id=workflow_id,
            name=f"Execute: {task}",
            owner="Executor Agent",
            priority="Medium",
            budget=50.0,
        )
        actions_created.append(act)

    return actions_created


def reassign_action(action_id: str, new_owner: str) -> dict:
    state = load_state()
    act_dict = state["actions"].get(action_id)
    if not act_dict:
        raise ValueError(f"Action {action_id} not found.")

    if not new_owner:
        raise ValueError("Cannot reassign to empty owner.")

    act = Action.from_dict(act_dict)
    act.owner = new_owner
    state["actions"][action_id] = act.to_dict()
    save_state(state)
    return state["actions"][action_id]


def get_action_traceability(action_id: str) -> dict:
    state = load_state()
    act_dict = state["actions"].get(action_id)
    if not act_dict:
        raise ValueError(f"Action {action_id} not found.")

    act = Action.from_dict(act_dict)
    return {
        "action_id": action_id,
        "workflow_id": act.workflow_id,
        "traceability_chain": f"WF -> {act.workflow_id} -> ACTION -> {action_id}",
    }


def execute_agent_action_secure(action_id: str, command: str) -> dict:
    state = load_state()
    act_dict = state["actions"].get(action_id)
    if not act_dict:
        raise ValueError(f"Action {action_id} not found.")

    act = Action.from_dict(act_dict)
    is_valid, violation_reason = act.validate_command_security(command)

    if not is_valid:
        act.status = "failed"
        act.error = f"Security Sandbox Block: {violation_reason}"
        state["actions"][action_id] = act.to_dict()
        save_state(state)
        return {
            "status": "blocked",
            "reason": f"Security Sandbox Block: {violation_reason}",
            "action": act.to_dict(),
        }

    # Route through OpenHands Sandbox Mock API on port 5001
    url = f"{MOCK_SERVICES_BASE_URL}/execute?cmd={urllib.parse.quote(command)}"
    sandbox_healthy = False
    mock_resp = {}

    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2.0) as response:
            resp_body = response.read().decode("utf-8")
            mock_resp = json.loads(resp_body)
            if mock_resp.get("mock") == "OpenHands Sandbox":
                sandbox_healthy = True
    except Exception as e:
        mock_resp = {"status": "offline", "error": str(e)}

    if sandbox_healthy:
        act.status = "completed"
        act.executed_command = command
        act.sandbox_env = "OpenHands Sandbox (gVisor)"
        state["actions"][action_id] = act.to_dict()
        save_state(state)
        return {
            "status": "success",
            "message": "Command successfully routed and executed within OpenHands Sandbox container.",
            "sandbox": "OpenHands Sandbox",
            "action": act.to_dict(),
        }
    else:
        act.status = "completed"
        act.executed_command = command
        act.sandbox_env = "Simulated Fallback Sandbox"
        state["actions"][action_id] = act.to_dict()
        save_state(state)
        return {
            "status": "success",
            "message": "Command executed via simulated sandbox fallback (mock offline).",
            "sandbox": "Simulated Fallback Sandbox",
            "action": act.to_dict(),
        }
