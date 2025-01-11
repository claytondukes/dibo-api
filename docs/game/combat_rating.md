# Combat Rating System

## Overview

Combat Rating (CR) is a critical metric in Diablo Immortal that determines a character's effectiveness, particularly in endgame content like Challenge Rifts and raids. It's a numerical value that represents overall power level, derived from various sources including gear, gems, and resonance.

## Importance

- Primary factor for success in Challenge Rifts
- Critical for raid participation and effectiveness
- More important than skill combinations or set bonuses in certain content
- Used for content gating and difficulty scaling

## Sources of Combat Rating

### 1. Legendary Gems

Combat Rating contribution varies by gem type and rank:

#### 1-star Legendary Gems

| Rank | CR  |
|------|-----|
| 1    | 8   |
| 2    | 12  |
| 3    | 16  |
| 4    | 20  |
| 5    | 24  |
| 6    | 28  |
| 7    | 32  |
| 8    | 36  |
| 9    | 40  |
| 10   | 44  |

#### 2-star Legendary Gems

| Rank | CR  |
|------|-----|
| 1    | 12  |
| 2    | 18  |
| 3    | 24  |
| 4    | 30  |
| 5    | 36  |
| 6    | 42  |
| 7    | 48  |
| 8    | 54  |
| 9    | 60  |
| 10   | 66  |

#### 5-star Legendary Gems

Combat Rating varies by quality (2/5 to 5/5):

| Rank | 2/5  | 3/5  | 4/5  | 5/5  |
|------|------|------|------|------|
| 1    | 12   | 18   | 22   | 24   |
| 2    | 24   | 36   | 44   | 48   |
| 3    | 44   | 56   | 66   | 72   |
| 4    | 66   | 78   | 88   | 96   |
| 5    | 88   | 100  | 110  | 120  |
| 6    | 110  | 122  | 132  | 144  |
| 7    | 132  | 144  | 154  | 168  |
| 8    | 154  | 166  | 176  | 192  |
| 9    | 176  | 188  | 198  | 216  |
| 10   | 198  | 210  | 220  | 240  |

### 2. Equipment

- Base item level
- Attribute values
- Quality/rank of items
- Socket bonuses

### 3. Helliquary

- Boss kills increase CR
- Scoria upgrades
- Bonus attributes

### 4. Other Sources

- Paragon levels
- Challenge Rift completions
- Horadric Vessel upgrades

## Impact on Gameplay

### Challenge Rifts

- CR is the primary determinant of success
- Higher CR allows access to higher rift levels
- CR differences create damage penalties/bonuses:
  - Below target CR: Significant damage penalty
  - Above target CR: Damage bonus

### Raids

- Minimum CR requirements for participation
- Higher CR increases individual effectiveness
- Affects damage dealt and taken
- Required for specific difficulties:
  - Normal: 500 CR
  - Hell 1: 1000 CR
  - Higher difficulties scale up

### PvE Content

- Affects damage dealt and taken
- Influences difficulty scaling
- Required for Hell difficulty progression
- Impacts farming efficiency

## Implementation Details

### CR Calculation

```python
def calculate_total_cr(build: Build) -> int:
    """Calculate total Combat Rating for a build."""
    cr = 0
    
    # Add gem CR
    for gem in build.gems:
        if gem.stars == 5:
            cr += CR_TABLE_5STAR[gem.quality][gem.rank]
        else:
            cr += CR_TABLE[gem.stars][gem.rank]
    
    # Add equipment CR
    cr += sum(item.combat_rating for item in build.equipment)
    
    # Add other sources
    cr += build.helliquary_cr
    cr += build.paragon_cr
    cr += build.vessel_cr
    
    return cr
```

### Content Requirements

```python
CR_REQUIREMENTS = {
    "challenge_rift": {
        "tier_70": 1000,
        "tier_100": 2000,
        # Add more tiers
    },
    "raid": {
        "normal": 500,
        "hell_1": 1000,
        "hell_2": 1500,
        # Add more difficulties
    },
    "hell_difficulty": {
        "hell_1": 1000,
        "hell_2": 1500,
        "hell_3": 2000,
        # Add more levels
    }
}
```

## Best Practices

### 1. CR Optimization

- Prioritize CR for progression content
- Balance CR with other stats for farming
- Consider CR requirements when planning upgrades

### 2. Content Selection

- Match content to current CR level
- Avoid excessive CR penalties
- Progress through difficulties appropriately

### 3. Build Planning

- Set CR targets for specific content
- Plan gem upgrades for CR progression
- Balance CR with build synergies

## CR Breakpoints

Important CR thresholds for various content types:

- Challenge Rift progression
- Raid participation
- Hell difficulty levels
