"""Tests for CLI functionality."""
import json
import pytest
from pathlib import Path
from cli import format_build_data, GemEffect, GemRankData, IndexedGem, StatValue, StatSource, BuildStats, FormattedBuildData

# Import test fixtures
from tests.unit.models.game_data.conftest import (
    sample_gems_data as base_gems_data,
    sample_equipment_sets_data as base_equipment_sets_data,
    sample_stats_data
)


@pytest.fixture
def sample_player_data():
    """Sample player data for testing."""
    return {
        "version": "1.0",
        "player": {
            "id": "test_player",
            "class": "barbarian"
        }
    }


@pytest.fixture
def sample_gems_data():
    """Sample gems data in the format expected by CLI."""
    return {
        "gems": {
            "Blood-Soaked Jade": [{
                "rank": 3,
                "quality": 2
            }]
        }
    }


@pytest.fixture
def sample_equipment_sets_data():
    """Sample equipment sets data in the format expected by CLI."""
    return {
        "sets": {
            "Grace of the Flagellant": [{
                "attributes": {
                    "damage": 15,
                    "effect": "DoT"
                }
            }]
        }
    }


@pytest.fixture
def mock_indexed_gems(tmp_path: Path) -> Path:
    """Create a mock indexed gems file for testing."""
    gems_data = {
        "Blood-Soaked Jade": {
            "stars": 3,
            "ranks": {
                "3": {
                    "effects": [{
                        "type": "stat_effect",
                        "text": "Critical Hit Chance increased by 4.5%",
                        "conditions": []
                    }]
                },
                "10": {
                    "effects": [{
                        "type": "stat_effect",
                        "text": "Critical Hit Chance increased by 9.0%",
                        "conditions": []
                    }]
                }
            }
        }
    }
    
    gems_file = tmp_path / "gems.json"
    with open(gems_file, "w") as f:
        json.dump(gems_data, f)
    return gems_file


def test_format_build_data_structure(sample_gems_data, sample_equipment_sets_data, sample_player_data, sample_stats_data):
    """Test that format_build_data produces the expected structure."""
    formatted = format_build_data(
        gems_data=sample_gems_data,
        sets_data=sample_equipment_sets_data,
        profile_data=sample_player_data
    )
    
    # Check top-level structure
    assert "metadata" in formatted
    assert formatted["metadata"]["version"] == "1.0.0"
    
    # Check profile structure
    assert "profile" in formatted
    assert formatted["profile"]["version"] == "1.0"
    assert formatted["profile"]["name"] == "test_player"
    assert formatted["profile"]["class"] == "barbarian"
    
    # Check stats structure
    assert "stats" in formatted
    assert set(formatted["stats"].keys()) == {
        "critical_hit_chance",
        "damage_increase"
    }
    
    # Check each stat category has the required structure
    for category in formatted["stats"]:
        assert "gems" in formatted["stats"][category]
        assert "essences" in formatted["stats"][category]
        assert isinstance(formatted["stats"][category]["gems"], list)
        assert isinstance(formatted["stats"][category]["essences"], list)
        
        # Check each gem in the category has the required fields
        for gem in formatted["stats"][category]["gems"]:
            assert "name" in gem
            assert "stars" in gem
            assert "base_values" in gem
            assert "rank_10_values" in gem
            assert "conditions" in gem
            assert "rank_10_conditions" in gem
            
            # Check value structure
            for value in gem["base_values"] + gem["rank_10_values"]:
                assert "value" in value
                assert "unit" in value
                assert "conditions" in value
                assert "scaling" in value
                assert value["unit"] == "percentage"
                assert isinstance(value["scaling"], bool)
                assert isinstance(value["conditions"], list)
    
    # Check gems structure if gems_data is provided
    if sample_gems_data:
        assert "gems" in formatted
        assert formatted["gems"]["version"] == "1.0"
        assert "gems" in formatted["gems"]
        
        # Check each gem has the required fields
        for gem_name, gem_list in formatted["gems"]["gems"].items():
            assert isinstance(gem_list, list)
            for gem in gem_list:
                assert "owned_rank" in gem
                assert "owned_quality" in gem
                assert isinstance(gem["owned_rank"], int)
                assert isinstance(gem["owned_quality"], int)
    
    # Check equipment structure if sets_data is provided
    if sample_equipment_sets_data:
        assert "equipment" in formatted
        assert formatted["equipment"]["version"] == "1.0"
        assert "sets" in formatted["equipment"]
        assert isinstance(formatted["equipment"]["sets"], list)
        
        # Check each set piece has the required fields
        for set_piece in formatted["equipment"]["sets"]:
            assert "name" in set_piece
            assert "attributes" in set_piece


