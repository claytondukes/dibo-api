# Equipment System API

## Overview
API endpoints for managing equipment, sets, and their interactions in the DIBO API system.

## Endpoints

### Primary Gear

#### GET /game/gear
List all available primary gear items.

**Query Parameters**:
- `class` (optional): Filter by class name
- `slot` (optional): Filter by gear slot
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)

**Response**:
```json
{
  "items": [
    {
      "name": "string",
      "slot": "string",
      "attributes": {
        "strength": "number",
        "fortitude": "number",
        "willpower": "number"
      },
      "essence_slot": {
        "available": "boolean",
        "current_essence": "string | null"
      }
    }
  ],
  "page": "number",
  "per_page": "number",
  "total": "number"
}
```

#### GET /game/gear/{class}/essences
List available essences for a specific class.

**Path Parameters**:
- `class`: Class name (e.g., "barbarian")

**Query Parameters**:
- `slot` (optional): Filter by gear slot
- `skill` (optional): Filter by modified skill
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)

**Response**:
```json
{
  "essences": [
    {
      "name": "string",
      "gear_slot": "string",
      "modifies_skill": "string",
      "effect": "string",
      "effect_type": "string",
      "effect_tags": ["string"]
    }
  ],
  "page": "number",
  "per_page": "number",
  "total": "number"
}
```

### Set Items

#### GET /game/sets
List all available equipment sets.

**Query Parameters**:
- `pieces` (optional): Filter by number of pieces (2, 4, or 6)
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)

**Response**:
```json
{
  "sets": [
    {
      "name": "string",
      "pieces": "number",
      "description": "string",
      "bonuses": {
        "2": "string",
        "4": "string",
        "6": "string"
      },
      "use_case": "string"
    }
  ],
  "page": "number",
  "per_page": "number",
  "total": "number"
}
```

#### GET /game/sets/{set_name}
Get detailed information about a specific set.

**Path Parameters**:
- `set_name`: Name of the set

**Response**:
```json
{
  "name": "string",
  "pieces": "number",
  "description": "string",
  "bonuses": {
    "2": "string",
    "4": "string",
    "6": "string"
  },
  "use_case": "string",
  "items": [
    {
      "slot": "string",
      "attributes": {
        "strength": "number",
        "fortitude": "number",
        "willpower": "number"
      }
    }
  ]
}
```

#### GET /game/sets/bonuses
Calculate active set bonuses for equipped items.

**Query Parameters**:
- `equipped_sets`: List of equipped set pieces (format: "set_name:count")

**Response**:
```json
{
  "active_bonuses": [
    {
      "set_name": "string",
      "pieces_equipped": "number",
      "active_thresholds": ["number"],
      "active_bonuses": {
        "2": "string",
        "4": "string",
        "6": "string"
      }
    }
  ],
  "total_sets": "number"
}
```

## Error Responses

All endpoints may return the following errors:

### 400 Bad Request
```json
{
  "error": "string",
  "message": "string",
  "details": {}
}
```

### 404 Not Found
```json
{
  "error": "NotFound",
  "message": "Resource not found",
  "details": {
    "resource_type": "string",
    "resource_id": "string"
  }
}
```

### 500 Internal Server Error
```json
{
  "error": "InternalError",
  "message": "An internal error occurred",
  "request_id": "string"
}
```

## Rate Limiting

All endpoints are subject to rate limiting:
- 100 requests per minute per authenticated user
- 20 requests per minute per IP for unauthenticated requests
