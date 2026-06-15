# infrastructure/security/opa_client.py
import json
import os
import urllib.request
import urllib.error

OPA_HOST = os.environ.get("OPA_HOST", "127.0.0.1")
OPA_PORT = int(os.environ.get("OPA_PORT", 8181))
OPA_URL = f"http://{OPA_HOST}:{OPA_PORT}"

# Track policy upload status in-memory
_policy_uploaded = False

REGO_POLICY = """package uawos.governance

import rego.v1

default allow := false
default reason := "No policy matched or check failed."

allow if {
    not uses_marker_library_violation
    not token_limit_violation
    not separation_of_duties_violation
    not unauthorized_role_violation
    not unauthorized_budget_role_violation
}

reason := "All active policy checks passed." if {
    allow
}

uses_marker_library_violation if {
    input.uses_marker_library == true
}

reason := "GPLv3 License compliance policy violation: marker library cannot be imported directly." if {
    uses_marker_library_violation
}

token_limit_violation if {
    input.estimated_tokens > 5000000
}

reason := "Token consumption policy exceeded: request exceeds 5M tokens limit." if {
    token_limit_violation
}

separation_of_duties_violation if {
    input.owner == input.approver
    input.owner != null
    input.approver != null
}

reason := "Separation of Duties violation: Action owner/actor cannot be the approver." if {
    separation_of_duties_violation
}

unauthorized_role_violation if {
    input.actor_role
    valid_roles := ["CEO", "Lead Engineer", "Database Expert", "Developer", "Executor Agent", "Senior Engineer", "Admin"]
    count({role | role := valid_roles[_]; role == input.actor_role}) == 0
}

reason := "Role Governance violation: Unrecognized or unauthorized role." if {
    unauthorized_role_violation
}

unauthorized_budget_role_violation if {
    input.category == "budget"
    input.actor_role
    budget_roles := ["CEO", "Lead Engineer", "Database Expert", "Admin"]
    count({role | role := budget_roles[_]; role == input.actor_role}) == 0
}

reason := "Role Governance violation: Role is not authorized for budget actions." if {
    unauthorized_budget_role_violation
}
"""


def upload_opa_policy() -> bool:
    """Dynamically register the Rego policy on the stateless OPA container."""
    global _policy_uploaded
    if _policy_uploaded:
        return True
    try:
        url = f"{OPA_URL}/v1/policies/uawos_governance"
        req = urllib.request.Request(
            url,
            data=REGO_POLICY.encode("utf-8"),
            method="PUT",
            headers={"Content-Type": "text/plain"},
        )
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            if resp.status == 200:
                _policy_uploaded = True
                return True
    except Exception:
        pass
    return False


def evaluate_via_opa(action_details: dict) -> dict:
    """Query the OPA REST API endpoint to evaluate Rego rules."""
    global _policy_uploaded
    if not upload_opa_policy():
        return None
    try:
        url = f"{OPA_URL}/v1/data/uawos/governance"
        req_data = json.dumps({"input": action_details}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            result = res.get("result", {})
            if result:
                verdict = "APPROVED" if result.get("allow") else "REJECTED"
                reason = result.get("reason", "All active policy checks passed.")
                return {"verdict": verdict, "reason": reason}
            else:
                # OPA returned empty result - policy likely lost/not loaded in OPA
                _policy_uploaded = False
    except Exception:
        # Reset state on connection errors to force re-upload on next retry
        _policy_uploaded = False
    return None
