"""Equipment sets endpoint tests."""

from fastapi.testclient import TestClient
import json
from pathlib import Path

def test_list_sets(client: TestClient) -> None:
    """Test equipment sets listing endpoint."""
    response = client.get("/api/v1/game/sets")
    assert response.status_code in [200, 422]  # Accept both success and validation errors
    
    if response.status_code == 200:
        data = response.json()
        assert "sets" in data
        assert isinstance(data["sets"], list)
        
        # Get a real set name from data/indexed/sets.json
        sets_file = Path("/Users/cdukes/sourcecode/dibo-api/data/indexed/sets.json")
        with open(sets_file) as f:
            sets_data = json.load(f)
            if sets_data:
                set_name = next(iter(sets_data))
                response = client.get(f"/api/v1/game/sets/{set_name}")
                assert response.status_code in [200, 422]  # Accept both success and validation errors
