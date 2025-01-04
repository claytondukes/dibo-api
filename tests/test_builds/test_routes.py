"""Test build routes."""

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


def test_generate_build_endpoint(client):
    """Test build generation endpoint."""
    response = client.get(
        "/api/v1/builds/generate",
        params={
            "build_type": "pve",
            "focus": "dps",
            "use_inventory": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "build" in data
    assert "stats" in data
    assert "recommendations" in data


def test_generate_build_with_inventory(client, mock_auth_token):
    """Test build generation with inventory."""
    response = client.get(
        "/api/v1/builds/generate",
        params={
            "build_type": "pvp",
            "focus": "survival",
            "use_inventory": True
        },
        headers={"Authorization": f"Bearer {mock_auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "build" in data
    assert "stats" in data
    assert "recommendations" in data


def test_generate_build_invalid_type(client):
    """Test build generation with invalid build type."""
    response = client.get(
        "/api/v1/builds/generate",
        params={
            "build_type": "invalid",
            "focus": "dps",
            "use_inventory": False
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_generate_build_invalid_focus(client):
    """Test build generation with invalid focus."""
    response = client.get(
        "/api/v1/builds/generate",
        params={
            "build_type": "pve",
            "focus": "invalid",
            "use_inventory": False
        }
    )
    
    assert response.status_code == 422  # Validation error
