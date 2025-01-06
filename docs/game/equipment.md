# Equipment System

## Overview

The equipment system in Diablo Immortal consists of two distinct categories:
1. Primary Gear (with Legendary Gem slots)
2. Set Items

## Primary Gear

Primary gear pieces are the main equipment slots that can:
- Have Legendary Gems socketed into them
- Modify skills through Essence transfer
- Contribute to your character's Combat Rating

### Primary Gear Slots (8 total)

```
Character Right Side:
┌─────────┬──────────┐
│  Head   │  Chest   │
├─────────┼──────────┤
│Shoulders│   Legs   │
├─────────┼──────────┤
│  Main   │   Off    │
│  Hand   │  Hand    │
├─────────┼──────────┤
│  Main   │   Off    │
│  Hand   │  Hand    │
└─────────┴──────────┘
```

1. Head - Helm slot
2. Chest - Torso armor
3. Shoulders - Shoulder armor
4. Legs - Leg armor
5. Main Hand (Slot 1) - Primary weapon set 1
6. Off-Hand (Slot 1) - Off-hand weapon/shield set 1
7. Main Hand (Slot 2) - Primary weapon set 2
8. Off-Hand (Slot 2) - Off-hand weapon/shield set 2

## Set Items

Set items are separate from primary gear and occupy different slots. They provide set bonuses when multiple pieces from the same set are equipped.

### Set Item Slots (8 total)

```
Character Left Side:
┌────────┬─────────┐
│ Neck   │  Waist  │
├────────┼─────────┤
│ Hands  │  Feet   │
├────────┼─────────┤
│ Finger │ Finger  │
│(Ring 1)│(Ring 2) │
├────────┼─────────┤
│ Wrist  │ Wrist   │
│(Bracer)│(Bracer) │
└────────┴─────────┘
```

1. Neck - Necklace slot
2. Waist - Belt slot
3. Hands - Gloves slot
4. Feet - Boot slot
5. Finger (Ring 1)
6. Finger (Ring 2)
7. Wrist (Bracer 1)
8. Wrist (Bracer 2)

### Set Bonuses
Sets provide cumulative bonuses at specific thresholds:
- 2-piece bonus
- 4-piece bonus
- 6-piece bonus

Valid set combinations:
- 6 + 2 pieces
- 4 + 4 pieces
- 4 + 2 + 2 pieces
- 2 + 2 + 2 + 2 pieces

## Implementation Details

### Primary Gear Schema
Primary gear slots are defined in the `GearSlot` enum in `api/models/game_data/schemas/gear.py`:

```python
class GearSlot(str, Enum):
    """Equipment slots for gear items that can have legendary gems and skill modifications."""
    HEAD = "Head"
    CHEST = "Chest"
    SHOULDERS = "Shoulders"
    LEGS = "Legs"
    MAIN_HAND_1 = "Main Hand"  # First weapon slot
    MAIN_HAND_2 = "Main Hand"  # Second weapon slot
    OFF_HAND_1 = "Off-Hand"    # First off-hand slot
    OFF_HAND_2 = "Off-Hand"    # Second off-hand slot
```

### Set Items Schema
Set items and their slots are defined in `api/models/game_data/schemas/sets.py`.

### Data Files
- Primary gear data: `data/indexed/classes/{class_name}/essences.json`
- Set data: `data/indexed/equipment/sets.json`
- Global constraints: `data/indexed/constraints.json`

## Important Notes

1. Only primary gear (Head, Chest, Shoulders, Legs, Weapons) can:
   - Have legendary gems socketed
   - Modify skills through essence transfer

2. Set items (Neck, Waist, Hands, Feet, Rings, Bracers):
   - Cannot have legendary gems
   - Cannot modify skills
   - Provide set bonuses when worn together

3. All equipment (both primary gear and set items):
   - Contribute to Combat Rating
   - Add to overall character power
