# scratch/test_api_contracts.py
import os
import sys

import pytest
from fastapi.testclient import TestClient

# Ensure project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from uawos_dashboard_daemon import SECURE_TOKEN, app


def test_api_status_contract():
    """Verify schema contract for system health status endpoint."""
    client = TestClient(app)
    response = client.get("/api/status")
    assert response.status_code == 200, f"Status failed: {response.text}"

    data = response.json()
    assert "timestamp" in data, "Status response missing timestamp."
    assert "docker_running" in data, "Status response missing docker_running status."
    assert "health_summary" in data, "Status response missing health_summary."
    assert "domains" in data, "Status response missing domains list."

    summary = data["health_summary"]
    for key in ["total", "green", "yellow", "red", "gray", "strict_percentage", "weighted_percentage"]:
        assert key in summary, f"health_summary missing key: {key}"


def test_objective_list_contract():
    """Verify schema contract for objective list retrieval."""
    client = TestClient(app)
    response = client.get("/api/objective/list")
    assert response.status_code == 200, f"Objective list failed: {response.text}"

    data = response.json()
    assert "objectives" in data, "Objective list response missing objectives key."
    assert isinstance(data["objectives"], dict), "Objectives must be mapped as a dictionary."


def test_pmcms_assessment_contract():
    """Verify maturity assessment details returned by PMCMS API."""
    client = TestClient(app)
    response = client.get("/api/pmcms")
    assert response.status_code == 200, f"PMCMS failed: {response.text}"

    data = response.json()
    assert "overall_score" in data, "PMCMS response missing overall_score."
    assert "maturity_level" in data, "PMCMS response missing maturity_level descriptor."
    assert "dimensions" in data, "PMCMS response missing dimensions object."

    dims = data["dimensions"]
    assert "Strategy" in dims, "PMCMS missing Strategy dimension."
    assert "Governance" in dims, "PMCMS missing Governance dimension."
    assert "Execution" in dims, "PMCMS missing Execution dimension."


def test_traceability_matrix_contract():
    """Verify requirement-to-code traceability metrics contract."""
    client = TestClient(app)
    response = client.get("/api/traceability")
    assert response.status_code == 200, f"Traceability failed: {response.text}"

    data = response.json()
    assert "matrix" in data, "Traceability response missing matrix."
    assert "health" in data, "Traceability response missing health metrics."
    assert isinstance(data["matrix"], dict), "Traceability matrix must be a dict."


def test_authorized_budget_action_contract():
    """Verify that unauthorized requests are blocked and authorized schema updates work."""
    client = TestClient(app)

    # 1. Reject unauthorized call
    bad_response = client.post("/api/budget/action", json={"action": "check_governance", "objective_id": "OBJ-101"})
    assert bad_response.status_code == 401, "Should have rejected unsigned request."

    # 2. Accept authorized call
    headers = {"X-UAWOS-Token": SECURE_TOKEN}
    good_response = client.post(
        "/api/budget/action", headers=headers, json={"action": "check_governance", "objective_id": "OBJ-101"}
    )
    assert good_response.status_code == 200, f"Budget action failed: {good_response.text}"
    data = good_response.json()
    assert "gov" in data, "Response missing governance audit object."
    assert "governance_verdict" in data["gov"], "Governance response missing verdict."


if __name__ == "__main__":
    pytest.main([__file__])
