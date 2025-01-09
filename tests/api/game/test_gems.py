"""Tests for gem-related API endpoints."""

from fastapi.testclient import TestClient
from api.core.config import settings

API_PREFIX = settings.API_V1_STR


def test_list_gems(client: TestClient):
    """Test listing all gems."""
    response = client.get(f"{API_PREFIX}/game/gems")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Verify structure of a gem
    gem = data[0]
    assert "Name" in gem
    assert "Stars" in gem
    assert gem["Stars"] in ["1", "2", "5"]  # Only valid star values


def test_list_gems_with_stars_filter(client: TestClient):
    """Test filtering gems by star rating."""
    response = client.get(f"{API_PREFIX}/game/gems?stars=5")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Verify all gems have 5 stars
    for gem in data:
        assert gem["Stars"] == "5"


def test_list_gems_with_skill_filter(client: TestClient):
    """Test filtering gems by skill type."""
    response = client.get(f"{API_PREFIX}/game/gems?skill_type=movement")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Load skill map to verify gems
    skill_map_response = client.get(f"{API_PREFIX}/game/gems/skills")
    assert skill_map_response.status_code == 200
    skill_map = skill_map_response.json()
    
    # Verify all returned gems are in the movement skill list
    movement_gems = skill_map["gems_by_skill"]["movement"]
    for gem in data:
        assert gem["Name"] in movement_gems


def test_list_gems_with_invalid_filters(client: TestClient):
    """Test listing gems with invalid filters."""
    # Test invalid skill type
    response = client.get(f"{API_PREFIX}/game/gems?skill_type=invalid")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0
    
    # Test invalid stars
    response = client.get(f"{API_PREFIX}/game/gems?stars=10")
    assert response.status_code == 422  # FastAPI validation error


def test_get_gem(client: TestClient):
    """Test getting a specific gem."""
    # Test getting an existing gem
    response = client.get(f"{API_PREFIX}/game/gems/Blood-Soaked%20Jade")
    assert response.status_code == 200
    gem = response.json()
    assert gem["Name"] == "Blood-Soaked Jade"
    assert gem["Stars"] == "5"
    
    # Test getting a non-existent gem
    response = client.get(f"{API_PREFIX}/game/gems/NonExistentGem")
    assert response.status_code == 404
