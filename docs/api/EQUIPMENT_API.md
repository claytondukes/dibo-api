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
  "slots": ["head", "chest", "shoulders", "legs", "main_hand", "off_hand"]
}
```

#### GET /game/gear

List all available primary gear items.

**Query Parameters**:

- `class` (optional): Filter by class name
- `slot` (optional): Filter by gear slot (head, chest, shoulders, legs, main_hand, off_hand)
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
      "essence": {
        "id": "string",
        "name": "string",
        "modifies_skill": "string",
        "effect": "string",
        "effect_type": "string",
        "tags": ["string"]
      }
    }
  ],
  "total": "number",
  "page": "number",
  "per_page": "number"
}
```

### Essences

#### GET /game/essences

List all available essences.

**Query Parameters**:

- `class` (required): Filter by class name
- `slot` (optional): Filter by gear slot
- `skill` (optional): Filter by modified skill
- `effect_type` (optional): Filter by effect type (damage, utility, defense)
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)

**Response**:

```json
{
  "metadata": {
    "version": "1.0",
    "last_updated": "2025-01-17T13:23:54-05:00"
  },
  "essences": [
    {
      "id": "string",
      "essence_name": "string",
      "slot": "string",
      "modifies_skill": "string",
      "effect": "string",
      "effect_type": "string",
      "tags": ["string"]
    }
  ],
  "total": "number",
  "page": "number",
  "per_page": "number"
}
```

#### GET /game/essences/{class}/{slot}

Get all essences for a specific class and slot.

**Path Parameters**:

- `class` (required): Class name
- `slot` (required): Gear slot

**Response**:

```json
{
  "metadata": {
    "version": "1.0",
    "last_updated": "2025-01-17T13:23:54-05:00",
    "slot": "string",
    "essence_count": "number"
  },
  "essences": {
    "essence_id": {
      "essence_name": "string",
      "modifies_skill": "string",
      "effect": "string",
      "effect_type": "string",
      "tags": ["string"]
    }
  }
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
