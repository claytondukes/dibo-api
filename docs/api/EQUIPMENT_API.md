# Equipment System API

## Overview

API endpoints for managing equipment, sets, and their interactions in the DIBO API system.

## Endpoints

### Primary Gear

#### GET /game/gear/slots

List available gear slots.

**Query Parameters**:

- `type` (optional): Filter by gear type ("primary" or "set")

**Response**:

```json
{
  "slots": ["head", "chest", "shoulders", "legs", "main_hand_1", "off_hand_1", "main_hand_2", "off_hand_2"]
}
```

#### GET /game/gear

List all available primary gear items.

**Query Parameters**:

- `class` (optional): Filter by class name
- `slot` (optional): Filter by gear slot (head, chest, shoulders, legs, main_hand_1, off_hand_1, main_hand_2, off_hand_2)
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)

**Response**:

```json
{
  "items": [
    {
      "id": "string",
      "name": "string",
      "slot": "string",
      "level": "number",
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

- `slot` (optional): Filter by gear slot (head, chest, shoulders, legs, main_hand_1, off_hand_1, main_hand_2, off_hand_2)
- `skill` (optional): Filter by modified skill
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)

**Response**:

```json
{
  "essences": [
    {
      "id": "string",
      "name": "string",
      "gear_slot": "string",
      "modifies_skill": "string",
      "effect": {
        "type": "string",
        "value": "number",
        "description": "string"
      },
      "tags": ["string"]
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
      "name": "string",
      "level": "number"
    }
  ]
}
```

## Error Responses

All endpoints may return the following errors:

### 400 Bad Request

```json
{
  "detail": {
    "msg": "string",
    "type": "validation_error",
    "loc": ["string"],
    "input": {}
  }
}
```

### 404 Not Found

```json
{
  "detail": {
    "msg": "Resource not found",
    "type": "not_found_error",
    "resource": "string"
  }
}
```

### 500 Internal Server Error

```json
{
  "detail": {
    "msg": "Internal server error",
    "type": "internal_error"
  }
}
