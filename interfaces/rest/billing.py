# interfaces/rest/billing.py
from fastapi import APIRouter, Header, HTTPException, Request

from application.use_cases import billing_use_cases
from interfaces.rest.auth import verify_secure_token

router = APIRouter()


@router.get("/api/budget/status")
def get_budget_status():
    try:
        return billing_use_cases.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/budget/action")
async def budget_action(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    try:
        payload = await request.json()
        action = payload.get("action", "")
        result = {"status": "success"}

        if action == "record_tokens":
            agent = payload.get("agent", "Executor Agent")
            model = payload.get("model", "tinyllama")
            tokens_in = int(payload.get("tokens_in", 10000))
            tokens_out = int(payload.get("tokens_out", 5000))
            tokens_reasoning = int(payload.get("tokens_reasoning", 0))
            billing_use_cases.record_agent_cost(agent, model, tokens_in, tokens_out, tokens_reasoning)
            result["message"] = f"Recorded token usage for {agent}."
        elif action == "adjust_budget":
            obj_id = payload.get("objective_id", "")
            name = payload.get("name", "")
            amount = float(payload.get("amount", 0.0))
            billing_use_cases.allocate_objective_budget(obj_id, name, amount)
            result["message"] = f"Adjusted budget for {obj_id} to ${amount:.2f}."
        elif action == "approve_request":
            app_id = payload.get("approval_id", "")
            decision = payload.get("decision", "Approved")
            billing_use_cases.process_approval_request(app_id, decision)
            result["message"] = f"Processed approval {app_id} as {decision}."
        elif action == "check_governance":
            obj_id = payload.get("objective_id", "")
            gov = billing_use_cases.evaluate_cost_governance(obj_id)
            result["gov"] = gov
            result["message"] = f"Evaluated governance for {obj_id}."
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
