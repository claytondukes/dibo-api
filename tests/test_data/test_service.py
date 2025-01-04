"""Tests for game data service."""

import json
import pytest
from fastapi import HTTPException

from api.data.models import BuildCategory
from api.data.service import DataService


def test_data_service_initialization(tmp_path):
    """Test DataService initialization with missing data."""
    data_dir = tmp_path / "data" / "indexed"
    data_dir.mkdir(parents=True)

    # Test missing gems data
    with pytest.raises(HTTPException) as exc_info:
        DataService(data_dir=data_dir)
    assert "Error loading data files" in str(exc_info.value.detail)

    # Create empty gems directory
    (data_dir / "gems").mkdir()
    with pytest.raises(HTTPException) as exc_info:
        DataService(data_dir=data_dir)
    assert "Error loading data files" in str(exc_info.value.detail)


def test_get_gems(mock_data_service):
    """Test getting gems without filters."""
    result = mock_data_service.get_gems()
    
    assert result.total == 2
    assert len(result.items) == 2
    assert result.page == 1
    assert result.per_page == 20

    # Verify first gem
    gem = result.items[0]
    assert gem.name == "Freedom and Devotion"
    assert gem.stars == 2
    assert gem.base_effect == "Increases Movement Speed by 10%"
    assert gem.rank_10_effect == "Increases Movement Speed by 20%"
    assert BuildCategory.MOVEMENT in gem.categories

    # Verify second gem
    gem = result.items[1]
    assert gem.name == "Lightning Core"
    assert gem.stars == 5
    assert BuildCategory.ATTACK in gem.categories


def test_get_gems_with_filters(mock_data_service):
    """Test getting gems with filters."""
    # Filter by stars
    result = mock_data_service.get_gems(stars=5)
    assert result.total == 1
    assert result.items[0].name == "Lightning Core"

    # Filter by category
    result = mock_data_service.get_gems(category=BuildCategory.MOVEMENT)
    assert result.total == 1
    assert result.items[0].name == "Freedom and Devotion"

    # Filter with no matches
    result = mock_data_service.get_gems(stars=1)
    assert result.total == 0
    assert len(result.items) == 0


def test_get_sets(mock_data_service):
    """Test getting equipment sets without filters."""
    result = mock_data_service.get_sets()
    
    assert result.total == 2
    assert len(result.items) == 2

    # Verify first set
    set_data = result.items[0]
    assert set_data.name == "Grace of the Flagellant"
    assert set_data.description == "A powerful set for damage dealers"
    assert set_data.bonuses == {
        "2": "+15% damage",
        "4": "+30% damage",
        "6": "+50% damage"
    }
    assert set_data.use_case == "Best for high damage builds"


def test_get_sets_with_filters(mock_data_service):
    """Test getting equipment sets with filters."""
    # Filter by pieces
    result = mock_data_service.get_sets(pieces=4)
    assert result.total == 1
    assert result.items[0].name == "Shepherd's Call to Wolves"

    # Filter with no matches
    result = mock_data_service.get_sets(pieces=2)
    assert result.total == 0
    assert len(result.items) == 0


def test_get_skills(mock_data_service):
    """Test getting skills without filters."""
    result = mock_data_service.get_skills("barbarian")
    
    assert result.total == 2
    assert len(result.items) == 2

    # Verify first skill
    skill = result.items[0]
    assert skill.name == "Whirlwind"
    assert skill.description == "Spin to win"
    assert skill.cooldown == 8.0
    assert BuildCategory.ATTACK in skill.categories
    assert BuildCategory.CHANNELED in skill.categories


def test_get_skills_with_filters(mock_data_service):
    """Test getting skills with filters."""
    # Filter by category
    result = mock_data_service.get_skills(
        "barbarian",
        category=BuildCategory.MOVEMENT
    )
    assert result.total == 1
    assert result.items[0].name == "Sprint"

    # Filter with no matches
    result = mock_data_service.get_skills(
        "barbarian",
        category=BuildCategory.UTILITY
    )
    assert result.total == 0
    assert len(result.items) == 0


def test_get_skills_invalid_class(mock_data_service):
    """Test getting skills for invalid class."""
    with pytest.raises(HTTPException) as exc_info:
        mock_data_service.get_skills("invalid_class")
    
    assert exc_info.value.status_code == 404
    assert "Character class not found" in str(exc_info.value.detail)


def test_pagination(mock_data_service):
    """Test pagination functionality."""
    # Test first page
    result = mock_data_service.get_gems(per_page=1)
    assert result.total == 2
    assert result.page == 1
    assert result.per_page == 1
    assert len(result.items) == 1
    assert result.items[0].name == "Freedom and Devotion"

    # Test second page
    result = mock_data_service.get_gems(page=2, per_page=1)
    assert result.total == 2
    assert result.page == 2
    assert result.per_page == 1
    assert len(result.items) == 1
    assert result.items[0].name == "Lightning Core"

    # Test empty page
    result = mock_data_service.get_gems(page=3, per_page=1)
    assert result.total == 2
    assert result.page == 3
    assert result.per_page == 1
    assert len(result.items) == 0


def test_get_stats(mock_data_service):
    """Test getting all stats without filters."""
    result = mock_data_service.get_stats()

    # Verify basic structure
    assert "critical_hit_chance" in result
    assert "damage_increase" in result
    assert "attack_speed" in result
    assert "movement_speed" in result
    assert "life" in result

    # Verify stat details
    crit = result["critical_hit_chance"]
    assert len(crit.gems) > 0
    assert len(crit.essences) >= 0

    # Verify a specific gem
    berserker = crit.gems[0]
    assert berserker.name == "Berserker's Eye"
    assert berserker.stars == "1"
    assert len(berserker.rank_10_values) > 0
    assert berserker.rank_10_values[0].value == 2.0


def test_get_stats_filter_by_stat(mock_data_service):
    """Test getting a specific stat."""
    result = mock_data_service.get_stats(stat="critical_hit_chance")

    # Verify stat details
    assert len(result.gems) > 0
    assert len(result.essences) >= 0

    # Verify a specific gem
    berserker = result.gems[0]
    assert berserker.name == "Berserker's Eye"
    assert berserker.stars == "1"
    assert len(berserker.rank_10_values) > 0
    assert berserker.rank_10_values[0].value == 2.0


def test_get_stats_invalid_stat(mock_data_service):
    """Test getting an invalid stat."""
    with pytest.raises(HTTPException) as exc_info:
        mock_data_service.get_stats(stat="invalid_stat")
    assert exc_info.value.status_code == 404
    assert "Stat not found" in str(exc_info.value.detail)
