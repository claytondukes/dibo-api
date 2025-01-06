"""Integration tests for gear-related endpoints."""

import pytest
from fastapi.testclient import TestClient

from api.core.config import get_settings
from api.main import create_app
from api.models.game_data.data_manager import GameDataManager


@pytest.fixture
def client(data_manager: GameDataManager) -> TestClient:
    """Create a test client."""
    app = create_app()
    app.state.data_manager = data_manager
    return TestClient(app)


def test_list_gear(client: TestClient) -> None:
    """Test listing gear items with no filters."""
    settings = get_settings()
    response = client.get(f"{settings.API_V1_STR}/game/gear")
    
    # TODO: Update test once gear data is available
    # For now, expect a 501 Not Implemented response
    assert response.status_code == 501
    assert "Missing required data file" in response.json()["detail"]
