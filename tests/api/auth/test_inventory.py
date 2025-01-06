"""Test inventory operations."""

from unittest.mock import patch, AsyncMock
import pytest
from fastapi.testclient import TestClient

from api.core.config import get_settings

settings = get_settings()


@pytest.fixture
def mock_token() -> str:
    """Mock access token."""
    return "mock.test.token"


@pytest.fixture
def mock_gists_response() -> list:
    """Mock GitHub gists response."""
    return [{
        "id": "gist123",
        "description": "DIBO Inventory",
        "files": {
            "profile.json": {
                "filename": "profile.json",
                "content": '{"version":"1.0","name":"TestChar","class":"Barbarian"}'
            },
            "gems.json": {
                "filename": "gems.json",
                "content": '{"version":"1.0","gems":[]}'
            },
            "sets.json": {
                "filename": "sets.json",
                "content": '{"version":"1.0","sets":[]}'
            },
            "builds.json": {
                "filename": "builds.json",
                "content": '{"version":"1.0","builds":[]}'
            }
        }
    }]


def test_get_inventory_unauthorized(client: TestClient):
    """Test getting inventory without authorization."""
    response = client.get(f"{settings.API_V1_STR}/auth/inventory")
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]


def test_get_inventory_invalid_token(client: TestClient):
    """Test getting inventory with invalid token."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=401,
            json=lambda: {"message": "Bad credentials"}
        )

        response = client.get(
            f"{settings.API_V1_STR}/auth/inventory",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]


@patch("httpx.AsyncClient.get")
def test_get_inventory_no_gists(mock_get, client: TestClient, mock_token):
    """Test getting inventory with no gists."""
    mock_get.return_value = AsyncMock(
        status_code=200,
        json=lambda: []
    )

    response = client.get(
        f"{settings.API_V1_STR}/auth/inventory",
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    assert response.status_code == 200
    inventory = response.json()

    # Check default empty inventory
    assert inventory["profile"]["version"] == "1.0"
    assert inventory["profile"]["name"] is None
    assert inventory["profile"]["class"] is None
    assert inventory["gems"]["version"] == "1.0"
    assert inventory["gems"]["gems"] == []
    assert inventory["sets"]["version"] == "1.0"
    assert inventory["sets"]["sets"] == []
    assert inventory["builds"]["version"] == "1.0"
    assert inventory["builds"]["builds"] == []


@patch("httpx.AsyncClient.get")
def test_get_inventory_with_gists(
    mock_get,
    client: TestClient,
    mock_token,
    mock_gists_response
):
    """Test getting inventory with gists."""
    mock_get.return_value = AsyncMock(
        status_code=200,
        json=lambda: mock_gists_response
    )

    response = client.get(
        f"{settings.API_V1_STR}/auth/inventory",
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    assert response.status_code == 200
    inventory = response.json()

    # Check inventory from gist
    assert inventory["profile"]["version"] == "1.0"
    assert inventory["profile"]["name"] == "TestChar"
    assert inventory["profile"]["class"] == "Barbarian"
    assert inventory["gems"]["version"] == "1.0"
    assert inventory["gems"]["gems"] == []
    assert inventory["sets"]["version"] == "1.0"
    assert inventory["sets"]["sets"] == []
    assert inventory["builds"]["version"] == "1.0"
    assert inventory["builds"]["builds"] == []
