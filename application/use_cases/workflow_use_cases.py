# application/use_cases/workflow_use_cases.py
import os
import time

from domains.workflow.workflow import Workflow
from infrastructure.storage.json_fallback_store import load_state, save_state

STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uawos_workflow_state.json"
)


def get_default_state() -> dict:
    return {
        "workflows": {
            "WRK-101": {
                "id": "WRK-101",
                "plan_id": "PLN-101",
                "title": "Optimized Funnel Refactor Workflow",
                "tasks": [
                    "DB Index Setup",
                    "Cache Configuration",
                    "Verification Tests",
                ],
                "dependencies": [],
                "state": "active",  # active, paused, terminated, completed
                "version": 1,
                "history": [],
                "governed": True,
            }
        }
    }


def create_workflow(
    plan_id: str,
    title: str,
    tasks: list,
    dependencies: list = None,
    governed: bool = True,
) -> dict:
    state = load_state()
    wid = f"WRK-{len(state['workflows']) + 101:03d}"

    wf = Workflow(
        id=wid,
        plan_id=plan_id,
        title=title,
        tasks=tasks,
        dependencies=dependencies or [],
        state="active",
        governed=governed,
    )

    state["workflows"][wid] = wf.to_dict()
    save_state(state)
    return state["workflows"][wid]


def generate_workflow(plan_id: str) -> dict:
    steps = ["Build Step 1", "Build Step 2"]
    try:
        plans_data = load_state()
        plan = plans_data["plans"].get(plan_id)
        if plan:
            steps = plan["steps"]
    except Exception:
        pass

    return create_workflow(
        plan_id=plan_id,
        title=f"Workflow from plan {plan_id}",
        tasks=[f"Orchestrate: {s}" for s in steps],
    )


def modify_workflow(workflow_id: str, updates: dict) -> dict:
    state = load_state()
    wf_dict = state["workflows"].get(workflow_id)
    if not wf_dict:
        raise ValueError(f"Workflow {workflow_id} not found.")

    wf = Workflow.from_dict(wf_dict)

    # Save to history
    snap = {k: v for k, v in wf.to_dict().items() if k != "history"}
    wf.history.append({"timestamp": time.time(), "state": snap})

    for k, v in updates.items():
        if k in ["title", "tasks", "dependencies", "state", "governed", "execution_mode", "temporal_run_id"]:
            setattr(wf, k, v)

    wf.version += 1
    state["workflows"][workflow_id] = wf.to_dict()
    save_state(state)
    return state["workflows"][workflow_id]


def pause_workflow(workflow_id: str) -> dict:
    return modify_workflow(workflow_id, {"state": "paused"})


def resume_workflow(workflow_id: str) -> dict:
    return modify_workflow(workflow_id, {"state": "active"})


def terminate_workflow(workflow_id: str) -> dict:
    return modify_workflow(workflow_id, {"state": "terminated"})


def simulate_workflow(workflow_id: str) -> dict:
    state = load_state()
    wf_dict = state["workflows"].get(workflow_id)
    if not wf_dict:
        raise ValueError(f"Workflow {workflow_id} not found.")

    wf = Workflow.from_dict(wf_dict)
    return wf.simulate()


def execute_workflow(workflow_id: str) -> dict:
    state = load_state()
    wf_dict = state["workflows"].get(workflow_id)
    if not wf_dict:
        raise ValueError(f"Workflow {workflow_id} not found.")

    wf = Workflow.from_dict(wf_dict)
    temporal_started = False
    run_id = None
    try:
        import asyncio

        from temporalio.client import Client

        async def _run():
            client = await Client.connect("localhost:7233")
            handle = await client.start_workflow(
                "UAWOSWorkflowOrchestrator", wf.to_dict(), id=workflow_id, task_queue="uawos-workflow-queue"
            )
            return handle.first_execution_run_id

        loop = asyncio.new_event_loop()
        run_id = loop.run_until_complete(_run())
        loop.close()
        temporal_started = True
    except Exception:
        pass

    updates = {"state": "active"}
    if temporal_started:
        updates["temporal_run_id"] = run_id
        updates["execution_mode"] = "temporal"
    else:
        updates["execution_mode"] = "simulation"

    return modify_workflow(workflow_id, updates)


def optimize_workflow(workflow_id: str) -> dict:
    state = load_state()
    wf_dict = state["workflows"].get(workflow_id)
    if not wf_dict:
        raise ValueError(f"Workflow {workflow_id} not found.")

    wf = Workflow.from_dict(wf_dict)
    optimized_tasks = wf.optimize()
    return modify_workflow(workflow_id, {"tasks": optimized_tasks})


def check_temporal_worker_queues() -> bool:
    import socket

    for port in [7233, 8233]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)
            s.connect(("127.0.0.1", port))
            s.close()
            return True
        except Exception:
            pass

    return os.environ.get("TEMPORAL_MOCK_ACTIVE", "true").lower() == "true"
