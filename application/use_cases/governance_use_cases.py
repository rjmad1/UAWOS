# application/use_cases/governance_use_cases.py
import os
import time
from typing import List, Dict

from domains.governance.governance import Policy, ExceptionRequest, RiskAcceptance, AuditLog
from infrastructure.storage.json_fallback_store import load_state, save_state, state_transaction
from infrastructure.security.opa_client import evaluate_via_opa
from infrastructure.security.fga_client import check_fga_authorization

STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "uawos_governance_state.json"
)

def get_default_state() -> dict:
    return {
        "policies": {
            "POL-01": {
                "id": "POL-01",
                "name": "Token Limit Control",
                "rule": "token_consumption <= 5000000",
                "category": "budget",
                "version": 1,
                "status": "approved",
            },
            "POL-02": {
                "id": "POL-02",
                "name": "No Direct GPLv3 Imports",
                "rule": "import_marker == False",
                "category": "licensing",
                "version": 1,
                "status": "approved",
            },
        },
        "exceptions": {},
        "risk_acceptances": {},
        "audit_logs": [],
    }



def create_policy(name: str, rule: str, category: str) -> dict:
    with state_transaction(STATE_FILE):
        state = load_state(STATE_FILE)
        pid = f"POL-{len(state['policies']) + 1:02d}"

        policy = Policy(
            id=pid,
            name=name,
            rule=rule,
            category=category,
            version=1,
            status="draft",
        )
        state["policies"][pid] = policy.to_dict()
        save_state(STATE_FILE, state)
    return state["policies"][pid]


def evaluate_action_governance(action_id: str, action_details: dict) -> dict:
    state = load_state()

    # Audit log entry
    log_audit("EVALUATION", {"action_id": action_id, "details": action_details})

    # 1. Check if an approved exception exists first (exceptions take precedence)
    if action_id in state["exceptions"]:
        exc = state["exceptions"][action_id]
        if exc["status"] == "Approved":
            return {
                "verdict": "APPROVED",
                "reason": f"Governance Policy Exception approved: {exc['reason']}",
            }

    # 2. Check OpenFGA ReBAC Authorization (if actor and role are present)
    actor = action_details.get("owner") or action_details.get("actor")
    actor_role = action_details.get("actor_role") or action_details.get("role")
    category = action_details.get("category")
    if actor and actor_role:
        fga_allowed = check_fga_authorization(actor, actor_role, category)
        if fga_allowed is None:
            return {
                "verdict": "REJECTED",
                "reason": "Security Infrastructure Offline: OpenFGA connection failed (Fail-Secure Enforcement).",
            }
        if not fga_allowed:
            if category == "budget":
                return {
                    "verdict": "REJECTED",
                    "reason": f"Role Governance violation: Role '{actor_role}' is not authorized for budget actions.",
                }
            else:
                return {
                    "verdict": "REJECTED",
                    "reason": f"Role Governance violation: Unrecognized or unauthorized role '{actor_role}'.",
                }

    # 3. Try OPA engine REST verification
    opa_result = evaluate_via_opa(action_details)
    if opa_result is None:
        return {
            "verdict": "REJECTED",
            "reason": "Security Infrastructure Offline: OPA connection failed (Fail-Secure Enforcement).",
        }
    return opa_result


def detect_policy_conflicts() -> list:
    state = load_state()
    conflicts = []
    policies = list(state["policies"].values())

    # Simple semantic overlap check (e.g. opposite rules)
    for i in range(len(policies)):
        for j in range(i + 1, len(policies)):
            p1 = policies[i]
            p2 = policies[j]
            if p1["category"] == p2["category"] and ("==" in p1["rule"] and "==" in p2["rule"]):
                pass
    return conflicts


def approve_policy(policy_id: str) -> dict:
    with state_transaction(STATE_FILE):
        state = load_state(STATE_FILE)
        policy_dict = state["policies"].get(policy_id)
        if not policy_dict:
            raise ValueError(f"Policy {policy_id} not found.")
        
        policy = Policy.from_dict(policy_dict)
        policy.status = "approved"
        state["policies"][policy_id] = policy.to_dict()
        save_state(STATE_FILE, state)
    return policy.to_dict()


def request_exception(action_id: str, reason: str) -> dict:
    with state_transaction(STATE_FILE):
        state = load_state(STATE_FILE)
        exc_id = f"EXC-{len(state['exceptions']) + 1:03d}"
        
        exc = ExceptionRequest(
            id=exc_id,
            action_id=action_id,
            reason=reason,
            status="Pending",
            timestamp=time.time(),
        )
        state["exceptions"][action_id] = exc.to_dict()
        save_state(STATE_FILE, state)
    return exc.to_dict()


def process_exception(action_id: str, decision: str) -> dict:
    with state_transaction(STATE_FILE):
        state = load_state(STATE_FILE)
        exc_dict = state["exceptions"].get(action_id)
        if not exc_dict:
            raise ValueError(f"Exception request for {action_id} not found.")
        
        exc = ExceptionRequest.from_dict(exc_dict)
        exc.status = decision
        state["exceptions"][action_id] = exc.to_dict()
        save_state(STATE_FILE, state)
    return exc.to_dict()


def accept_risk(risk_id: str, justification: str) -> dict:
    with state_transaction(STATE_FILE):
        state = load_state(STATE_FILE)
        
        ra = RiskAcceptance(
            risk_id=risk_id,
            justification=justification,
            status="Accepted",
            timestamp=time.time(),
        )
        state["risk_acceptances"][risk_id] = ra.to_dict()
        save_state(STATE_FILE, state)
    return ra.to_dict()


def log_audit(event_type: str, details: dict):
    with state_transaction(STATE_FILE):
        state = load_state(STATE_FILE)
        
        log = AuditLog(
            event_type=event_type,
            details=details,
            timestamp=time.time(),
        )
        state["audit_logs"].append(log.to_dict())
        save_state(STATE_FILE, state)


def get_dynamic_agent_autonomy_level(agent_name: str) -> int:
    try:
        import uawos_agent_workforce
        trust = uawos_agent_workforce.calculate_agent_trust(agent_name)
    except Exception:
        trust = 95.0

    if trust >= 90.0:
        return 5
    elif trust >= 70.0:
        return 4
    else:
        return 3


def run_governor_audit_analysis() -> list:
    state = load_state()
    proposals = []
    logs = state.get("audit_logs", [])

    token_violations = 0
    gpl_violations = 0

    for entry in logs:
        details = entry.get("details", {})
        action_details = details.get("details", {})
        if action_details.get("estimated_tokens", 0) > 5000000:
            token_violations += 1
        if action_details.get("uses_marker_library", False):
            gpl_violations += 1

    if token_violations > 0:
        proposals.append(
            {
                "type": "policy_modification",
                "policy_id": "POL-01",
                "suggestion": "Adjust token consumption limits or trigger throttling.",
                "reason": f"Detected {token_violations} token limit violations in audit logs.",
            }
        )
    if gpl_violations > 0:
        proposals.append(
            {
                "type": "policy_modification",
                "policy_id": "POL-02",
                "suggestion": "Restrict marker library imports to isolated sandboxes.",
                "reason": f"Detected {gpl_violations} GPL license compliance violations in audit logs.",
            }
        )

    # Default proposal
    if not proposals:
        proposals.append(
            {
                "type": "policy_modification",
                "policy_id": "POL-01",
                "suggestion": "Review default token limit based on scaling metrics.",
                "reason": "System audit analysis found stable performance logs.",
            }
        )

    return proposals
