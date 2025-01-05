# Authentication Tests

## OAuth Flow Tests (`test_oauth_flow.py`)

### `test_complete_oauth_flow`
✅ **Status**: Stable
Tests the complete OAuth authentication flow with GitHub:
1. Get login URL and state
2. Mock GitHub token exchange
3. Mock GitHub user info request
4. Verify token response
5. Test protected endpoint access

### `test_github_token_exchange_failure`
✅ **Status**: Stable
Tests error handling when GitHub token exchange fails:
1. Get valid state token
2. Mock failed token exchange
3. Verify error response

### `test_github_user_info_failure`
✅ **Status**: Stable
Tests error handling when GitHub user info fetch fails:
1. Mock successful token exchange
2. Mock failed user info request
3. Verify error response

## Inventory Tests (`test_inventory.py`)

### `test_get_inventory_success`
✅ **Status**: Stable
Tests successful inventory retrieval:
1. Mock GitHub Gist response
2. Verify inventory structure
3. Validate gem data

### `test_get_inventory_unauthorized`
✅ **Status**: Stable
Tests unauthorized access handling:
1. Request without token
2. Verify 401 response

### `test_get_inventory_empty`
✅ **Status**: Stable
Tests handling of empty inventory:
1. Mock empty Gist response
2. Verify empty inventory structure

### `test_get_inventory_github_error`
✅ **Status**: Stable
Tests GitHub API error handling:
1. Mock GitHub API error
2. Verify error response

## Route Tests (`test_routes.py`)

### `test_github_login`
✅ **Status**: Stable
Tests GitHub login endpoint:
1. Verify response structure
2. Validate auth URL
3. Check state parameter

### `test_github_callback`
✅ **Status**: Stable
Tests GitHub callback endpoint:
1. Verify token exchange
2. Validate response format
3. Check error handling

## Test Dependencies

### Fixtures
- `client`: FastAPI test client
- `test_settings`: Test configuration
- `mock_github_user_response`: Mock user data
- `mock_github_token_response`: Mock token data

### Environment Variables
Required environment variables set in `conftest.py`:
- `DEV_GITHUB_CLIENT_ID`
- `DEV_GITHUB_CLIENT_SECRET`
- `DEV_GITHUB_CALLBACK_URL`
