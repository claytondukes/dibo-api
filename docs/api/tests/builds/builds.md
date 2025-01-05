# Build Generation Tests

## Overview

The build generation test suite verifies the functionality of DIBO's build generation system, which creates optimized character builds based on user preferences, game mechanics, and optional inventory data.

## Implementation Status

```
✅ Complete
- Data loading and validation
- Basic gem selection
- Skill type validation
- Essence scoring
- Build type scoring
- Percentage bonus handling
- Attack speed modifiers
- Weapon skill validation
- Mobility skill validation
- Control/buff validation

🔄 In Progress
- Equipment selection
- Set bonus evaluation
- Stats calculation
- Synergy detection

❌ Not Started
- Equipment optimization
- Set piece combinations
- Final build recommendations
```

## Service Tests (`test_service.py`)

### `test_build_service_isolated`
🚧 **Status**: In Development

Tests build service in isolation:
1. Initialize service with mock data
2. Test data loading and validation
3. Verify service configuration
4. Test request/response models

**Test Cases:**
```python
class BuildRequest:
    build_type: BuildType      # raid, pve, pvp, farm
    focus: BuildFocus         # dps, survival, buff
    character_class: str      # e.g., "barbarian"
    inventory: Optional[Dict] = None
```

### `test_skill_selection`
✅ **Status**: Complete

Tests skill selection logic:
1. Test DPS focus optimization
2. Test survival focus optimization
3. Validate skill combinations
4. Verify skill type requirements:
   - Weapon skill validation
   - Mobility skill requirements
   - Control/buff skill balance
   - Damage skill distribution

### `test_essence_selection`
✅ **Status**: Complete

Tests essence selection logic:
1. Test DPS optimization
2. Test survival optimization
3. Verify essence synergies
4. Test scoring systems:
   - Build type specific scoring
   - Percentage bonus handling
   - Attack speed modifiers

## Equipment Selection Tests (`test_equipment_selection.py`)

### `test_equipment_scoring`
🔄 **Status**: In Progress

Tests equipment scoring system:
1. Test stat prioritization:
   ```python
   def test_calculate_equipment_score():
       # Test stat alignment scoring
       # Test synergy scoring
       # Test set bonus impact
   ```

2. Test score calculations:
   - Base stat contribution
   - Synergy bonuses
   - Set piece interactions

### `test_set_bonus_calculation`
🔄 **Status**: In Progress

Tests set bonus calculations:
1. Test 2-piece bonuses
2. Test 4-piece bonuses
3. Test 6-piece bonuses
4. Validate bonus stacking rules
5. Verify set piece combinations

## Route Tests (`test_routes.py`)

### `test_generate_build`
🚧 **Status**: In Development

Tests build generation endpoint:
1. Test build creation pipeline:
   ```mermaid
   graph TD
       A[Validate Input] --> B[Load Data]
       B --> C[Select Gems]
       C --> D[Select Skills]
       D --> E[Select Equipment]
       E --> F[Calculate Stats]
       F --> G[Find Synergies]
       G --> H[Return Build]
   ```

2. Verify response format
3. Validate build components
4. Test error handling

### `test_analyze_build`
🚧 **Status**: In Development

Tests build analysis endpoint:
1. Test build scoring
2. Test optimization suggestions
3. Verify analysis details

## Test Dependencies

### Fixtures
- `client`: FastAPI test client
- `test_settings`: Test configuration
- `mock_build_service`: Mocked build service
- `mock_data`: Test data fixtures

### Test Data Structure
```
data/
├── builds/
│   ├── templates/          # Build templates
│   └── constraints/        # Build constraints
├── skills/
│   └── barbarian/         # Class-specific skills
└── equipment/
    └── sets/              # Equipment set definitions
```

### Environment Variables
Required environment variables in `conftest.py`:
- `BUILD_DATA_DIR`: Path to build data
- `TEMPLATE_DIR`: Path to build templates
- `DATA_DIR`: Path to game data

## Test Coverage Goals

1. Core Components:
   - Data loading and validation
   - Gem and skill selection
   - Equipment optimization
   - Stats calculation
   - Synergy detection

2. Edge Cases:
   - Invalid input handling
   - Missing inventory data
   - Conflicting requirements
   - Invalid skill combinations

3. Integration Points:
   - Data service integration
   - GitHub Gist integration
   - External API calls
