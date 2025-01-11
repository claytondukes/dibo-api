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

### Resonance Calculation

```python
def calculate_resonance(
    gem_star: int,
    gem_rank: int,
    gem_quality: Optional[int] = None
) -> int:
    """Calculate gem resonance based on stats."""
    if gem_star == 5 and gem_quality:
        return RESONANCE_TABLE_5STAR[gem_quality][gem_rank]
    return RESONANCE_TABLE[gem_star][gem_rank]
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
- Check aux system rules

### 2. Build Testing

- DPS with resonance
- Survival scaling
- Content thresholds
- Bracket verification

### 3. Integration Testing

- Full build scaling
- Team composition impact
- Content performance
- System interactions
