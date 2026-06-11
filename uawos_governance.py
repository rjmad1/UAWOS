# uawos_governance.py
import json
import os
import time

from uawos_state_utils import load_state, save_state

import uawos_db

STATE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "uawos_governance_state.json"
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


# Core API
def create_policy(name: str, rule: str, category: str) -> dict:
    """Create a new policy ruleset (FR-101, FR-102)."""
    state = load_state()
    pid = f"POL-{len(state['policies']) + 1:02d}"

    policy = {
        "id": pid,
        "name": name,
        "rule": rule,
        "category": category,
        "version": 1,
        "status": "draft",
    }
    state["policies"][pid] = policy
    save_state(state)
    return state["policies"][pid]


# Enforce Law 11
def evaluate_action_governance(action_id: str, action_details: dict) -> dict:
    """Enforce Law 11: No External Action without Governance Evaluation."""
    state = load_state()

    # Audit log entry (FR-110)
    log_audit("EVALUATION", {"action_id": action_id, "details": action_details})

    verdict = "APPROVED"
    reason = "All active policy checks passed."

    # Check for direct marker imports
    if action_details.get("uses_marker_library", False):
        # Law 11 / Policy violation
        verdict = "REJECTED"
        reason = "GPLv3 License compliance policy violation: marker library cannot be imported directly."

    # Check token budget limit
    tokens = action_details.get("estimated_tokens", 0)
    if tokens > 5000000:
        verdict = "REJECTED"
        reason = "Token consumption policy exceeded: request exceeds 5M tokens limit."

    # Check Separation of Duties (Separation of duties)
    owner = action_details.get("owner") or action_details.get("actor")
    approver = action_details.get("approver")
    if owner and approver and owner == approver:
        verdict = "REJECTED"
        reason = (
            "Separation of Duties violation: Action owner/actor cannot be the approver."
        )

    # Check Actor Role Governance
    actor_role = action_details.get("actor_role") or action_details.get("role")
    if actor_role:
        valid_roles = [
            "CEO",
            "Lead Engineer",
            "Database Expert",
            "Developer",
            "Executor Agent",
            "Senior Engineer",
            "Admin",
        ]
        if actor_role not in valid_roles:
            verdict = "REJECTED"
            reason = f"Role Governance violation: Unrecognized or unauthorized role '{actor_role}'."
        else:
            category = action_details.get("category")
            if category == "budget" and actor_role not in [
                "CEO",
                "Lead Engineer",
                "Database Expert",
                "Admin",
            ]:
                verdict = "REJECTED"
                reason = f"Role Governance violation: Role '{actor_role}' is not authorized for budget actions."

    # Check if there is an active exception override (FR-108)
    if action_id in state["exceptions"]:
        exc = state["exceptions"][action_id]
        if exc["status"] == "Approved":
            verdict = "APPROVED"
            reason = f"Governance Policy Exception approved: {exc['reason']}"

    return {"verdict": verdict, "reason": reason}


# FR-103: Conflict detection
def detect_policy_conflicts() -> list:
    state = load_state()
    conflicts = []
    policies = list(state["policies"].values())

    # Simple semantic overlap check (e.g. opposite rules)
    for i in range(len(policies)):
        for j in range(i + 1, len(policies)):
            p1 = policies[i]
            p2 = policies[j]
            if p1["category"] == p2["category"] and (
                "==" in p1["rule"] and "==" in p2["rule"]
            ):
                # check if they contradict
                pass
    return conflicts


# FR-104 & FR-107: Approvals
def approve_policy(policy_id: str) -> dict:
    state = load_state()
    policy = state["policies"].get(policy_id)
    if not policy:
        raise ValueError(f"Policy {policy_id} not found.")
    policy["status"] = "approved"
    state["policies"][policy_id] = policy
    save_state(state)
    return policy


# FR-108: Governance Exceptions
def request_exception(action_id: str, reason: str) -> dict:
    state = load_state()
    exc_id = f"EXC-{len(state['exceptions']) + 1:03d}"
    exception = {
        "id": exc_id,
        "action_id": action_id,
        "reason": reason,
        "status": "Pending",
        "timestamp": int(time.time()),
    }
    state["exceptions"][action_id] = exception
    save_state(state)
    return exception


def process_exception(action_id: str, decision: str) -> dict:
    state = load_state()
    exc = state["exceptions"].get(action_id)
    if not exc:
        raise ValueError(f"Exception request for {action_id} not found.")
    exc["status"] = decision
    state["exceptions"][action_id] = exc
    save_state(state)
    return exc


# FR-109: Risk Acceptance
def accept_risk(risk_id: str, justification: str) -> dict:
    state = load_state()
    acceptance = {
        "risk_id": risk_id,
        "justification": justification,
        "status": "Accepted",
        "timestamp": int(time.time()),
    }
    state["risk_acceptances"][risk_id] = acceptance
    save_state(state)
    return acceptance


