# uawos_governance.py
import os
import time

from uawos_state_utils import load_state, save_state

from application.use_cases.governance_use_cases import (
    create_policy,
    evaluate_action_governance,
    detect_policy_conflicts,
    approve_policy,
    request_exception,
    process_exception,
    accept_risk,
    log_audit,
    get_dynamic_agent_autonomy_level,
    run_governor_audit_analysis,
)

# Exposed variables for compatibility/tests
OPA_HOST = os.environ.get("OPA_HOST", "127.0.0.1")
OPA_PORT = int(os.environ.get("OPA_PORT", 8181))
OPA_URL = f"http://{OPA_HOST}:{OPA_PORT}"

OPENFGA_HOST = os.environ.get("OPENFGA_HOST", "127.0.0.1")
OPENFGA_PORT = int(os.environ.get("OPENFGA_PORT", 8083))
OPENFGA_URL = f"http://{OPENFGA_HOST}:{OPENFGA_PORT}"

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uawos_governance_state.json")


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
    request_exception("ACT-SSO", "Testing SSO exception")
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
    assert any(log["event_type"] == "AUDIT_TEST" for log in state["audit_logs"]), "Auditing failed."
    return True


def verify_fr_111():
    # Test separation of duties violation
    res_sod = evaluate_action_governance("ACT-SOD", {"owner": "Alice", "approver": "Alice"})
    assert res_sod["verdict"] == "REJECTED", "Separation of duties violation not blocked."
    assert "Separation of Duties" in res_sod["reason"], "Incorrect rejection reason for Separation of Duties."

    # Test valid separation of duties
    res_valid_sod = evaluate_action_governance("ACT-SOD-OK", {"owner": "Alice", "approver": "Bob"})
    assert res_valid_sod["verdict"] == "APPROVED", "Valid separation of duties rejected."

    # Test unrecognized role
    res_bad_role = evaluate_action_governance("ACT-ROLE-BAD", {"actor_role": "Hacker"})
    assert res_bad_role["verdict"] == "REJECTED", "Unrecognized role not blocked."

    # Test unauthorized role for budget action
    res_unauth_role = evaluate_action_governance("ACT-BUDGET-UNAUTH", {"actor_role": "Developer", "category": "budget"})
    assert res_unauth_role["verdict"] == "REJECTED", "Unauthorized role for budget was not blocked."

    # Test authorized role for budget action
    res_auth_role = evaluate_action_governance("ACT-BUDGET-AUTH", {"actor_role": "CEO", "category": "budget"})
    assert res_auth_role["verdict"] == "APPROVED", "Authorized role for budget was rejected."

    return True


def verify_fr_112():
    # Test fine-grained OpenFGA ReBAC integration
    res_fga_ceo = evaluate_action_governance(
        "ACT-FGA-CEO", {"owner": "Alice", "actor_role": "CEO", "category": "budget"}
    )
    assert res_fga_ceo["verdict"] == "APPROVED", "OpenFGA CEO budget request failed."

    res_fga_dev = evaluate_action_governance(
        "ACT-FGA-DEV", {"owner": "Bob", "actor_role": "Developer", "category": "budget"}
    )
    assert res_fga_dev["verdict"] == "REJECTED", "OpenFGA Developer budget request was not blocked."

    res_fga_dev_general = evaluate_action_governance(
        "ACT-FGA-DEV-OK", {"owner": "Bob", "actor_role": "Developer", "category": "licensing"}
    )
    assert res_fga_dev_general["verdict"] == "APPROVED", "OpenFGA Developer licensing request failed."

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
        ("FR-112", verify_fr_112),
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
