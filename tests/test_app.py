from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
initial_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activity_state():
    activities.clear()
    activities.update(deepcopy(initial_activities))
    yield


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"].startswith("Learn strategies")
    assert payload["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_new_participant():
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up test@mergington.edu for Chess Club"}
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
    response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_updates_activity():
    response = client.delete("/activities/Chess%20Club/participants/michael@mergington.edu")

    assert response.status_code == 200
    assert response.json() == {"message": "Removed michael@mergington.edu from Chess Club"}
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_remove_missing_participant_returns_404():
    response = client.delete("/activities/Chess%20Club/participants/nonexistent@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
