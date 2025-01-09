"""Tests for game-related API routes."""

import json
from typing import Dict, List

import pytest
from fastapi.testclient import TestClient

from api.models.game_data.data_manager import GameDataManager


def test_list_sets(client: TestClient):
    """Test listing equipment sets."""
    response = client.get("/api/v1/game/sets")
    assert response.status_code == 200
    data = response.json()
    assert "sets" in data
    assert "page" in data
    assert "per_page" in data
    assert "total" in data
    
    # Verify we got some sets
    assert len(data["sets"]) > 0
    
    # Verify set structure
    set_data = data["sets"][0]
    assert "name" in set_data
    assert "pieces" in set_data
    assert "description" in set_data
    assert "bonuses" in set_data
    assert "use_case" in set_data


def test_list_sets_with_pieces_filter(client: TestClient):
    """Test listing equipment sets filtered by pieces."""
    response = client.get("/api/v1/game/sets?pieces=4")
    assert response.status_code == 200
    data = response.json()
    
    # Verify all returned sets have 4 pieces
    for set_data in data["sets"]:
        assert set_data["pieces"] == 4


def test_get_set_details(client: TestClient, data_manager: GameDataManager):
    """Test getting specific set details."""
    # Get a real set name from the data
    sets_data = data_manager.get_equipment_sets()
    set_name = next(iter(sets_data.keys()))
    
    response = client.get(f"/api/v1/game/sets/{set_name}")
    assert response.status_code == 200
    data = response.json()
    
    # Verify set data matches
    assert data["name"] == set_name
    assert data["pieces"] == sets_data[set_name].pieces
    assert data["description"] == sets_data[set_name].description
    assert data["bonuses"] == sets_data[set_name].bonuses
    assert data["use_case"] == sets_data[set_name].use_case


