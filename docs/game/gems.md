# Gem System Guide

## Overview

The gem system provides character customization through resonance, effects, and stat boosts.

## Core Systems

### Resonance System

Resonance is a critical multiplier that scales base attributes:

#### Base Resonance Values by Rank and Star Rating

| Rank | 1★   | 2★   | 2/5★ | 3/5★ | 4/5★ | 5/5★ |
|------|------|------|------|------|------|------|
| 1    | 15   | 30   | 30   | 60   | 90   | 100  |
| 2    | 30   | 60   | 110  | 140  | 180  | 200  |
| 3    | 45   | 90   | 190  | 230  | 270  | 300  |
| 4    | 60   | 120  | 280  | 320  | 360  | 400  |
| 5    | 75   | 150  | 370  | 410  | 450  | 500  |
| 6    | 90   | 180  | 460  | 500  | 540  | 600  |
| 7    | 105  | 210  | 550  | 590  | 630  | 700  |
| 8    | 120  | 240  | 640  | 680  | 720  | 800  |
| 9    | 135  | 270  | 730  | 770  | 810  | 900  |
| 10   | 150  | 300  | 820  | 860  | 900  | 1000 |

Key Features:

- All gems provide resonance based on rank
- 5★ gems have quality ratings (2-5) affecting resonance
- Crucial for high-end raids and Challenge Rift progression
- Affects PvP matchmaking brackets

### Auxiliary System

The aux system allows effect substitution while preserving resonance:

- Primary gem provides:
  - Full resonance based on rank/quality
  - Combat Rating
  - Magic Find
  - All numeric stat bonuses

- Auxiliary gem provides:
  - Only its Rank 1 effect
  - Must match primary gem's star rating
  - No additional resonance/stats
  - Cannot duplicate any equipped gem

## Gem Structure

### Star Rating

Gems come in three ratings with different resonance scaling:

- 1-star Legendary Gem
  - Base resonance: 15-150 (Rank 1-10)
  - Magic Find: +5% at Rank 5
  - Combat Rating: 8-44 (Rank 1-10)

- 2-star Legendary Gem
  - Base resonance: 30-300 (Rank 1-10)
  - Magic Find: +10% at Rank 5
  - Combat Rating: 12-66 (Rank 1-10)

- 5-star Legendary Gem
  - Base resonance varies by quality:
    - 2/5: 30-820 (Rank 1-10)
    - 3/5: 60-860 (Rank 1-10)
    - 4/5: 90-900 (Rank 1-10)
    - 5/5: 100-1000 (Rank 1-10)
  - Magic Find: +15% at Rank 5
  - Combat Rating varies by quality:
    - 2/5: 12-198 (Rank 1-10)
    - 3/5: 18-210 (Rank 1-10)
    - 4/5: 22-220 (Rank 1-10)
    - 5/5: 24-240 (Rank 1-10)

### Gem Components

Each gem consists of:

- Name
- Star rating and quality (for 5★)
- Base effect (Rank 1)
- Maximum effect (Rank 10)
- Magic Find value
- Resonance value
- Combat Rating
- Rank-specific effects and stats

### Effect Types

Gems can have multiple effect types:

- stat_effect: Direct stat modifications (e.g., damage reduction)
- proc_effect: Triggered effects (e.g., on critical hit)
- generic_effect: General gameplay effects
- control_effect: Crowd control effects (stun, slow, etc.)

### Conditions

Effects can be conditional based on:

- Movement state (e.g., while moving)
- Health thresholds (e.g., below 50% life)
- Combat triggers (e.g., on critical hit)
- Skill usage (e.g., after using ultimate)
- Status effects (e.g., while stunned)

## Build Generation

The DiBO API uses an intelligent system to dynamically generate optimal gem builds based on:

### Core Factors

- Player class and level
- Content type (PvE/PvP)
- Team composition
- Enemy types and mechanics
- Current meta state
- Player playstyle preferences
- Combat Rating requirements

### Dynamic Optimization

Instead of using static templates, the system:

1. Analyzes gem synergies in real-time
2. Considers current game state
3. Adapts to meta changes
4. Accounts for unique player circumstances
5. Optimizes for specific content challenges

### Historical Reference

For reference purposes, example build templates can be found in [Build Templates Reference](../reference/build_templates/README.md).

## Content Impact

### 1. Challenge Rifts

- Resonance directly scales power
- Higher resonance enables higher clear levels
- Critical for leaderboard progression

