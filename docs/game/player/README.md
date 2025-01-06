# Diablo Immortal Player Inventory System

This directory contains the JSON schema for tracking your Diablo Immortal inventory, builds, and equipped items. These files are designed to be stored in your GitHub Gists for easy access and updating.

## Type Definitions

```python
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class PlayerProfile(BaseModel):
    """Player profile information and equipped items."""
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    battle_net_id: str
    character_class: str
    paragon_level: int
    primary_gear: Dict[str, GearItem]
    set_items: Dict[str, SetItem]

class GearItem(BaseModel):
    """Primary gear item with essence and gem slots."""
    slot: str
    essence: Optional[str] = None
    legendary_gem: Optional[str] = None
    attributes: Dict[str, int]

class SetItem(BaseModel):
    """Set item with normal gem sockets."""
    slot: str
    set_name: str
    attributes: Dict[str, int]
    socket_count: int = Field(ge=2, le=3)
    combat_rating: int

class GemInventory(BaseModel):
    """Collection of owned legendary gems."""
    version: str
    gems: Dict[str, List[GemInstance]]

class GemInstance(BaseModel):
    """Individual gem instance with rank and quality."""
    rank: int = Field(ge=1, le=10)
    quality: Optional[int] = Field(None, ge=2, le=5)
    is_auxiliary: bool = False

class SetInventory(BaseModel):
    """Collection of owned set items."""
    version: str
    sets: Dict[str, List[SetItem]]
```

## Files

### `profile.json`
Contains your player information and currently equipped items:
```python
PlayerProfile(
    version="1.0.0",
    battle_net_id="example#1234",
    character_class="barbarian",
    paragon_level=600,
    primary_gear={
        "head": GearItem(...),
        "shoulders": GearItem(...),
        # ... other gear slots
    },
    set_items={
        "neck": SetItem(...),
        "waist": SetItem(...),
        # ... other set slots
    }
)
```

### `gems.json`
Tracks all legendary gems you own:
```python
GemInventory(
    version="1.0.0",
    gems={
        "Blood-Soaked Jade": [
            GemInstance(rank=10, quality=5),
            GemInstance(rank=1, is_auxiliary=True)
        ],
        # ... other gems
    }
)
```

### `sets.json`
Lists all set items in your inventory:
```python
SetInventory(
    version="1.0.0",
    sets={
        "Grace of the Flagellant": [
            SetItem(
                slot="neck",
                attributes={"strength": 642, "fortitude": 641},
                socket_count=3,
                combat_rating=2026
            ),
            # ... other set items
        ]
    }
)
```

### `builds.json`
Stores your saved builds with references to inventory items.

## Setting Up Your Inventory

1. Create a new GitHub Gist at https://gist.github.com/
2. Create the required JSON files:
   - `profile.json`
   - `gems.json`
   - `sets.json`
   - `builds.json`
3. Copy the contents of each file from this directory
4. Update with your actual inventory data

## Data Validation

All files are validated against Pydantic models to ensure:
- Correct data types
- Valid value ranges
- Required fields presence
- Proper version formatting
- Consistent structure

## File Format Guidelines

1. Files must be valid JSON
2. Follow the exact schema defined in type definitions
3. Use semantic versioning (X.Y.Z)
4. Keep last_updated field current
5. Maintain referential integrity between files

## Error Handling

Common validation errors:
- Invalid version format
- Missing required fields
- Out of range values
- Invalid slot names
- Incorrect attribute types

## Security Notes

- Do not include sensitive account information
- Use environment variables for API keys
- Follow secure gist creation practices
- Implement proper authentication
