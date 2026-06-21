# interfaces/rest/requirements.py
import os

from fastapi import APIRouter, Header, HTTPException, Request

import uawos_requirement_studio
from interfaces.rest.auth import verify_secure_token

router = APIRouter()


@router.get("/api/requirement/list")
def get_requirement_list():
    try:
        return uawos_requirement_studio.load_state(
            uawos_requirement_studio.STATE_FILE, uawos_requirement_studio.get_default_state
        )
    except Exception as e:
        return {"error": str(e)}


@router.post("/api/requirement/submit")
async def requirement_submit(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    try:
        payload = await request.json()
        title = payload.get("title", "New Requirement")
        text = payload.get("text", "")
        return uawos_requirement_studio.submit_new_requirement(title, text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/requirement/clarify")
async def requirement_clarify(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    try:
        payload = await request.json()
        req_id = payload.get("requirement_id", "")
        answers = payload.get("answers", {})
        waive = payload.get("waive", False)
        return uawos_requirement_studio.update_clarifications(req_id, answers, waive)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/requirement/author")
async def requirement_author(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    try:
        payload = await request.json()
        req_id = payload.get("requirement_id", "")
        return uawos_requirement_studio.author_proposition(req_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/requirement/absorb")
async def requirement_absorb(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    try:
        payload = await request.json()
        req_id = payload.get("requirement_id", "")
        return uawos_requirement_studio.absorb_requirement(req_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/requirement/publish")
async def requirement_publish(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    try:
        payload = await request.json()
        cand_id = payload.get("roadmap_id", "")
        return uawos_requirement_studio.publish_roadmap_item(cand_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/requirement/direct_ingest")
async def requirement_direct_ingest(
    request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)
):
    verify_secure_token(x_uawos_token, authorization)
    try:
        payload = await request.json()
        req_id = payload.get("requirement_id", "")
        answers = payload.get("answers", {})
        waive = payload.get("waive", False)
        return uawos_requirement_studio.direct_ingest_to_backlog(req_id, answers, waive)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/requirement/reset")
def requirement_reset(x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    try:
        state = uawos_requirement_studio.get_default_state()
        uawos_requirement_studio.save_state(uawos_requirement_studio.STATE_FILE, state)
        if os.path.exists(uawos_requirement_studio.STATE_FILE):
            os.remove(uawos_requirement_studio.STATE_FILE)
        return {"status": "SUCCESS"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
