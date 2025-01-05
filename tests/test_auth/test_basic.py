"""Basic auth tests."""

from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from api.core.config import Settings


def test_github_login(client: TestClient, test_settings: Settings):
    """Test GitHub login route returns correct URL."""
    response = client.get(f"{test_settings.API_V1_STR}/auth/login")
    assert response.status_code == 200

    data = response.json()
    assert "auth_url" in data
    assert test_settings.ACTIVE_GITHUB_CLIENT_ID in data["auth_url"]
    assert "callback" in data["auth_url"]


def test_github_callback_invalid_state(client: TestClient, test_settings: Settings):
    """Test GitHub callback with invalid state."""
    response = client.get(
        f"{test_settings.API_V1_STR}/auth/github/callback",
        params={"code": "test-code", "state": "invalid-state"}
    )
    assert response.status_code == 400
    assert "Invalid state parameter" in response.json()["detail"]


@patch("api.auth.service.AuthService.get_user_gists")
def test_get_gists(mock_get_gists, client: TestClient, mock_token, test_settings: Settings):
    """Test getting user's gists."""
    # Mock GitHub API response
    mock_get_gists.return_value = [{
        "id": "gist123",
        "description": "Test Gist",
        "files": {
            "test.json": {
                "filename": "test.json",
                "content": '{"test": "data"}'
            }
        }
    }]

    response = client.get(
        f"{test_settings.API_V1_STR}/auth/gists",
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
