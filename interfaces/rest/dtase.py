# interfaces/rest/dtase.py
from fastapi import APIRouter, Header, HTTPException, Request

import uawos_dtase
from interfaces.rest.auth import verify_secure_token

router = APIRouter()


@router.post("/api/dtase/analyze")
async def analyze_dtase(request: Request, x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    try:
        payload = await request.json()
        text = payload.get("text", "")
        return uawos_dtase.analyze_unstructured_input(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
