import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def test_root_serves_frontend():
    response = client.get("/")

    assert response.status_code == 200
    assert "Mergington High School" in response.text


def test_activities_returns_activity_data_without_caching():
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.headers["cache-control"] == "no-store"


def test_student_signup_is_visible_in_activities_response():
    activity_name = "Debate Club"
    email = "student@mergington.edu"

    try:
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        activities_response = client.get("/activities")

        assert signup_response.status_code == 200
        assert activities_response.status_code == 200
        assert email in activities_response.json()[activity_name]["participants"]
        assert activities_response.headers["cache-control"] == "no-store"
    finally:
        activities[activity_name]["participants"].remove(email)


def test_student_cannot_sign_up_twice():
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


@pytest.mark.parametrize(
    "method, path, expected_detail",
    [
        ("post", "/activities/Unknown Club/signup?email=student@example.com", "Activity not found"),
        ("delete", "/activities/Unknown Club/participants?email=student@example.com", "Activity not found"),
        ("delete", "/activities/Chess Club/participants?email=absent@example.com", "Student is not signed up for this activity"),
    ],
)
def test_invalid_activity_requests_return_helpful_errors(method, path, expected_detail):
    response = getattr(client, method)(path)

    assert response.status_code in (404, 400)
    assert response.json()["detail"] == expected_detail


def test_student_can_be_unregistered_from_activity():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    initial_participants = activities[activity_name]["participants"].copy()

    try:
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )

        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    finally:
        activities[activity_name]["participants"] = initial_participants
