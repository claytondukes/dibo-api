"""Equipment sets endpoint tests."""

from fastapi.testclient import TestClient
import json
from pathlib import Path
from datetime import datetime

def test_list_sets(client: TestClient) -> None:
    """Test equipment sets listing endpoint."""
    response = client.get("/api/v1/game/sets")
    assert response.status_code == 200
    
    data = response.json()
    assert "sets" in data
    assert isinstance(data["sets"], list)
    assert "page" in data
    assert "per_page" in data
    assert "total" in data
    
    # Verify pagination defaults
    assert data["page"] == 1
    assert data["per_page"] == 20
    assert data["total"] >= 0
    
    # Test filtering by pieces
    response = client.get("/api/v1/game/sets?pieces=2")
    assert response.status_code == 200
    filtered_data = response.json()
    assert all(set_info["pieces"] >= 2 for set_info in filtered_data["sets"])

    # Test individual set details
    sets_file = Path("/Users/cdukes/sourcecode/dibo-api/data/indexed/sets.json")
    with open(sets_file) as f:
        sets_data = json.load(f)
        if "registry" in sets_data and sets_data["registry"]:
            set_name = next(iter(sets_data["registry"]))
            response = client.get(f"/api/v1/game/sets/{set_name}")
            assert response.status_code == 200
            set_details = response.json()
            assert set_details["name"] == set_name
            assert "pieces" in set_details
            assert "description" in set_details
            assert "bonuses" in set_details
            assert "use_case" in set_details
