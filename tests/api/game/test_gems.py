"""Tests for gem-related endpoints."""

import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.models.game_data.schemas.synergies import SynergyCondition
from api.core.config import get_settings


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client fixture."""
    return TestClient(app)


def test_synergy_files_use_description(client: TestClient):
    """Test that both synergy files use 'description' consistently."""
    data_path = Path(get_settings().data_path)
    
    # Check main synergies file
    synergies_file = data_path / "synergies.json"
    assert synergies_file.exists(), f"File not found: {synergies_file}"
    
    with open(synergies_file) as f:
        synergies_data = json.load(f)
        
    # Check all conditions use 'description'
    for synergy_type, synergy_data in synergies_data.items():
        if not isinstance(synergy_data, dict) or "conditions" not in synergy_data:
            continue
            
        for conditions in synergy_data["conditions"].values():
            for condition in conditions:
                assert "text" not in condition, f"Found 'text' in {synergy_type} conditions"
                assert "description" in condition, f"Missing 'description' in {synergy_type} conditions"
                
    # Check gem synergies file
    gem_synergies_file = data_path / "gems" / "synergies.json"
    assert gem_synergies_file.exists(), f"File not found: {gem_synergies_file}"
    
    with open(gem_synergies_file) as f:
        gem_synergies_data = json.load(f)
        
    # Check all conditions use 'description'
    for synergy_type, synergy_data in gem_synergies_data.items():
        if not isinstance(synergy_data, dict) or "conditions" not in synergy_data:
            continue
            
        for conditions in synergy_data["conditions"].values():
            for condition in conditions:
                assert "text" not in condition, f"Found 'text' in {synergy_type} conditions"
                assert "description" in condition, f"Missing 'description' in {synergy_type} conditions"


def test_synergy_condition_model(client: TestClient):
    """Test that SynergyCondition model validates correctly."""
    condition = SynergyCondition(
        type="trigger",
        trigger="on_hit",
        description="when hit"
    )
    assert condition.description == "when hit"
