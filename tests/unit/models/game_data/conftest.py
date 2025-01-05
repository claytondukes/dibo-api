"""
Pytest fixtures for game data tests.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.tmpdir import TempPathFactory


@pytest.fixture
def sample_metadata() -> Dict[str, Any]:
    """Sample metadata for testing."""
    return {
        "last_updated": "2025-01-05T16:49:39-05:00",
        "version": "1.0",
        "data_structure_version": "1.0"
    }


@pytest.fixture
def sample_gem() -> Dict[str, Any]:
    """Sample gem data for testing."""
    return {
        "Stars": 5,
        "Name": "Blood-Soaked Jade",
        "Base Effect": "Up to 8% increased damage",
        "Rank 10 Effect": "Increases all damage by 32%",
        "Owned Rank": 10,
        "Quality (if 5 star)": 5
    }


@pytest.fixture
def sample_gems_data() -> Dict[str, Any]:
    """Sample gems collection for testing."""
    return {
        "gems_by_skill": {
            "movement": [
                {
                    "Stars": 5,
                    "Name": "Blood-Soaked Jade",
                    "Base Effect": "Up to 8% increased damage",
                    "Rank 10 Effect": "Increases all damage by 32%",
                    "Owned Rank": 10,
                    "Quality (if 5 star)": 5
                }
            ],
            "primary attack": [],
            "attack": [],
            "summon": [],
            "channeled": []
        }
    }


@pytest.fixture
def mock_data_dir(
    tmp_path_factory: TempPathFactory,
    sample_metadata: Dict[str, Any],
    sample_gems_data: Dict[str, Any]
) -> Path:
    """Create a temporary data directory with mock files."""
    base_dir = tmp_path_factory.mktemp("data")
    
    # Create metadata file
    with open(base_dir / "metadata.json", "w") as f:
        json.dump(sample_metadata, f)
    
    # Create gems directory and file
    gems_dir = base_dir / "gems"
    gems_dir.mkdir()
    with open(gems_dir / "gems.json", "w") as f:
        json.dump(sample_gems_data, f)
    
    return base_dir
