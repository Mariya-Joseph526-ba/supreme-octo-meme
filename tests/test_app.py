import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def activities():
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        }
    }


@pytest.fixture
def client(monkeypatch, activities):
    monkeypatch.setattr(app_module, "activities", activities)
    return TestClient(app_module.app, follow_redirects=False)


def test_root_redirects_to_static_homepage(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_available_activities(client, activities):
    # Arrange
    expected_activities = activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, activities):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post("/activities/Unknown Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant_and_preserves_others(client, activities):
    # Arrange
    email = "michael@mergington.edu"
    remaining_participants = ["daniel@mergington.edu"]

    # Act
    response = client.delete("/activities/Chess Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert activities["Chess Club"]["participants"] == remaining_participants


def test_unregister_returns_404_for_missing_participant(client):
    # Arrange
    email = "absent@mergington.edu"

    # Act
    response = client.delete("/activities/Chess Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found in this activity"}


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete("/activities/Unknown Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
