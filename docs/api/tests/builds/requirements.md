# Build Requirements Tests

## Overview

This document tracks the implementation and testing status of the build requirements system, which ensures that generated builds adhere to class-specific, build type, and focus-specific requirements.

## Test Status (2025-01-04)

### ✅ Implemented Tests

1. `test_build_specific_requirements`:
   - Class-specific requirements validation
   - Build type constraints validation
   - Focus-specific needs validation
   
   ```python
   @pytest.mark.asyncio
   async def test_build_specific_requirements(mock_data_dir):
       """Test that builds respect class, type and focus specific requirements."""
       # Tests class constraints (weapon types, skill categories)
       # Tests build type requirements (PvE vs PvP)
       # Tests focus-specific requirements (DPS vs Survival)
   ```

### Test Coverage

1. Class Requirements:
   - Weapon type restrictions
   - Skill category requirements
   - Incompatible skill combinations
   - Required skill category counts

2. Build Type Requirements:
   - PvE specific requirements:
     - AoE skill requirements
     - Control skill requirements
   - PvP specific requirements:
     - Mobility requirements
     - Control skill requirements

3. Focus Requirements:
   - DPS focus:
     - Minimum damage category skills
     - Critical hit thresholds
     - Attack speed requirements
   - Survival focus:
     - Defense category requirements
     - Healing skill requirements
     - Life and armor thresholds

## Implementation Details

### Class Requirements
```json
{
    "weapon_types": ["two_handed_axe", "two_handed_sword"],
    "skill_categories": ["melee", "buff", "mobility"],
    "required_categories": {
        "melee": 2,
        "buff": 1
    },
    "incompatible_skills": [
        ["whirlwind", "charge"],
        ["ground_stomp", "leap"]
    ]
}
```

### Build Type Requirements
```json
{
    "pve": {
        "required_categories": {
            "aoe": 2,
            "control": 1
        }
    },
    "pvp": {
        "required_categories": {
            "mobility": 1,
            "control": 2
        }
    }
}
```

### Focus Requirements
```json
{
    "dps": {
        "required_categories": {
            "damage": 3
        },
        "min_stats": {
            "critical_hit": 30,
            "attack_speed": 20
        }
    },
    "survival": {
        "required_categories": {
            "defense": 2,
            "healing": 1
        },
        "min_stats": {
            "life": 50000,
            "armor": 5000
        }
    }
}
```

## Validation Process

1. Class Validation:
   - Verify character class exists
   - Check weapon type compatibility
   - Validate skill category requirements
   - Ensure no incompatible skill combinations

2. Build Type Validation:
   - Check required skill categories for build type
   - Validate minimum category counts
   - Verify build type specific constraints

3. Focus Validation:
   - Verify required categories for focus
   - Check minimum stat requirements
   - Validate focus-specific constraints

## Future Improvements

1. Planned Enhancements:
   - Add support for hybrid builds
   - Implement dynamic stat requirements
   - Add build composition validation
   - Support for legendary gem requirements

2. Known Limitations:
   - Currently only supports single class builds
   - Static stat requirements
   - Limited build type combinations