### 2. Raid Content

- Resonance affects total damage output
- Higher resonance enables harder raids
- Required for specific difficulty tiers

### 3. PvP System

- Affects matchmaking brackets
- Influences total attribute scaling
- Important for competitive play

## Implementation Details

### Data Structure

```python
class Gem(BaseModel):
    """Represents a single gem in the game."""
    
    stars: str               # Star rating (1, 2, or 5)
    quality: Optional[int]   # Quality rating for 5★ gems (2-5)
    name: str               # Gem name
    ranks: Dict[str, GemRank] # Effects per rank
    max_rank: int          # Maximum achievable rank (10)
    magic_find: str        # Magic find value
    max_effect: str        # Maximum effect description
    base_effect: str       # Base effect (rank 1)
    resonance: Dict[str, int] # Resonance per rank/quality
    combat_rating: Dict[str, int] # Combat Rating per rank/quality
```

### Rank Data Coverage

The gem data includes rank information from 1-10 for all gems. Each gem has a complete set of effects and values for every rank:

#### Effect Scaling Patterns

1. Common Scaling Types
   - Linear Damage Scaling: Effects increase by fixed percentage between ranks

     ```text
     Example: Defiant Soul damage scaling
     Rank 1: 64% base damage
     Rank 2: 80% base damage
     Rank 4: 96% base damage
     Rank 6: 128% base damage
     Rank 8: 160% base damage
     Rank 10: 192% base damage
     ```

   - Stepped Stat Bonuses: Additional effects at key ranks

     ```text
     Example: Ca'arsen's Invigoration
     Rank 1: 5% Attack Speed
     Rank 3: +0.5% Primary Attack damage
     Rank 5: Primary Attack damage to 1%
     Rank 7: Primary Attack damage to 1.5%
     Rank 9: Primary Attack damage to 2%
     ```

2. Effect Progression Guidelines
   - Damage effects: Linear scaling between ranks
   - Cooldowns: Major reductions at ranks 3, 6, and 9
   - Proc chances: Increases at ranks 3, 5, 7, and 9
   - Stat bonuses: Small increases at odd ranks
   - Duration bonuses: Usually at ranks 4, 7, and 10

### File Structure

```text
data/indexed/gems/
├── core/                # Individual gem files
│   ├── 1star/          # 1-star gems
│   ├── 2star/          # 2-star gems
│   └── 5star/          # 5-star gems
└── metadata/           # Shared metadata
    ├── conditions.json  # Effect conditions
    ├── effect_details.json  # Effect specifics
    ├── gem_skillmap.json    # Skill associations
    └── stat_boosts/    # Stat boost data
```

### Effect Processing

```python
def process_gem_effects(
    gem: Gem,
    rank: int,
    conditions: Dict[str, Any]
) -> List[Effect]:
    """Process gem effects for given rank and conditions."""
    effects = []
    for effect in gem.ranks[str(rank)].effects:
        if meets_conditions(effect.conditions, conditions):
            effects.append(process_effect(effect))
    return effects
```

## Strategic Considerations

### 1. Progression Focus

- Early Game (All Gems)
  - Focus on ranking up 1★ gems
  - Build resonance foundation
  - Effect-based choices

- Mid Game (Mix of Stars)
  - Balance 1★ and 2★ gems
  - Target key breakpoints
  - Optimize resonance/effect ratio

- End Game (5★ Focus)
  - Maximize 5★ gem quality
  - Target resonance thresholds
  - Content-specific loadouts

### 2. Content Optimization

- Challenge Rifts
  - Maximize total resonance
  - Focus on damage scaling
  - Clear speed priority

- Raids
  - Meet resonance requirements
  - Boss-specific effects
  - Team contribution focus

- PvP
  - Bracket considerations
  - Effect priority vs resonance
  - Matchmaking impact

### 3. Resource Management

- Upgrade Priority
  - Focus on highest quality gems
  - Balance rank vs quality
  - Consider resonance breakpoints

- Auxiliary Usage
  - Preserve high resonance gems
  - Utilize Rank 1 effects
  - Content-specific swaps

## Testing Guidelines

### 1. Effect Validation

- Verify resonance calculations
- Test scaling formulas
- Validate stat contributions
- Check condition triggers
- Confirm effect stacking

### 2. Data Integrity

- Validate gem file structure
- Check metadata consistency
- Test condition mappings
- Verify effect references

## Last Updated

2025-01-12 23:59:46 EST
