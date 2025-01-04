"""Tests for game data routes."""

import pytest
from fastapi import status

from api.data.models import BuildCategory


def test_list_gems_no_filters(test_client):
    """Test listing gems without filters."""
    response = test_client.get("/api/v1/data/gems")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["per_page"] == 20
    assert len(data["items"]) == 2

    # Verify gem data
    gem = data["items"][0]
    assert gem["name"] == "Freedom and Devotion"
    assert gem["stars"] == 2
    assert gem["base_effect"] == "Increases Movement Speed by 10%"
    assert gem["rank_10_effect"] == "Increases Movement Speed by 20%"
    assert gem["categories"] == [BuildCategory.MOVEMENT.value]


def test_list_gems_filter_by_stars(test_client):
    """Test listing gems filtered by stars."""
    response = test_client.get("/api/v1/data/gems?stars=5")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Lightning Core"
    assert data["items"][0]["stars"] == 5


def test_list_gems_filter_by_category(test_client):
    """Test listing gems filtered by category."""
    response = test_client.get(
        f"/api/v1/data/gems?category={BuildCategory.MOVEMENT.value}"
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Freedom and Devotion"
    assert BuildCategory.MOVEMENT.value in data["items"][0]["categories"]


def test_list_gems_pagination(test_client):
    """Test gem listing pagination."""
    response = test_client.get("/api/v1/data/gems?per_page=1")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["per_page"] == 1
    assert len(data["items"]) == 1


def test_list_sets_no_filters(test_client):
    """Test listing equipment sets without filters."""
    response = test_client.get("/api/v1/data/sets")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2

    # Verify set data
    set_data = data["items"][0]
    assert set_data["name"] == "Grace of the Flagellant"
    assert set_data["description"] == "A powerful set for damage dealers"
    assert set_data["bonuses"] == {
        "2": "+15% damage",
        "4": "+30% damage",
        "6": "+50% damage"
    }


def test_list_sets_filter_by_pieces(test_client):
    """Test listing equipment sets filtered by pieces."""
    response = test_client.get("/api/v1/data/sets?pieces=4")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Shepherd's Call to Wolves"


def test_list_skills_by_class(test_client):
    """Test listing skills for a character class."""
    response = test_client.get("/api/v1/data/skills/barbarian")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2

    # Verify skill data
    skill = data["items"][0]
    assert skill["name"] == "Whirlwind"
    assert skill["description"] == "Spin to win"
    assert skill["cooldown"] == 8.0
    assert BuildCategory.ATTACK.value in skill["categories"]
    assert BuildCategory.CHANNELED.value in skill["categories"]


def test_list_skills_filter_by_category(test_client):
    """Test listing skills filtered by category."""
    response = test_client.get(
        f"/api/v1/data/skills/barbarian?category={BuildCategory.MOVEMENT.value}"
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Sprint"
    assert data["items"][0]["categories"] == [BuildCategory.MOVEMENT.value]


def test_list_skills_invalid_class(test_client):
    """Test listing skills for an invalid character class."""
    response = test_client.get("/api/v1/data/skills/invalid_class")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("endpoint", [
    "/api/v1/data/gems",
    "/api/v1/data/sets",
    "/api/v1/data/skills/barbarian"
])
def test_pagination_validation(test_client, endpoint):
    """Test pagination parameter validation."""
    # Test invalid page number
    response = test_client.get(f"{endpoint}?page=0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test invalid per_page
    response = test_client.get(f"{endpoint}?per_page=0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    response = test_client.get(f"{endpoint}?per_page=101")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("stars", [-1, 0, 3, 4, 6])
def test_gems_invalid_stars(test_client, stars):
    """Test gem listing with invalid star values."""
    response = test_client.get(f"/api/v1/data/gems?stars={stars}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("pieces", [-1, 0, 1, 3, 5, 7])
def test_sets_invalid_pieces(test_client, pieces):
    """Test set listing with invalid piece values."""
    response = test_client.get(f"/api/v1/data/sets?pieces={pieces}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_stats_no_filter(test_client):
    """Test listing all stats without filters."""
    response = test_client.get("/api/v1/data/stats")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "critical_hit_chance" in data
    assert "damage_increase" in data
    assert "attack_speed" in data
    assert "movement_speed" in data
    assert "life" in data

    # Verify stat structure
    crit = data["critical_hit_chance"]
    assert "gems" in crit
    assert "essences" in crit
    
    # Verify gem details
    gems = crit["gems"]
    assert len(gems) > 0
    gem = gems[0]
    assert all(key in gem for key in ["name", "stars", "base_values", "rank_10_values"])


def test_list_stats_filter_by_stat(test_client):
    """Test listing a specific stat."""
    response = test_client.get("/api/v1/data/stats?stat=critical_hit_chance")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "gems" in data
    assert "essences" in data
    assert len(data["gems"]) > 0


def test_list_stats_invalid_stat(test_client):
    """Test listing an invalid stat."""
    response = test_client.get("/api/v1/data/stats?stat=invalid_stat")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Stat not found" in response.json()["detail"]
