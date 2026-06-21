# interfaces/rest/objectives.py
from fastapi import APIRouter, Header, HTTPException, Request

from application.use_cases import objective_use_cases
from interfaces.rest.auth import verify_secure_token

router = APIRouter()


@router.get("/api/objective/list")
def get_objective_list():
    try:
        return objective_use_cases.load_state(objective_use_cases.STATE_FILE, objective_use_cases.get_default_state)
    except Exception as e:
        return {"error": str(e)}


@router.get("/api/objective/conflicts")
def get_objective_conflicts():
    try:
        return {"conflicts": objective_use_cases.detect_objective_conflicts()}
    except Exception as e:
        return {"error": str(e)}


@router.post("/api/objective/submit")
async def objective_submit(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    try:
        payload = await request.json()
        text = payload.get("text", "")
        input_type = payload.get("input_type", "text")
        owner = payload.get("owner", "")
        sponsor = payload.get("sponsor", "")
        source_uri = payload.get("source_uri", "")
        return objective_use_cases.create_objective_from_input(text, input_type, owner, sponsor, source_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/objective/action")
async def objective_action(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    try:
        payload = await request.json()
        action = payload.get("action", "")
        obj_id = payload.get("objective_id", "")
        result = {"status": "success"}

        if action == "pause":
            result["data"] = objective_use_cases.pause_objective(obj_id)
        elif action == "cancel":
            result["data"] = objective_use_cases.cancel_objective(obj_id)
        elif action == "archive":
            result["data"] = objective_use_cases.archive_objective(obj_id)
        elif action == "restore":
            result["data"] = objective_use_cases.restore_objective(obj_id)
        elif action == "resume":
            result["data"] = objective_use_cases.resume_objective(obj_id)
        elif action == "update":
            updates = payload.get("updates", {})
            result["data"] = objective_use_cases.update_objective(obj_id, updates)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
