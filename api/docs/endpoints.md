# API Endpoints Documentation

## Base URL
All endpoints are prefixed with `/api/v1`

## Authentication Endpoints
**Base path:** `/auth`

### OAuth Authentication
- `GET /auth/login` - Get GitHub login URL
- `GET /auth/callback` - Handle GitHub OAuth callback
  - Query Parameters:
    - `code`: GitHub OAuth code
    - `state`: CSRF state token

### Gist Management
- `GET /auth/gists` - Get user's gists
- `POST /auth/gists` - Create a new gist
- `GET /auth/inventory` - Get user's DIBO inventory from gists
- `PUT /auth/gists/{gist_id}` - Update a gist

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
**Base path:** `/data`

### Equipment and Items
- `GET /data/sets` - List available equipment sets
  - Query Parameters:
    - `pieces`: Filter by number of pieces (2, 4, or 6)
    - `page`: Page number (default: 1)
    - `per_page`: Items per page (default: 20, max: 100)

### Gems
- `GET /data/gems` - List available gems
  - Query Parameters:
    - `stars`: Filter by star rating (1, 2, or 5)
    - `category`: Filter by category
    - `page`: Page number (default: 1)
    - `per_page`: Items per page (default: 20, max: 100)

### Skills
- `GET /data/skills/{character_class}` - List available skills for a character class
  - Query Parameters:
    - `category`: Filter by category
    - `page`: Page number (default: 1)
    - `per_page`: Items per page (default: 20, max: 100)

### Stats
- `GET /data/stats` - List stat relationships
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
