from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


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
