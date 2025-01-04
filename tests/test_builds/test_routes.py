"""Test build routes."""

import pytest
from fastapi.testclient import TestClient

from api.builds.models import BuildFocus, BuildType
from api.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.mark.parametrize("character_class", [
    "barbarian",
    "crusader",
    "demon-hunter",
    "monk",
    "necromancer",
    "wizard"
])
def test_generate_build_for_class(client, character_class):
    """Test build generation for each character class."""
    response = client.get(
        "/api/v1/builds/generate",
        params={
            "build_type": "pve",
            "focus": "dps",
            "use_inventory": False,
            "character_class": character_class
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "build" in data
    assert "stats" in data
    assert "recommendations" in data
    
    # Verify build details
    build = data["build"]
    assert build["character_class"] == character_class
    assert "skills" in build
    assert len(build["skills"]) <= 6  # Maximum 6 skills per build
    assert "gems" in build
    assert "equipment" in build
    
    # Verify stats calculation
    stats = data["stats"]
    assert "damage" in stats
    assert "defense" in stats
    assert "utility" in stats
    assert all(isinstance(v, (int, float)) for v in stats.values())
    
    # Verify recommendations
    recommendations = data["recommendations"]
    assert "priority_stats" in recommendations
    assert "suggested_playstyle" in recommendations
    assert isinstance(recommendations["priority_stats"], list)
    assert len(recommendations["priority_stats"]) > 0


@pytest.mark.parametrize("build_type,focus", [
    (BuildType.PVE, BuildFocus.DPS),
    (BuildType.PVP, BuildFocus.SURVIVAL),
    (BuildType.RAID, BuildFocus.BUFF),
    (BuildType.FARM, BuildFocus.DPS)
])
def test_generate_build_types_and_focus(client, build_type, focus):
    """Test build generation with different types and focus."""
    response = client.get(
        "/api/v1/builds/generate",
        params={
            "build_type": build_type.value.lower(),
            "focus": focus.value.lower(),
            "use_inventory": False,
            "character_class": "barbarian"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify build aligns with type and focus
    build = data["build"]
    assert "optimization_goals" in build
    goals = build["optimization_goals"]
    
    if focus == BuildFocus.DPS:
        assert "damage" in goals
        assert goals["damage"] > goals.get("defense", 0)
    elif focus == BuildFocus.SURVIVAL:
        assert "defense" in goals
        assert goals["defense"] > goals.get("damage", 0)
    elif focus == BuildFocus.BUFF:
        assert "utility" in goals
        
    # Verify build type specific requirements
    if build_type == BuildType.PVP:
        assert "crowd_control" in data["stats"]
    elif build_type == BuildType.RAID:
        assert "boss_damage" in data["stats"]
    elif build_type == BuildType.FARM:
        assert "movement_speed" in data["stats"]


def test_generate_build_with_inventory(client, mock_auth_token):
    """Test build generation with user's inventory."""
    response = client.get(
        "/api/v1/builds/generate",
        params={
            "build_type": "pvp",
            "focus": "survival",
            "use_inventory": True,
            "character_class": "barbarian"
        },
        headers={"Authorization": f"Bearer {mock_auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify inventory integration
    build = data["build"]
    assert "inventory_usage" in build
    usage = build["inventory_usage"]
    assert "gems_from_inventory" in usage
    assert "equipment_from_inventory" in usage
    assert isinstance(usage["gems_from_inventory"], list)
    assert isinstance(usage["equipment_from_inventory"], list)


def test_generate_build_inventory_unauthorized(client):
    """Test build generation with inventory but no auth."""
    response = client.get(
        "/api/v1/builds/generate",
        params={
            "build_type": "pve",
            "focus": "dps",
            "use_inventory": True,
            "character_class": "barbarian"
        }
    )
    
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_generate_build_invalid_params(client):
    """Test build generation with various invalid parameters."""
    # Invalid build type
    response = client.get(
        "/api/v1/builds/generate",
        params={
            "build_type": "invalid",
            "focus": "dps",
            "use_inventory": False,
            "character_class": "barbarian"
        }
    )
    assert response.status_code == 422
    
    # Invalid focus
    response = client.get(
        "/api/v1/builds/generate",
        params={
            "build_type": "pve",
            "focus": "invalid",
            "use_inventory": False,
            "character_class": "barbarian"
        }
    )
    assert response.status_code == 422
    
    # Invalid character class
    response = client.get(
        "/api/v1/builds/generate",
        params={
            "build_type": "pve",
            "focus": "dps",
            "use_inventory": False,
            "character_class": "invalid-class"
        }
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_build_missing_data(client, monkeypatch):
    """Test build generation with missing game data."""
    async def mock_missing_data(*args, **kwargs):
        raise FileNotFoundError("Missing game data")
    
    monkeypatch.setattr(
        "api.builds.service.BuildService.load_class_data",
        mock_missing_data
    )
    
    response = client.get(
        "/api/v1/builds/generate",
        params={
            "build_type": "pve",
            "focus": "dps",
            "use_inventory": False,
            "character_class": "barbarian"
        }
    )
    
    assert response.status_code == 500
    assert "Failed to load game data" in response.json()["detail"]


def test_analyze_build_success(client):
    """Test successful build analysis."""
    build_config = {
        "character_class": "barbarian",
        "skills": [
            {"id": "whirlwind", "essence": "dust_devils"},
            {"id": "sprint", "essence": "marathon"},
            {"id": "leap", "essence": "death_from_above"}
        ],
        "gems": [
            {"id": "berserkers_eye", "rank": 5},
            {"id": "power_and_command", "rank": 4}
        ],
        "equipment": [
            {"slot": "head", "set": "grace_of_the_flagellant"},
            {"slot": "chest", "set": "grace_of_the_flagellant"}
        ]
    }
    
    response = client.post(
        "/api/v1/builds/analyze",
        json=build_config
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify analysis structure
    assert "stats" in data
    assert "synergies" in data
    assert "recommendations" in data
    
    # Verify stat calculations
    stats = data["stats"]
    assert "damage" in stats
    assert "defense" in stats
    assert "utility" in stats
    assert all(isinstance(v, (int, float)) for v in stats.values())
    
    # Verify synergy analysis
    synergies = data["synergies"]
    assert "skill_synergies" in synergies
    assert "set_bonuses" in synergies
    assert "gem_interactions" in synergies
    
    # Verify recommendations
    recommendations = data["recommendations"]
    assert "suggested_improvements" in recommendations
    assert "alternative_options" in recommendations


def test_analyze_build_invalid_class(client):
    """Test build analysis with invalid character class."""
    build_config = {
        "character_class": "invalid-class",
        "skills": [],
        "gems": [],
        "equipment": []
    }
    
    response = client.post(
        "/api/v1/builds/analyze",
        json=build_config
    )
    
    assert response.status_code == 422
    assert "Invalid character class" in response.json()["detail"]


def test_analyze_build_invalid_skill(client):
    """Test build analysis with invalid skill configuration."""
    build_config = {
        "character_class": "barbarian",
        "skills": [
            {"id": "invalid_skill", "essence": "dust_devils"}
        ],
        "gems": [],
        "equipment": []
    }
    
    response = client.post(
        "/api/v1/builds/analyze",
        json=build_config
    )
    
    assert response.status_code == 422
    assert "Invalid skill configuration" in response.json()["detail"]


def test_analyze_build_invalid_essence(client):
    """Test build analysis with invalid essence configuration."""
    build_config = {
        "character_class": "barbarian",
        "skills": [
            {"id": "whirlwind", "essence": "invalid_essence"}
        ],
        "gems": [],
        "equipment": []
    }
    
    response = client.post(
        "/api/v1/builds/analyze",
        json=build_config
    )
    
    
    assert response.status_code == 422
    assert "Invalid essence configuration" in response.json()["detail"]


def test_analyze_build_invalid_gem(client):
    """Test build analysis with invalid gem configuration."""
    build_config = {
        "character_class": "barbarian",
        "skills": [],
        "gems": [
            {"id": "invalid_gem", "rank": 5}
        ],
        "equipment": []
    }
    
    response = client.post(
        "/api/v1/builds/analyze",
        json=build_config
    )
    
    assert response.status_code == 422
    assert "Invalid gem configuration" in response.json()["detail"]


@pytest.mark.asyncio
async def test_analyze_build_missing_data(client, monkeypatch):
    """Test build analysis with missing game data."""
    async def mock_missing_data(*args, **kwargs):
        raise FileNotFoundError("Missing game data")
    
    monkeypatch.setattr(
        "api.builds.service.BuildService.load_class_data",
        mock_missing_data
    )
    
    build_config = {
        "character_class": "barbarian",
        "skills": [],
        "gems": [],
        "equipment": []
    }
    
    response = client.post(
        "/api/v1/builds/analyze",
        json=build_config
    )
    
    assert response.status_code == 500
    assert "Failed to load game data" in response.json()["detail"]
