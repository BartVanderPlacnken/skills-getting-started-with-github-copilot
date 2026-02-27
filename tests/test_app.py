"""Tests for the Mergington High School Activities API.

This test suite covers all endpoints with AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the API call
- Assert: Verify the response
"""

from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


# ============================================================================
# Helper Methods
# ============================================================================


def get_activities():
    """Helper: Fetch all activities."""
    return client.get("/activities")


def signup_for_activity(activity_name: str, email: str):
    """Helper: Sign up a student for an activity."""
    return client.post(f"/activities/{activity_name}/signup?email={email}")


def unregister_from_activity(activity_name: str, email: str):
    """Helper: Unregister a student from an activity."""
    return client.post(f"/activities/{activity_name}/unregister?email={email}")


def assert_success_response(response, expected_status: int = 200):
    """Helper: Assert that response indicates success."""
    assert response.status_code == expected_status
    return response.json()


def assert_error_response(response, expected_status: int, detail_substring: str):
    """Helper: Assert that response indicates error with expected message."""
    assert response.status_code == expected_status
    result = response.json()
    assert detail_substring.lower() in result["detail"].lower()


# ============================================================================
# Test Classes
# ============================================================================


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_dict(self):
        """Verify that /activities returns a dictionary of activities."""
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Club",
            "Music Ensemble",
            "Science Club",
            "Debate Team",
        ]

        # Act
        response = get_activities()
        activities = assert_success_response(response)

        # Assert
        assert isinstance(activities, dict)
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self):
        """Verify that each activity has required fields."""
        # Arrange
        required_fields = {
            "description",
            "schedule",
            "max_participants",
            "participants",
        }

        # Act
        response = get_activities()
        activities = assert_success_response(response)

        # Assert
        for activity_name, activity_data in activities.items():
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self):
        """Verify successful signup for an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "new_student@mergington.edu"

        # Act
        response = signup_for_activity(activity_name, email)
        result = assert_success_response(response)

        # Assert
        assert result["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_activity_not_found(self):
        """Verify error when signing up for non-existent activity."""
        # Arrange
        activity_name = "Non-Existent Activity"
        email = "student@mergington.edu"

        # Act
        response = signup_for_activity(activity_name, email)

        # Assert
        assert_error_response(response, 404, "Activity not found")

    def test_signup_duplicate_registration(self):
        """Verify error when student tries to sign up twice."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered

        # Act
        response = signup_for_activity(activity_name, email)

        # Assert
        assert_error_response(response, 400, "already signed up")


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful(self):
        """Verify successful unregistration from an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"  # Already registered

        # Act
        response = unregister_from_activity(activity_name, email)
        result = assert_success_response(response)

        # Assert
        assert result["message"] == f"Unregistered {email} from {activity_name}"

    def test_unregister_activity_not_found(self):
        """Verify error when unregistering from non-existent activity."""
        # Arrange
        activity_name = "Non-Existent Activity"
        email = "student@mergington.edu"

        # Act
        response = unregister_from_activity(activity_name, email)

        # Assert
        assert_error_response(response, 404, "Activity not found")

    def test_unregister_not_registered(self):
        """Verify error when unregistering a student not in the activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "not_registered@mergington.edu"

        # Act
        response = unregister_from_activity(activity_name, email)

        # Assert
        assert_error_response(response, 400, "not signed up")


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static(self):
        """Verify that root endpoint redirects to static files."""
        # Arrange
        expected_url = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_url
