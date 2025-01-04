"""Test inventory gist functionality."""

import json
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
import httpx

from api.core.config import Settings


@pytest.fixture
def mock_gists_list_response():
    """Mock GitHub gists list API response."""
    return [
        {
            "id": "gist123",
            "files": {
                "gems.json": {
                    "filename": "gems.json"
                }
            }
        }
    ]


@pytest.fixture
def mock_gist_content_response():
    """Mock GitHub gist content API response."""
    return {
        "files": {
            "gems.json": {
                "content": json.dumps({
                    "Berserker's Eye": {
                        "owned_rank": 10,
                        "quality": None
                    },
                    "Blessing of the Worthy": {
                        "owned_rank": 3,
                        "quality": "2"
                    }
                })
            }
        }
    }


def test_get_inventory_success(
    client: TestClient,
    mock_gists_list_response,
    mock_gist_content_response
):
    """Test successful inventory fetch."""
    with patch("httpx.AsyncClient.get") as mock_get:
        # Mock the gists list response
        mock_get.side_effect = [
            httpx.Response(200, json=mock_gists_list_response),
            httpx.Response(200, json=mock_gist_content_response)
        ]
        
        response = client.get(
            "/api/v1/auth/inventory",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Berserker's Eye" in data
        assert data["Berserker's Eye"]["owned_rank"] == 10
        assert "Blessing of the Worthy" in data
        assert data["Blessing of the Worthy"]["quality"] == "2"


def test_get_inventory_no_gist(client: TestClient):
    """Test when user has no inventory gist."""
    with patch("httpx.AsyncClient.get") as mock_get:
        # Mock empty gists list
        mock_get.return_value = httpx.Response(200, json=[])
        
        response = client.get(
            "/api/v1/auth/inventory",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        assert response.json() == {}


def test_get_inventory_invalid_gist(
    client: TestClient,
    mock_gists_list_response
):
    """Test handling of invalid gist content."""
    with patch("httpx.AsyncClient.get") as mock_get:
        # Mock the gists list response
        mock_get.side_effect = [
            httpx.Response(200, json=mock_gists_list_response),
            httpx.Response(200, json={
                "files": {
                    "gems.json": {
                        "content": "invalid json"
                    }
                }
            })
        ]
        
        response = client.get(
            "/api/v1/auth/inventory",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 400
        assert "Invalid inventory gist format" in response.json()["detail"]


def test_get_inventory_no_auth(client: TestClient):
    """Test inventory fetch without auth token."""
    response = client.get("/api/v1/auth/inventory")
    assert response.status_code == 401
    assert "Missing or invalid authorization token" in response.json()["detail"]


def test_get_inventory_github_error(client: TestClient):
    """Test handling of GitHub API errors."""
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = httpx.Response(
            401,
            json={"message": "Bad credentials"}
        )
        
        response = client.get(
            "/api/v1/auth/inventory",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 400
        assert "Failed to fetch gists" in response.json()["detail"]
