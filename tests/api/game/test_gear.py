"""Gear endpoint tests."""

from fastapi.testclient import TestClient
from pathlib import Path

def test_list_gear(client: TestClient) -> None:
    """Test gear listing endpoint."""
    response = client.get("/api/v1/game/gear")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    
    # Test filtering by class
    response = client.get("/api/v1/game/gear", params={"class": "barbarian"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    
    # Test filtering by slot
    response = client.get("/api/v1/game/gear", params={"slot": "head"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

def test_list_essences(client: TestClient) -> None:
    """Test class-specific essences endpoint."""
    # Get valid class from data/indexed/classes
    data_path = Path("/Users/cdukes/sourcecode/dibo-api/data/indexed/classes")
    valid_class = next(data_path.iterdir()).name
    
    response = client.get(f"/api/v1/game/gear/{valid_class}/essences")
    assert response.status_code == 200
    data = response.json()
    assert "essences" in data
    assert isinstance(data["essences"], list)
    
    # Test with invalid class
    response = client.get("/api/v1/game/gear/invalid_class/essences")
    assert response.status_code == 404
