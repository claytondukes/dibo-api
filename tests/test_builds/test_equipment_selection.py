import pytest
from pathlib import Path
from typing import Dict, List, Optional

from api.builds.models import BuildFocus, BuildType, Equipment, Gem, Skill
from api.builds.service import BuildService

@pytest.fixture
def build_service(tmp_path: Path) -> BuildService:
    """Create a BuildService with test data."""
    # Create test data directory
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    # Create test equipment data
    gear_data = {
        "head": {
            "test_helm": {
                "base_stats": {
                    "life": 100,
                    "armor": 50
                },
                "essence_mods": {
                    "test_essence": {
                        "damage": 20,
                        "critical_hit": 10
                    }
                },
                "skill_mods": {
                    "test_skill": {
                        "damage": 30
                    }
                },
                "gem_mods": {
                    "test_gem": {
                        "effect_bonus": 20
                    }
                }
            }
        }
    }
    
    # Create test set data
    set_data = {
        "test_set": {
            "bonus_2pc": {
                "damage": 10,
                "life": 5
            },
            "bonus_4pc": {
                "critical_hit": 20,
                "attack_speed": 15
            },
            "bonus_6pc": {
                "damage": 40,
                "penetration": 30
            },
            "pieces": {
                "test_ring": {
                    "base_stats": {
                        "damage": 50,
                        "critical_hit": 20
                    }
                },
                "test_neck": {
                    "base_stats": {
                        "damage": 40,
                        "life": 30
                    }
                }
            },
            "skill_synergies": {
                "test_skill": {
                    "damage": 20
                }
            },
            "gem_synergies": {
                "test_gem": {
                    "effect_bonus": 15
                }
            }
        }
    }
    
    # Write test data files
    (data_dir / "equipment").mkdir()
    (data_dir / "equipment" / "gear.json").write_text(str(gear_data))
    (data_dir / "equipment" / "sets.json").write_text(str(set_data))
    
    return BuildService(data_dir=data_dir)

def test_select_gear_piece(build_service: BuildService):
    """Test selecting a gear piece."""
    # Test data
    selected_gems = [
        Gem(name="test_gem", rank=10, quality=5, aux_gem=None)
    ]
    selected_skills = [
        Skill(name="test_skill", rank=1, essence=None)
    ]
    
    # Test with no inventory
    piece = build_service._select_gear_piece(
        slot="head",
        build_type=BuildType.PVE,
        focus=BuildFocus.DPS,
        selected_gems=selected_gems,
        selected_skills=selected_skills,
        inventory=None
    )
    
    assert piece.name == "test_helm"
    assert piece.slot == "head"
    assert piece.rank is None
    assert piece.quality is None
    assert piece.essence is None
    
    # Test with inventory
    inventory = {
        "head": {
            "test_helm": {
                "rank": 10,
                "quality": 5,
                "essence": "test_essence"
            }
        }
    }
    
    piece = build_service._select_gear_piece(
        slot="head",
        build_type=BuildType.PVE,
        focus=BuildFocus.DPS,
        selected_gems=selected_gems,
        selected_skills=selected_skills,
        inventory=inventory
    )
    
    assert piece.name == "test_helm"
    assert piece.slot == "head"
    assert piece.rank == 10
    assert piece.quality == 5
    assert piece.essence == "test_essence"

def test_select_set_pieces(build_service: BuildService):
    """Test selecting set pieces."""
    # Test data
    selected_gems = [
        Gem(name="test_gem", rank=10, quality=5, aux_gem=None)
    ]
    selected_skills = [
        Skill(name="test_skill", rank=1, essence=None)
    ]
    
    # Test with no inventory
    pieces = build_service._select_set_pieces(
        build_type=BuildType.PVE,
        focus=BuildFocus.DPS,
        selected_gems=selected_gems,
        selected_skills=selected_skills,
        inventory=None
    )
    
    assert len(pieces) == 8  # Should select 8 pieces total
    assert any(p.name == "test_ring" for p in pieces)
    assert any(p.name == "test_neck" for p in pieces)
    
    # Test with inventory
    inventory = {
        "test_ring": {
            "slot": "ring1",
            "rank": 10,
            "quality": 5,
            "essence": None
        },
        "test_neck": {
            "slot": "neck",
            "rank": 8,
            "quality": 4,
            "essence": None
        }
    }
    
    pieces = build_service._select_set_pieces(
        build_type=BuildType.PVE,
        focus=BuildFocus.DPS,
        selected_gems=selected_gems,
        selected_skills=selected_skills,
        inventory=inventory
    )
    
    assert len(pieces) == 8
    ring = next(p for p in pieces if p.name == "test_ring")
    assert ring.slot == "ring1"
    assert ring.rank == 10
    assert ring.quality == 5
    
    neck = next(p for p in pieces if p.name == "test_neck")
    assert neck.slot == "neck"
    assert neck.rank == 8
    assert neck.quality == 4

def test_calculate_equipment_score(build_service: BuildService):
    """Test calculating equipment score."""
    # Test data
    selected_gems = [
        Gem(name="test_gem", rank=10, quality=5, aux_gem=None)
    ]
    selected_skills = [
        Skill(name="test_skill", rank=1, essence=None)
    ]
    
    # Test scoring a piece
    score = build_service._calculate_equipment_score(
        piece_name="test_helm",
        slot="head",
        data=build_service.equipment_data["gear"]["head"]["test_helm"],
        build_type=BuildType.PVE,
        focus=BuildFocus.DPS,
        selected_gems=selected_gems,
        selected_skills=selected_skills
    )
    
    assert 0.0 <= score <= 1.0
    assert score > 0.0  # Should have some score due to DPS stats

def test_calculate_set_score(build_service: BuildService):
    """Test calculating set score."""
    # Test data
    selected_gems = [
        Gem(name="test_gem", rank=10, quality=5, aux_gem=None)
    ]
    selected_skills = [
        Skill(name="test_skill", rank=1, essence=None)
    ]
    
    # Test scoring a set
    score = build_service._calculate_set_score(
        set_name="test_set",
        data=build_service.equipment_data["sets"]["test_set"],
        build_type=BuildType.PVE,
        focus=BuildFocus.DPS,
        selected_gems=selected_gems,
        selected_skills=selected_skills
    )
    
    assert 0.0 <= score <= 1.0
    assert score > 0.0  # Should have some score due to DPS bonuses
