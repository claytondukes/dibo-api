# Data Service Tests

## Service Tests (`test_service.py`)

### `test_load_indexed_data`
✅ **Status**: Stable
Tests data loading functionality:
1. Load synergies data
2. Load stats data
3. Load constraints
4. Verify data structure

### `test_get_class_data`
✅ **Status**: Stable
Tests class data retrieval:
1. Load class-specific data
2. Verify skills data
3. Validate essence data
4. Check constraints

### `test_get_equipment_data`
✅ **Status**: Stable
Tests equipment data retrieval:
1. Load equipment sets
2. Verify set bonuses
3. Validate item stats

## Route Tests (`test_routes.py`)

### `test_get_indexed_data`
✅ **Status**: Stable
Tests data retrieval endpoints:
1. Get synergies
2. Get stats
3. Get constraints
4. Verify response format

### `test_get_class_data`
✅ **Status**: Stable
Tests class-specific endpoints:
1. Get class skills
2. Get class essences
3. Validate response structure

### `test_get_equipment_data`
✅ **Status**: Stable
Tests equipment endpoints:
1. Get equipment sets
2. Verify response format
3. Validate set data

## Test Dependencies

### Fixtures
- `client`: FastAPI test client
- `test_settings`: Test configuration
- `mock_data_dir`: Test data directory

### Test Data Structure
```
data/
├── indexed/
│   ├── synergies.json
│   ├── stats.json
│   └── constraints.json
├── classes/
│   └── barbarian/
│       ├── base_skills.json
│       └── essences.json
└── equipment/
    └── sets.json
```

### Environment Variables
Required environment variables set in `conftest.py`:
- `DATA_DIR`: Path to test data directory
- `PROJECT_ROOT`: Project root path