def test_get_set_bonuses(client: TestClient, data_manager: GameDataManager):
    """Test getting active set bonuses."""
    # Get a real set name from the data
    sets_data = data_manager.get_equipment_sets()
    set_name = next(iter(sets_data.keys()))
    
    equipped_sets = {
        set_name: 4  # Test with 4 pieces equipped
    }
    response = client.get(
        "/api/v1/game/sets/bonuses",
        params={"equipped_sets": json.dumps(equipped_sets)}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "active_bonuses" in data
    assert "total_sets" in data
    
    # Verify bonuses are correct
    assert set_name in data["active_bonuses"]
    bonuses = data["active_bonuses"][set_name]
    assert len(bonuses) == 2  # Should have 2-piece and 4-piece bonuses


def test_list_gear(client: TestClient):
    """Test listing gear items."""
    response = client.get("/api/v1/game/gear")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "page" in data
    assert "per_page" in data
    assert "total" in data


def test_list_class_essences(client: TestClient):
    """Test listing class-specific essences."""
    class_name = "barbarian"  # Use a known class
    response = client.get(f"/api/v1/game/gear/{class_name}/essences")
    assert response.status_code == 200
    data = response.json()
    assert "essences" in data
    assert "page" in data
    assert "per_page" in data
    assert "total" in data


def test_list_class_essences_with_filters(client: TestClient):
    """Test listing class-specific essences with filters."""
    class_name = "barbarian"  # Use a known class
    response = client.get(
        f"/api/v1/game/gear/{class_name}/essences",
        params={
            "slot": "chest",
            "skill": "Whirlwind"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "essences" in data
    assert "page" in data
    assert "per_page" in data
    assert "total" in data


def test_invalid_set_name(client: TestClient):
    """Test getting details for non-existent set."""
    response = client.get("/api/v1/game/sets/NonExistentSet")
    assert response.status_code == 404


def test_invalid_class_name(client: TestClient):
    """Test getting essences for non-existent class."""
    response = client.get("/api/v1/game/gear/invalid_class/essences")
    assert response.status_code == 500  # Internal server error due to missing data


def test_list_gems(client: TestClient):
    """Test listing gems."""
    response = client.get("/api/v1/game/gems")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert "Name" in response.json()[0]


def test_list_gems_with_filters(client: TestClient):
    """Test listing gems with filters."""
    response = client.get("/api/v1/game/gems?skill_type=movement&stars=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert all(gem["Stars"] == 5 for gem in response.json())


def test_get_gem(client: TestClient):
    """Test getting details for a specific gem."""
    response = client.get("/api/v1/game/gems/berserker's%20eye")
    assert response.status_code == 200
    assert response.json()["Name"].lower() == "berserker's eye"
    assert "BaseEffect" in response.json()


def test_get_gem_progression(client: TestClient):
    """Test getting progression data for a specific gem."""
    response = client.get("/api/v1/game/gems/berserker's%20eye/progression")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Stars" in response.json()
    assert "Ranks" in response.json()
    assert "MaxRank" in response.json()
    assert "MaxEffect" in response.json()


def test_invalid_gem_name(client: TestClient):
    """Test getting details for a non-existent gem."""
    response = client.get("/api/v1/game/gems/nonexistent")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_invalid_gem_progression(client: TestClient):
    """Test getting progression data for a non-existent gem."""
    response = client.get("/api/v1/game/gems/nonexistent/progression")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_list_gem_stats(client: TestClient):
    """Test listing gem stats."""
    response = client.get("/api/v1/game/gems/stats")
    assert response.status_code == 200
    data = response.json()
    assert "CriticalHitChance" in data
    assert "DamageIncrease" in data
    assert "MovementSpeed" in data
    assert len(data["CriticalHitChance"]["Gems"]) > 0


def test_get_gem_stats(client: TestClient):
    """Test getting stats for a specific gem."""
    response = client.get("/api/v1/game/gems/berserker's%20eye/stats")
    assert response.status_code == 200
    data = response.json()
    assert "CriticalHitChance" in data
    assert "DamageIncrease" in data
    assert len(data["CriticalHitChance"]) > 0


def test_invalid_gem_stats(client: TestClient):
    """Test getting stats for a non-existent gem."""
    response = client.get("/api/v1/game/gems/nonexistent/stats")
    assert response.status_code == 404


def test_list_gem_synergies(client: TestClient):
    """Test listing gem synergies."""
    response = client.get("/api/v1/game/gems/synergies")
    assert response.status_code == 200
    data = response.json()
    assert "CriticalHit" in data
    assert "DamageBoost" in data
    assert "Control" in data
    assert len(data["CriticalHit"]["Gems"]) > 0


def test_get_gem_synergies(client: TestClient):
    """Test getting synergies for a specific gem."""
    response = client.get("/api/v1/game/gems/berserker's%20eye/synergies")
    assert response.status_code == 200
    data = response.json()
    assert "CriticalHit" in data
    assert "DamageBoost" in data
    assert "berserker's eye" in [g.lower() for g in data["CriticalHit"]["Gems"]]


def test_invalid_gem_synergies(client: TestClient):
    """Test getting synergies for a non-existent gem."""
    response = client.get("/api/v1/game/gems/nonexistent/synergies")
    assert response.status_code == 404


def test_list_gem_skills(client: TestClient):
    """Test listing gem skill types."""
    response = client.get("/api/v1/game/gems/skills")
    assert response.status_code == 200
    skills = response.json()
    assert isinstance(skills, list)
    assert "movement" in skills
    assert "primary attack" in skills
    assert "attack" in skills


def test_list_classes(client: TestClient):
    """Test listing available classes."""
    response = client.get("/api/v1/game/classes")
    assert response.status_code == 200
    data = response.json()
    assert "classes" in data
    assert isinstance(data["classes"], list)
    assert "barbarian" in data["classes"]


def test_get_class_details(client: TestClient):
    """Test getting class details."""
    response = client.get("/api/v1/game/classes/barbarian")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "barbarian"
    assert "skills" in data
    assert "mechanics" in data


def test_invalid_class_details(client: TestClient):
    """Test getting details for a non-existent class."""
    response = client.get("/api/v1/game/classes/nonexistent")
    assert response.status_code == 404


def test_list_stats(client: TestClient):
    """Test listing available stats."""
    response = client.get("/api/v1/game/stats")
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert isinstance(data["stats"], dict)
    # Check for common stat categories
    categories = data["stats"].keys()
    assert any(cat in categories for cat in ["offensive", "defensive", "utility"])


def test_get_stat_details(client: TestClient):
    """Test getting stat details."""
    # Get list of stats first
    response = client.get("/api/v1/game/stats")
    assert response.status_code == 200
    data = response.json()
    
    # Get first stat from offensive category
    first_stat = data["stats"]["offensive"][0]
    
    # Get details for that stat
    response = client.get(f"/api/v1/game/stats/{first_stat}")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "description" in data
    assert data["category"] == "offensive"


def test_invalid_stat_details(client: TestClient):
    """Test getting details for a non-existent stat."""
    response = client.get("/api/v1/game/stats/nonexistent")
    assert response.status_code == 404


def test_list_constraints(client: TestClient):
    """Test listing game constraints."""
    response = client.get("/api/v1/game/constraints")
    assert response.status_code == 200
    data = response.json()
    assert "constraints" in data
    assert isinstance(data["constraints"], dict)
    # Check for common constraint fields
    for constraint in data["constraints"].values():
        assert any(field in constraint for field in ["min_value", "max_value", "allowed_values"])


def test_list_synergies(client: TestClient):
    """Test listing available synergies."""
    response = client.get("/api/v1/game/synergies")
    assert response.status_code == 200
    data = response.json()
    assert "synergies" in data
    assert isinstance(data["synergies"], dict)
    # Check for common synergy types
    categories = data["synergies"].keys()
    assert all(cat in categories for cat in ["gems", "essences", "skills"])


def test_get_synergy_details(client: TestClient):
    """Test getting synergy details."""
    # Get list of synergies first
    response = client.get("/api/v1/game/synergies")
    assert response.status_code == 200
    data = response.json()
    
    # Get first synergy from gems category
    first_synergy = data["synergies"]["gems"][0]
    
    # Get details for that synergy
    response = client.get(f"/api/v1/game/synergies/{first_synergy}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "gems" in data
    assert "essences" in data
    assert "skills" in data
    assert "conditions" in data


def test_invalid_synergy_details(client: TestClient):
    """Test getting details for a non-existent synergy."""
    response = client.get("/api/v1/game/synergies/nonexistent")
    assert response.status_code == 404
