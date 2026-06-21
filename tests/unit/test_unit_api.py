# tests/unit/test_unit_api.py
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_api_status():
    """Verify system status API is responsive."""
    response = client.get("/api/status")
    assert response.status_code == 200
    # Response might be empty dict initially or populated status cache
    assert isinstance(response.json(), dict)


def test_api_objective_list():
    """Verify objective list API returns a list or dict of objectives."""
    response = client.get("/api/objective/list")
    assert response.status_code == 200
    data = response.json()
    assert "objectives" in data


def test_api_requirement_list():
    """Verify requirement list API returns a checklist structure."""
    response = client.get("/api/requirement/list")
    assert response.status_code == 200
    data = response.json()
    assert "requirements" in data


def test_api_budget_status():
    """Verify budget status API returns cost forecasts and metrics."""
    response = client.get("/api/budget/status")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "objective_budgets" in data


def test_api_docs():
    """Verify documentation categories are listed."""
    response = client.get("/api/docs")
    assert response.status_code == 200
    data = response.json()
    assert "Architectural Standards" in data
