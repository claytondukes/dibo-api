# API Endpoints Documentation

## Base URL
All endpoints are prefixed with `/api/v1`

## Authentication Endpoints
**Base path:** `/auth`

### OAuth Authentication
- `GET /auth/login` - Get GitHub login URL
  - Response:
    - `auth_url`: GitHub authorization URL
    - `state`: CSRF state token for validation
- `GET /auth/github` - Handle GitHub OAuth callback
  - Query Parameters:
    - `code`: GitHub OAuth code
    - `state`: CSRF state token
  - Response:
    - `access_token`: GitHub access token
    - `token_type`: Token type (always "bearer")
    - `scope`: Granted scopes

### Gist Management
- `GET /auth/gists` - Get user's gists
  - Requires: Bearer token
  - Response: List of user's GitHub gists
- `POST /auth/gists` - Create a new gist
  - Requires: Bearer token
  - Body:
    - `filename`: Name of the file
    - `content`: Content of the gist
    - `description`: Optional description
- `GET /auth/inventory` - Get user's DIBO inventory from gists
- `PUT /auth/gists/{gist_id}` - Update a gist
  - Requires: Bearer token
  - Body:
    - `filename`: Name of the file
    - `content`: Content of the gist
    - `description`: Optional description

### DIBO Inventory
- `GET /auth/inventory` - Get user's DIBO inventory from gists
  - Requires: Bearer token
  - Response:
    - `profile`: User profile data
      - `version`: Schema version (1.0)
      - `name`: Character name
      - `class`: Character class
    - `gems`: Gem collection data
      - `version`: Schema version (1.0)
      - `gems`: List of owned gems
    - `sets`: Equipment set data
      - `version`: Schema version (1.0)
      - `sets`: List of owned sets
    - `builds`: Build data
      - `version`: Schema version (1.0)
      - `builds`: List of saved builds

## Build Endpoints
**Base path:** `/builds`

### Build Management
- `GET /builds/{gist_id}` - Get a previously saved build
- `PUT /builds/{gist_id}` - Update a previously saved build
- `POST /builds/analyze` - Analyze a specific build configuration
- `GET /builds/generate` - Generate a build based on criteria
  - Query Parameters:
    - `build_type`: Type of build to generate
    - `focus`: Primary focus of the build
    - `save`: Whether to save the build to a gist (default: false)
    - `use_inventory`: Whether to consider user's inventory (default: false)

## Game Data Endpoints
**Base path:** `/game`

### Equipment Sets
- `GET /game/equipment/sets` - List available equipment sets
  - Query Parameters:
    - `pieces`: Filter by number of pieces (2, 4, or 6)
    - `page`: Page number (default: 1)
    - `per_page`: Items per page (default: 20, max: 100)

### Gems
- `GET /game/gems` - List all gems
  - Query Parameters:
    - `skill_type`: Filter by skill type (e.g., movement, attack)
    - `stars`: Filter by star rating (1, 2, or 5)
- `GET /game/gems/{name}` - Get a specific gem by name
  - Response includes:
    - `name`: Name of the gem
    - `stars`: Star rating (1, 2, or 5)
    - `base_effect`: Base effect at rank 1
    - `rank_10_effect`: Effect at rank 10 (optional)
    - `owned_rank`: Current rank if owned (optional)
    - `quality`: Quality rating for 5-star gems (optional)

### Skills
- `GET /game/skills/{character_class}` - List available skills for a character class
  - Query Parameters:
    - `category`: Filter by category
    - `page`: Page number (default: 1)
    - `per_page`: Items per page (default: 20, max: 100)

### Stats
- `GET /game/stats` - List stat relationships
  - Query Parameters:
    - `stat`: Specific stat to retrieve

## Documentation
- `GET /api/v1/docs` - Swagger UI API documentation
- `GET /api/v1/redoc` - ReDoc API documentation
- `GET /api/v1/openapi.json` - OpenAPI specification

## Notes
- All endpoints requiring authentication expect a Bearer token in the Authorization header
- Pagination is available on list endpoints with `page` and `per_page` parameters
- API responses are cached where appropriate for better performance
- All responses are in JSON format