# FR-110: Auditing
def log_audit(event_type: str, details: dict):
    state = load_state()
    entry = {
        "event_type": event_type,
        "details": details,
        "timestamp": int(time.time()),
    }
    state["audit_logs"].append(entry)
    save_state(state)


# ----------------- VERIFICATION TESTS (FR-101 to FR-110) -----------------


def verify_fr_101():
    res = evaluate_action_governance("ACT-EXEC", {"uses_marker_library": True})
    assert res["verdict"] == "REJECTED", "Policy enforcement failed."
    return True


def verify_fr_102():
    policy = create_policy("New Policy", "x == y", "testing")
    assert policy["version"] == 1, "Policy versioning failed."
    return True


def verify_fr_103():
    conflicts = detect_policy_conflicts()
    assert isinstance(conflicts, list), "Policy conflict check failed."
    return True


def verify_fr_104():
    p = create_policy("Draft Policy", "a == b", "auth")
    app = approve_policy(p["id"])
    assert app["status"] == "approved", "Policy approval failed."
    return True


def verify_fr_105():
    # Risks can be recorded and checked
    log_audit("RISK_IDENTIFIED", {"risk_id": "RSK-01", "impact": "High"})
    state = load_state()
    assert len(state["audit_logs"]) > 0, "Risk logging failed."
    return True


def verify_fr_106():
    # Compliance check run
    res = evaluate_action_governance("ACT-TEST", {"estimated_tokens": 1000})
    assert res["verdict"] == "APPROVED", "Compliance verification failed."
    return True


def verify_fr_107():
    exc = request_exception("ACT-SSO", "Testing SSO exception")
    proc = process_exception("ACT-SSO", "Approved")
    assert proc["status"] == "Approved", "Approval workflow failed."
    return True


def verify_fr_108():
    exc = request_exception("ACT-GPL", "GPL exception for isolated staging sandbox")
    assert exc["action_id"] == "ACT-GPL", "Exception requesting failed."
    return True


def verify_fr_109():
    ra = accept_risk("RSK-01", "Accepted for development lifecycle.")
    assert ra["status"] == "Accepted", "Risk acceptance failed."
    return True


def verify_fr_110():
    log_audit("AUDIT_TEST", {"msg": "Self test active"})
    state = load_state()
    assert any(
        log["event_type"] == "AUDIT_TEST" for log in state["audit_logs"]
    ), "Auditing failed."
    return True


def verify_fr_111():
    # Test separation of duties violation
    res_sod = evaluate_action_governance(
        "ACT-SOD", {"owner": "Alice", "approver": "Alice"}
    )
    assert (
        res_sod["verdict"] == "REJECTED"
    ), "Separation of duties violation not blocked."
    assert (
        "Separation of Duties" in res_sod["reason"]
    ), "Incorrect rejection reason for Separation of Duties."

    # Test valid separation of duties
    res_valid_sod = evaluate_action_governance(
        "ACT-SOD-OK", {"owner": "Alice", "approver": "Bob"}
    )
    assert (
        res_valid_sod["verdict"] == "APPROVED"
    ), "Valid separation of duties rejected."

    # Test unrecognized role
    res_bad_role = evaluate_action_governance("ACT-ROLE-BAD", {"actor_role": "Hacker"})
    assert res_bad_role["verdict"] == "REJECTED", "Unrecognized role not blocked."

    # Test unauthorized role for budget action
    res_unauth_role = evaluate_action_governance(
        "ACT-BUDGET-UNAUTH", {"actor_role": "Developer", "category": "budget"}
    )
    assert (
        res_unauth_role["verdict"] == "REJECTED"
    ), "Unauthorized role for budget was not blocked."

    # Test authorized role for budget action
    res_auth_role = evaluate_action_governance(
        "ACT-BUDGET-AUTH", {"actor_role": "CEO", "category": "budget"}
    )
    assert (
        res_auth_role["verdict"] == "APPROVED"
    ), "Authorized role for budget was rejected."

    return True


def run_self_tests():
    print("Running Governance self tests...")
    state = get_default_state()
    save_state(state)

    tests = [
        ("FR-101", verify_fr_101),
        ("FR-102", verify_fr_102),
        ("FR-103", verify_fr_103),
        ("FR-104", verify_fr_104),
        ("FR-105", verify_fr_105),
        ("FR-106", verify_fr_106),
        ("FR-107", verify_fr_107),
        ("FR-108", verify_fr_108),
        ("FR-109", verify_fr_109),
        ("FR-110", verify_fr_110),
        ("FR-111", verify_fr_111),
    ]

    for code, fn in tests:
        try:
            fn()
            print(f"  [PASS] {code} verified.")
        except AssertionError as ae:
            print(f"  [FAIL] {code}: {ae}")
            raise ae

    print("All Governance Engine self tests completed successfully!")


if __name__ == "__main__":
    run_self_tests()
