"""Tests for the builds API endpoints."""

from fastapi.testclient import TestClient


def test_generate_build_basic(client: TestClient):
    """Test basic build generation."""
    response = client.post(
        "/api/v1/game/builds/generate",
        params={
            "build_type": "raid",
            "focus": "dps",
            "save": False,
            "use_inventory": False,
            "character_class": "barbarian"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "class_type" in data
    assert data["class_type"] == "barbarian"


def test_generate_build_invalid_class(client: TestClient):
    """Test build generation with invalid class."""
    response = client.post(
        "/api/v1/game/builds/generate",
        params={
            "build_type": "raid",
            "focus": "dps",
            "save": False,
            "use_inventory": False,
            "character_class": "invalid_class"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid character class" in data["detail"]["message"]


def test_generate_build_invalid_type(client: TestClient):
    """Test build generation with invalid build type."""
    response = client.post(
        "/api/v1/game/builds/generate",
        params={
            "build_type": "invalid_type",
            "focus": "dps",
            "save": False,
            "use_inventory": False,
            "character_class": "barbarian"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid build type" in data["detail"]["message"]


def test_generate_build_invalid_focus(client: TestClient):
    """Test build generation with invalid focus."""
    response = client.post(
        "/api/v1/game/builds/generate",
        params={
            "build_type": "raid",
            "focus": "invalid_focus",
            "save": False,
            "use_inventory": False,
            "character_class": "barbarian"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid focus type" in data["detail"]["message"]


def test_generate_and_save_build(client: TestClient):
    """Test build generation with save option."""
    response = client.post(
        "/api/v1/game/builds/generate",
        params={
            "build_type": "raid",
            "focus": "dps",
            "save": True,
            "use_inventory": False,
            "character_class": "barbarian"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "id" in data  # Should have a gist ID when saved
    assert "class_type" in data
    assert data["class_type"] == "barbarian"


def test_generate_build_with_inventory(client: TestClient):
    """Test build generation using inventory."""
    response = client.post(
        "/api/v1/game/builds/generate",
        params={
            "build_type": "raid",
            "focus": "dps",
            "save": False,
            "use_inventory": True,
            "character_class": "barbarian"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "class_type" in data
    assert data["class_type"] == "barbarian"
    # Additional inventory-specific assertions can be added here
