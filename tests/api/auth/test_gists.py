"""Test gist operations."""

from unittest.mock import patch, AsyncMock
import httpx
import pytest
from fastapi.testclient import TestClient

from api.core.config import get_settings

settings = get_settings()


@pytest.fixture
def mock_access_token() -> str:
    """Mock access token."""
    return "gho_mock_token"


@pytest.fixture
def mock_github_gists_response() -> dict:
    """Mock GitHub gists response."""
    return [
        {
            "id": "test123",
            "html_url": "https://gist.github.com/test123",
            "files": {
                "test.json": {
                    "filename": "test.json",
                    "content": '{"test": true}'
                }
            }
        }
    ]


@pytest.fixture
def mock_gist_create_response() -> dict:
    """Mock gist creation response."""
    return {
        "id": "test123",
        "html_url": "https://gist.github.com/test123",
        "files": {
            "test.json": {
                "filename": "test.json",
                "content": '{"test": true}'
            }
        }
    }


@pytest.fixture
def mock_gist_update_response() -> dict:
    """Mock gist update response."""
    return {
        "id": "test123",
        "html_url": "https://gist.github.com/test123",
        "files": {
            "test.json": {
                "filename": "test.json",
                "content": '{"test": false, "updated": true}'
            }
        }
    }


def test_get_gists(
    client: TestClient,
    mock_access_token,
    mock_github_gists_response
):
    """Test getting user's gists."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_github_gists_response
        )

        response = client.get(
            f"{settings.API_V1_STR}/auth/gists",
            headers={"Authorization": f"Bearer {mock_access_token}"}
        )
        assert response.status_code == 200
        gists = response.json()
        assert isinstance(gists, list)
        assert len(gists) > 0
        assert "files" in gists[0]


def test_get_gists_unauthorized(client: TestClient):
    """Test getting gists without authorization."""
    response = client.get(f"{settings.API_V1_STR}/auth/gists")
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]


def test_get_gists_invalid_token(client: TestClient):
    """Test getting gists with invalid token."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=401,
            json=lambda: {"message": "Bad credentials"}
        )

        response = client.get(
            f"{settings.API_V1_STR}/auth/gists",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]


def test_create_gist(
    client: TestClient,
    mock_access_token,
    mock_gist_create_response
):
    """Test creating a new gist."""
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=201,
            json=lambda: mock_gist_create_response
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/gists",
            headers={"Authorization": f"Bearer {mock_access_token}"},
            json={
                "filename": "test.json",
                "content": '{"test": true}',
                "description": "Test gist"
            }
        )
        assert response.status_code == 201
        gist = response.json()
        assert gist["id"] == "test123"
        assert "files" in gist
        assert "test.json" in gist["files"]


def test_update_gist(
    client: TestClient,
    mock_access_token,
    mock_gist_update_response
):
    """Test updating an existing gist."""
    with patch("httpx.AsyncClient.patch") as mock_patch:
        mock_patch.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_gist_update_response
        )

        response = client.patch(
            f"{settings.API_V1_STR}/auth/gists/test123",
            headers={"Authorization": f"Bearer {mock_access_token}"},
            json={
                "filename": "test.json",
                "content": '{"test": false, "updated": true}',
                "description": "Updated test gist"
            }
        )
        assert response.status_code == 200
        gist = response.json()
        assert gist["id"] == "test123"
        assert "files" in gist
        assert "test.json" in gist["files"]


def test_create_gist_failure(
    client: TestClient,
    mock_access_token
):
    """Test handling of gist creation failure."""
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=422,
            json=lambda: {"message": "Validation Failed"}
        )

        response = client.post(
            f"{settings.API_V1_STR}/auth/gists",
            headers={"Authorization": f"Bearer {mock_access_token}"},
            json={
                "filename": "test.json",
                "content": '{"test": true}',
                "description": "Test gist"
            }
        )
        assert response.status_code == 422
        assert "Failed to create gist" in response.json()["detail"]


def test_update_gist_failure(
    client: TestClient,
    mock_access_token
):
    """Test handling of gist update failure."""
    with patch("httpx.AsyncClient.patch") as mock_patch:
        mock_patch.return_value = AsyncMock(
            status_code=404,
            json=lambda: {"message": "Not Found"}
        )

        response = client.patch(
            f"{settings.API_V1_STR}/auth/gists/test123",
            headers={"Authorization": f"Bearer {mock_access_token}"},
            json={
                "filename": "test.json",
                "content": '{"test": true}',
                "description": "Test gist"
            }
        )
        assert response.status_code == 404
        assert "Gist not found" in response.json()["detail"]