def test_format_build_data_matches_api_schema(sample_gems_data, sample_stats_data):
    """Test that format_build_data output matches the API's expected schema."""
    formatted = format_build_data(gems_data=sample_gems_data)
    
    # Load the API's sample stats data
    api_stats = sample_stats_data
    
    # Compare structures
    assert set(formatted["stats"].keys()) == set(api_stats.keys())
    
    # Compare a known gem's structure
    if formatted["stats"]["critical_hit_chance"]["gems"]:
        cli_gem = formatted["stats"]["critical_hit_chance"]["gems"][0]
        api_gem = api_stats["critical_hit_chance"]["gems"][0]
        
        # Check all fields match
        assert set(cli_gem.keys()) == set(api_gem.keys())
        assert isinstance(cli_gem["stars"], str)  # Stars should be string
        assert isinstance(cli_gem["base_values"], list)
        assert isinstance(cli_gem["rank_10_values"], list)
        
        # Check value structure
        if cli_gem["base_values"]:
            cli_value = cli_gem["base_values"][0]
            api_value = api_gem["base_values"][0]
            assert set(cli_value.keys()) == set(api_value.keys())
            assert cli_value["unit"] == api_value["unit"]
            assert isinstance(cli_value["value"], (int, float))
            assert isinstance(cli_value["scaling"], bool)
            assert isinstance(cli_value["conditions"], list)


def test_format_build_data_with_empty_input():
    """Test format_build_data with no input data."""
    formatted = format_build_data()
    
    # Check basic structure is present
    assert "metadata" in formatted
    assert "stats" in formatted
    assert "profile" in formatted
    
    # Check default profile values
    assert formatted["profile"]["name"] is None
    assert formatted["profile"]["class"] == "barbarian"
    
    # Check stats categories are empty but present
    for category in formatted["stats"]:
        assert formatted["stats"][category]["gems"] == []
        assert formatted["stats"][category]["essences"] == []


def test_format_build_data_with_invalid_gems_file(monkeypatch: pytest.MonkeyPatch):
    """Test format_build_data handles missing gems file gracefully."""
    # Need to unset DATA_DIR to ensure we use the absolute path
    monkeypatch.delenv("DATA_DIR", raising=False)
    monkeypatch.setenv("INDEXED_GEMS_PATH", "/nonexistent/path/gems.json")
    
    with pytest.raises(FileNotFoundError) as exc_info:
        format_build_data(gems_data={"gems": {"Blood-Soaked Jade": [{"rank": 3}]}})
    assert "Indexed gems file not found at" in str(exc_info.value)


def test_format_build_data_with_invalid_gems_data(mock_indexed_gems: Path, monkeypatch: pytest.MonkeyPatch):
    """Test format_build_data handles invalid gems data gracefully."""
    monkeypatch.setenv("INDEXED_GEMS_PATH", str(mock_indexed_gems))
    
    # Test with missing rank
    with pytest.raises(ValueError) as exc_info:
        format_build_data(gems_data={"gems": {"Blood-Soaked Jade": [{"quality": 2}]}})
    assert "missing required field 'rank'" in str(exc_info.value)
    
    # Test with invalid gem name
    result = format_build_data(gems_data={"gems": {"NonexistentGem": [{"rank": 3}]}})
    assert len(result["stats"]["critical_hit_chance"]["gems"]) == 0
    
    # Test with invalid rank
    result = format_build_data(gems_data={"gems": {"Blood-Soaked Jade": [{"rank": 999}]}})
    assert len(result["stats"]["critical_hit_chance"]["gems"]) == 0


def test_format_build_data_type_validation(mock_indexed_gems: Path, monkeypatch: pytest.MonkeyPatch):
    """Test that format_build_data returns data matching our type definitions."""
    monkeypatch.setenv("INDEXED_GEMS_PATH", str(mock_indexed_gems))
    
    result = format_build_data(
        gems_data={"gems": {"Blood-Soaked Jade": [{"rank": 3, "quality": 2}]}},
        sets_data={"sets": {"Grace of the Flagellant": [{"attributes": {"damage": 15}}]}},
        profile_data={"player": {"id": "test_player", "class": "barbarian"}}
    )
    
    # Validate top-level structure matches FormattedBuildData
    assert isinstance(result, dict)
    assert set(result.keys()) >= {"metadata", "stats", "profile", "gems", "equipment"}
    
    # Validate stats structure matches BuildStats
    for stat_type in result["stats"]:
        stat_data = result["stats"][stat_type]
        assert isinstance(stat_data, dict)
        assert set(stat_data.keys()) == {"gems", "essences"}
        assert isinstance(stat_data["gems"], list)
        assert isinstance(stat_data["essences"], list)
        
        # Validate gem stats match StatSource
        for gem in stat_data["gems"]:
            assert isinstance(gem, dict)
            assert set(gem.keys()) == {"name", "stars", "base_values", "rank_10_values", "conditions", "rank_10_conditions"}
            
            # Validate stat values match StatValue
            for value in gem["base_values"] + gem["rank_10_values"]:
                assert isinstance(value, dict)
                assert set(value.keys()) == {"value", "unit", "conditions", "scaling"}
                assert isinstance(value["value"], (int, float))
                assert isinstance(value["unit"], str)
                assert isinstance(value["conditions"], list)
                assert isinstance(value["scaling"], bool)
