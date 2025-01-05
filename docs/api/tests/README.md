# API Test Documentation

This document provides an overview of the test suite for the DIBO API. Tests are organized by module and marked for stability.

## Test Structure

```
tests/
├── conftest.py           # Global test configuration and fixtures
├── test_auth/           # Authentication tests
├── test_data/           # Data service tests
└── test_builds/         # Build generation tests
```

## Test Categories

### ✅ Stable Tests

These tests are marked with `@pytest.mark.stable` and are considered well-maintained and reliable.

#### Authentication Module (`test_auth/`)
- **OAuth Flow** (`test_oauth_flow.py`)
  - ✅ `test_complete_oauth_flow`: Full OAuth authentication flow
  - ✅ `test_github_token_exchange_failure`: Error handling for token exchange
  - ✅ `test_github_user_info_failure`: Error handling for user info fetch

- **Inventory** (`test_inventory.py`)
  - ✅ `test_get_inventory_success`: Successful inventory retrieval
  - ✅ `test_get_inventory_unauthorized`: Unauthorized access handling
  - ✅ `test_get_inventory_empty`: Empty inventory handling
  - ✅ `test_get_inventory_github_error`: GitHub API error handling

#### Data Service (`test_data/`)
- **Routes** (`test_routes.py`)
  - ✅ `test_get_indexed_data`: Data retrieval endpoints
  - ✅ `test_get_class_data`: Class-specific data endpoints
  - ✅ `test_get_equipment_data`: Equipment data endpoints

- **Service** (`test_service.py`)
  - ✅ `test_load_indexed_data`: Data loading functionality
  - ✅ `test_get_class_data`: Class data retrieval
  - ✅ `test_get_equipment_data`: Equipment data retrieval

### 🚧 In Development Tests

These tests are currently under development or need review.

#### Build Generation (`test_builds/`)
- **Service** (`test_service.py`)
  - 🚧 `test_build_service_isolated`: Isolated build service tests
  - 🚧 `test_skill_selection`: Skill selection logic
  - 🚧 `test_essence_selection`: Essence selection logic

- **Equipment Selection** (`test_equipment_selection.py`)
  - 🚧 `test_equipment_scoring`: Equipment scoring system
  - 🚧 `test_set_bonus_calculation`: Set bonus calculations

- **Routes** (`test_routes.py`)
  - 🚧 `test_generate_build`: Build generation endpoint
  - 🚧 `test_analyze_build`: Build analysis endpoint

## Running Tests

### Run All Tests
```bash
pytest -v
```

### Run Only Stable Tests
```bash
pytest -v -m stable
```

### Run Specific Module Tests
```bash
pytest -v tests/test_auth/  # Run auth tests
pytest -v tests/test_data/  # Run data tests
pytest -v tests/test_builds/  # Run build tests
```

### Run a Single Test
```bash
pytest -v -k test_name  # e.g., pytest -v -k test_complete_oauth_flow
```

## Test Configuration

The test suite uses the following configuration:

- **pytest.ini**: Contains test discovery and execution settings
- **conftest.py**: Provides shared fixtures and configuration
- **Environment Variables**: Set in `conftest.py` for test environment

## Adding New Tests

When adding new tests:

1. Follow the existing module structure
2. Use appropriate fixtures from `conftest.py`
3. Add type hints and docstrings
4. Mark stable tests with `@pytest.mark.stable`
5. Update this documentation

## CI/CD Integration

The test suite is integrated with CI/CD:

- All tests must pass before merging
- Stable tests are given priority in the CI pipeline
- Test coverage reports are generated
- Failed stable tests block deployments
