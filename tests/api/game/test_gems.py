"""
Tests for gem-related API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.core.config import settings

client = TestClient(app)
API_PREFIX = settings.API_V1_STR


def test_list_gems(client):
    """Test listing all gems."""
    response = client.get(f"{API_PREFIX}/game/gems")
    assert response.status_code == 200
    gems = response.json()
    assert isinstance(gems, list)
    assert len(gems) == 1
    assert gems[0]["Name"] == "Blood-Soaked Jade"


def test_list_gems_with_filters(client):
    """Test listing gems with filters."""
    # Test skill type filter
    response = client.get(f"{API_PREFIX}/game/gems?skill_type=movement")
    assert response.status_code == 200
    gems = response.json()
    assert isinstance(gems, list)
    assert len(gems) == 1
    assert gems[0]["Name"] == "Blood-Soaked Jade"

    # Test star rating filter
    response = client.get(f"{API_PREFIX}/game/gems?stars=5")
    assert response.status_code == 200
    gems = response.json()
    assert isinstance(gems, list)
    assert len(gems) == 1
    assert gems[0]["Stars"] == 5

    # Test no results
    response = client.get(f"{API_PREFIX}/game/gems?skill_type=attack")
    assert response.status_code == 200
    gems = response.json()
    assert isinstance(gems, list)
    assert len(gems) == 0


def test_get_gem(client):
    """Test getting a specific gem."""
    # Test getting an existing gem
    response = client.get(f"{API_PREFIX}/game/gems/Blood-Soaked%20Jade")
    assert response.status_code == 200
    gem = response.json()
    assert gem["Name"] == "Blood-Soaked Jade"

    # Test getting a non-existent gem
    response = client.get(f"{API_PREFIX}/game/gems/NonExistentGem")
    assert response.status_code == 404
