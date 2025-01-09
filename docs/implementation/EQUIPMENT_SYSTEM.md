# Equipment System Implementation Plan

## Overview

Implementation plan for refactoring and building the equipment system, following test-driven development and the test pyramid approach.

## Important Guidelines

### Data Usage

- Use ONLY real game data from `/data/indexed/` for all testing
- Never create fictional or mock data
- Available data sources:
  - `/data/indexed/equipment/sets.json` - Set definitions
  - `/data/indexed/classes/{class_name}/essences.json` - Class-specific essences
  - `/data/indexed/classes/{class_name}/base_skills.json` - Base skills
  - `/data/indexed/classes/{class_name}/constraints.json` - Class constraints
  - `/docs/game/player/sets.json` - Example set data structure
- If required data is missing:
  1. Document the missing data
  2. Request the data from project maintainers
  3. Do not proceed with implementation until data is provided

### Data Testing Strategy

- Use real game data for all test cases
- Test against actual game mechanics and rules
- Verify behavior against documented game systems
- If edge cases are not covered by available data:
  1. Document the missing test cases
  2. Request additional test data
  3. Do not create fictional test data

## System Components

### Data Models

```text
/api/models/game_data/schemas/
├── gear.py           # Primary gear with essence slots
├── sets.py           # Set items and bonuses
├── essences.py       # Class-specific essence modifications
└── constraints.py    # Class-specific constraints
```

### API Endpoints

```text
/api/routes/game/
├── gear.py
│   ├── GET /game/gear                    # List available gear
│   └── GET /game/gear/{class}/essences   # List class-specific essences
└── sets.py
    ├── GET /game/sets                    # List all sets
    ├── GET /game/sets/{set_name}         # Get specific set details
    └── GET /game/sets/bonuses            # Get active set bonuses
```

## Implementation Phases

### Phase 1: Schema Updates

#### 1.1 Primary Gear Schema

**Tests**: `/tests/unit/models/game_data/test_gear_schema.py`

- GearSlot enum validation
- GearItem model validation
- Gear attribute constraints
- Essence slot validation

**Implementation**:

- GearSlot enum (HEAD, CHEST, etc.)
- GearItem model
- Attribute constraints
- Essence slot definitions

#### 1.2 Set Items Schema

**Tests**: `/tests/unit/models/game_data/test_sets_schema.py`

- SetSlot enum validation
- SetItem model validation
- SetBonus model validation
- Set bonus threshold validation

**Implementation**:

- SetSlot enum (NECK, WAIST, etc.)
- SetItem model
- SetBonus model
- Bonus threshold validation

#### 1.3 Essence Schema

**Tests**: `/tests/unit/models/game_data/test_essences_schema.py`

- EssenceEffect model validation
- Skill modification validation
- Class-specific constraint validation

**Implementation**:

- EssenceEffect model
- SkillModification model
- ClassConstraints integration

### Phase 2: Data Management

#### 2.1 Game Data Manager

**Tests**: `/tests/unit/models/game_data/test_data_manager.py`

- Gear data loading
- Set data loading
- Essence data loading
- Data validation

**Implementation**:

- Gear data loading
- Set data loading
- Essence data loading
- Data validation logic

#### 2.2 Data Access Layer

**Tests**: `/tests/unit/models/game_data/test_data_access.py`

- Gear queries
- Set queries
- Essence queries

**Implementation**:

- GearDataAccess class
- SetDataAccess class
- EssenceDataAccess class

### Phase 3: API Implementation

#### 3.1 Gear API

**Tests**: `/tests/api/game/test_gear_routes.py`

- GET /game/gear endpoint
- GET /game/gear/{class}/essences endpoint
- Error handling

**Implementation**:

- List available gear
- Get class-specific essences
- Error handling middleware

#### 3.2 Sets API

**Tests**: `/tests/api/game/test_sets_routes.py`

- GET /game/sets endpoint
- GET /game/sets/{set_name} endpoint
- GET /game/sets/bonuses endpoint
- Pagination tests
- Filter tests

**Implementation**:

- List all sets
- Get specific set details
- Calculate set bonuses
- Pagination
- Filtering

### Phase 4: Business Logic

#### 4.1 Set Bonus Calculator

**Tests**: `/tests/unit/services/test_set_calculator.py`

- Bonus threshold calculation
- Multiple set combinations
- Invalid combinations

**Implementation**:

- SetBonusCalculator class
- Threshold validation
- Combination rules

#### 4.2 Essence Modifier

**Tests**: `/tests/unit/services/test_essence_modifier.py`

- Skill modifications
- Stacking rules
- Class restrictions

**Implementation**:

- EssenceModifier class
- Skill modification logic
- Validation rules

### Phase 5: End-to-End Testing

#### 5.1 Equipment System E2E

**Tests**: `/tests/e2e/test_equipment_system.py`

- Complete gear loadout
- Set system verification
- Class integration

## Test Coverage Goals

- Unit Tests: 70% coverage
- Integration Tests: 20% coverage
- E2E Tests: 10% coverage

## Branch Strategy

```text
main
└── feat/equipment-system
    ├── feat/equipment-schemas
    ├── feat/data-management
    ├── feat/gear-api
    ├── feat/sets-api
    └── feat/business-logic
```

## Validation Requirements

After each phase:

1. Full test suite must pass
2. Documentation must be updated
3. Type hints must be complete
4. Game data validation must pass
5. Error handling must be comprehensive

## Performance Considerations

- Implement caching for set calculations
- Optimize data loading patterns
- Add query optimization
- Monitor response times
- Profile memory usage

## Documentation Updates

- API documentation
- Schema documentation
- Test coverage reports
- README updates
- OpenAPI specification updates

## Dependencies

- FastAPI
- Pydantic
- pytest
- mypy
- black
- ruff
