# tests/unit/test_meeting_api.py
from fastapi.testclient import TestClient

from apps.api.main import app
from interfaces.rest.auth import SECURE_TOKEN

client = TestClient(app)
headers = {"x-uawos-token": SECURE_TOKEN}


def test_meeting_transcribe():
    """Verify meeting transcription endpoint attributes speech and returns speaker turns."""
    response = client.post("/api/meeting/transcribe", json={"template": "sprint"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Success"
    assert "meeting_id" in data
    assert len(data["transcript"]) > 0
    assert "speaker" in data["transcript"][0]


def test_meeting_synthesize():
    """Verify meeting synthesis returns collective intelligence sections."""
    # Pre-transcribe to get a meeting ID and transcript
    transcribe_res = client.post("/api/meeting/transcribe", json={"template": "sprint"}, headers=headers)
    transcribe_data = transcribe_res.json()

    response = client.post(
        "/api/meeting/synthesize",
        json={
            "meeting_id": transcribe_data["meeting_id"],
            "transcript": transcribe_data["transcript"],
            "personas": ["Product Manager", "Legal Analyst"],
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Success"
    assert "synthesis" in data
    synthesis = data["synthesis"]
    assert "executive_summary" in synthesis
    assert "decisions_register" in synthesis
    assert "action_items" in synthesis


def test_meeting_promote():
    """Verify meeting promotion directly creates a new UAWOS Objective and Outcome."""
    response = client.post(
        "/api/meeting/promote",
        json={
            "meeting_id": "MTG-TEST",
            "title": "Promote Test Title",
            "description": "Promote Test Description",
            "owner": "Test Owner",
            "priority": "High",
            "metric_name": "Test Metric",
            "metric_unit": "units",
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Success"
    assert "objective_id" in data

    # Check that it exists in the objectives database list
    list_res = client.get("/api/objective/list", headers=headers)
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert data["objective_id"] in list_data["objectives"]
    assert list_data["objectives"][data["objective_id"]]["title"] == "Promote Test Title"
