"""Tests for build generation and scoring.

TODO: This file will be consolidated into test_builds/test_skill_selection.py
Keep for now as it contains useful test data setup patterns.
"""

import json
import pytest
from pathlib import Path

from api.builds.models import BuildType, BuildFocus, Gem
from api.builds.service import BuildService


@pytest.fixture
def test_data_dir(tmp_path):
    """Create test data directory with minimal required data."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    # Create indexed data directory
    indexed_dir = data_dir / "indexed"
    indexed_dir.mkdir()
    
    # Create gems directory with synergies
    gems_dir = indexed_dir / "gems"
    gems_dir.mkdir()
    
    # Create minimal synergies.json
    synergies = {
        "damage_boost": {
            "gems": ["Berserker's Eye"],
            "skills": ["Cleave"]
        }
    }
    with open(gems_dir / "synergies.json", "w") as f:
        json.dump(synergies, f)
        
    # Create minimal class data
    class_dir = indexed_dir / "classes"
    class_dir.mkdir()
    barbarian_data = {
        "base_skills": {
            "registry": {
                "Cleave": {
                    "base_type": "damage",
                    "second_base_type": None,
                    "cooldown": "medium"
                }
            }
        }
    }
    with open(class_dir / "barbarian.json", "w") as f:
        json.dump(barbarian_data, f)
        
    return data_dir


def test_skill_score_gem_synergies(test_data_dir, monkeypatch):
    """Test that gem synergies are properly scored for skills.
    
    This test verifies that a skill with a matching gem synergy scores
    higher than the same skill without the synergistic gem.
    """
    # Initialize service with test data path
    service = BuildService()
    monkeypatch.setattr(service, "data_dir", test_data_dir)
    service.load_data()  # Reload with test data
    
    # Test parameters
    skill_name = "Cleave"
    build_type = BuildType.PVE
    focus = BuildFocus.DPS
    
    # Score without any gems
    score_without_gem = service._calculate_skill_score(
        skill_name=skill_name,
        build_type=build_type,
        focus=focus,
        selected_gems=[]
    )
    
    # Score with Berserker's Eye gem
    berserker_gem = Gem(name="Berserker's Eye", rank=1)
    score_with_gem = service._calculate_skill_score(
        skill_name=skill_name,
        build_type=build_type,
        focus=focus,
        selected_gems=[berserker_gem]
    )
    
    # Print scores for debugging
    print(f"\nScore without gem: {score_without_gem}")
    print(f"Score with gem: {score_with_gem}")
    
    # The score with the gem should be higher due to damage synergy
    assert score_with_gem > score_without_gem, (
        f"Expected score with Berserker's Eye ({score_with_gem}) to be higher than "
        f"score without gem ({score_without_gem}) for {skill_name}"
    )
