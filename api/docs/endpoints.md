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
  - Response:
    - `id`: Gist ID
    - `html_url`: URL to view the gist
    - `files`: Map of filenames to file objects

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
**Base path:** `/game/builds`

### Build Management
- `GET /game/builds/{gist_id}` - Get a previously saved build
  - Requires: Bearer token
  - Response: BuildResponse object containing:
    - `name`: Build name
    - `type`: Build type (raid, pve, pvp, farm)
    - `focus`: Build focus (dps, survival, buff)
    - `build`: BuildRecommendation object
      - `gems`: List of recommended gems
      - `skills`: List of recommended skills with essences
      - `equipment`: List of recommended equipment pieces
      - `synergies`: List of synergy descriptions
    - `stats`: BuildStats object
      - `dps`: DPS rating
      - `survival`: Survival rating
      - `utility`: Utility rating
    - `gear`: Map of gear slots to equipment details
    - `sets`: Map of set names to set details
    - `skills`: Map of skill slots to skill details
    - `paragon`: Map of paragon tree details
    - `gist_url`: URL to view the build gist
    - `raw_url`: URL to get the raw JSON

- `PUT /game/builds/{gist_id}` - Update a previously saved build
  - Requires: Bearer token
  - Body: BuildResponse object (same structure as GET response)
  - Response: Updated BuildResponse object

- `POST /game/builds/analyze` - Analyze a specific build configuration
  - Body: BuildRecommendation object
  - Response: BuildResponse object with analysis results

- `GET /game/builds/generate` - Generate a build based on criteria
  - Query Parameters:
    - `build_type`: Type of build to generate (raid, pve, pvp, farm)
    - `focus`: Primary focus of the build (dps, survival, buff)
    - `save`: Whether to save the build to a gist (default: false)
    - `use_inventory`: Whether to consider user's inventory (default: false)
  - Response: BuildResponse object

## Game Data Endpoints
**Base path:** `/game`

### Equipment Sets
- `GET /game/equipment/sets` - List available equipment sets
  - Query Parameters:
    - `pieces`: Filter by number of pieces (2, 4, or 6)
    - `page`: Page number (default: 1)
    - `per_page`: Items per page (default: 20, max: 100)
  - Response:
    - List of equipment sets with their bonuses and requirements

### Gems
- `GET /game/gems` - List all gems
  - Query Parameters:
    - `skill_type`: Filter by skill type (e.g., movement, attack)
    - `stars`: Filter by star rating (1, 2, or 5)
  - Response:
    - List of gems with their effects and requirements

- `GET /game/gems/{name}` - Get a specific gem by name
  - Response:
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
  - Response:
    - List of skills with their effects and requirements

### Essences
- `GET /game/essences/{character_class}` - List available essences for a character class
  - Query Parameters:
    - `skill`: Filter by modified skill
    - `slot`: Filter by gear slot
  - Response:
    - List of essences with their effects and requirements

## Documentation
- `GET /api/v1/docs` - Swagger UI API documentation
- `GET /api/v1/redoc` - ReDoc API documentation
- `GET /api/v1/openapi.json` - OpenAPI specification

## Notes
- All endpoints requiring authentication expect a Bearer token in the Authorization header
- Pagination is available on list endpoints with `page` and `per_page` parameters
- API responses are cached where appropriate for better performance
- All responses are in JSON format
