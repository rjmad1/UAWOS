# interfaces/rest/governance.py
from fastapi import APIRouter, Header, HTTPException

import uawos_proactive_governance
from interfaces.rest.auth import verify_secure_token

router = APIRouter()


@router.get("/api/governance/status")
def get_governance_status():
    try:
        return uawos_proactive_governance.run_full_governance_audit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/governance/run")
def run_governance_audit(x_uawos_token: str = Header(None), authorization: str = Header(None)):
    verify_secure_token(x_uawos_token, authorization)
    try:
        return uawos_proactive_governance.run_full_governance_audit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
