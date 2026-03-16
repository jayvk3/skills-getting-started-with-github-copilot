import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    # Arrange - TestClient is set up

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0  # Assuming there are activities
    # Check structure of one activity
    activity = next(iter(data.values()))
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_success():
    # Arrange
    activity_name = "Soccer Team"
    email = "student@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity_name}"
    # Verify added to participants
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_activity_not_found():
    # Arrange
    activity_name = "NonExistentActivity"
    email = "student@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_already_signed_up():
    # Arrange
    activity_name = "Basketball Club"
    email = "student@example.com"
    # First signup
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act - Try to signup again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "Student is already signed up for this activity" in data["detail"]


def test_unregister_success():
    # Arrange
    activity_name = "Art Club"
    email = "student@example.com"
    # Signup first
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {email} from {activity_name}"
    # Verify removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_activity_not_found():
    # Arrange
    activity_name = "NonExistentActivity"
    email = "student@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_not_signed_up():
    # Arrange
    activity_name = "Drama Society"
    email = "student@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "Student is not signed up for this activity" in data["detail"]


def test_root_redirect():
    # Arrange - TestClient

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200  # RedirectResponse, but TestClient follows redirects by default?
    # Actually, RedirectResponse returns 307, but TestClient might follow.
    # Wait, in FastAPI, RedirectResponse is 307, but TestClient doesn't follow by default I think.
    # Let me check: actually, TestClient follows redirects unless follow_redirects=False
    # By default, it follows, so it should get 200 from the static file, but since no static, perhaps 404.
    # The redirect is to /static/index.html, but in TestClient, it might not serve static.
    # To test redirect, use follow_redirects=False
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_multiple_operations():
    # Arrange
    activity_name = "Science Club"
    email1 = "student1@example.com"
    email2 = "student2@example.com"

    # Act - Multiple signups and unregisters
    client.post(f"/activities/{activity_name}/signup?email={email1}")
    client.post(f"/activities/{activity_name}/signup?email={email2}")
    client.delete(f"/activities/{activity_name}/unregister?email={email1}")

    # Assert - Check final state
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email1 not in activities[activity_name]["participants"]
    assert email2 in activities[activity_name]["participants"]