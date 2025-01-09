# Secondary (Normal) Gems

## Overview

Secondary gems are normal gems that can be socketed into set items to provide basic stat boosts. Unlike legendary gems, they focus on straightforward attribute improvements without complex effects.

## Gem Types

### 1. Sapphire

- **Primary Effect**: Armor Penetration
- Example at Rank 8: +656 Armor Penetration
- Best for: Offensive builds focused on bypassing enemy defenses

### 2. Tourmaline

- **Primary Effect**: Damage
- Example at Rank 9: +380 Damage
- Best for: Pure damage output builds

### 3. Topaz

- **Primary Effect**: Resistance
- Example at Rank 8: +656 Resistance
- Best for: Defensive builds and survivability

### 4. Ruby

- **Primary Effect**: TBD
- Socket locations: Set items
- Best for: TBD based on effect

### 5. Citrine

- **Primary Effect**: TBD
- Socket locations: Set items
- Best for: TBD based on effect

### 6. Aquamarine

- **Primary Effect**: TBD
- Socket locations: Set items
- Best for: TBD based on effect

## Progression System

### Ranking Up

- Gems can be ranked up to increase their effectiveness
- Each rank provides linear stat increases
- Maximum rank varies by gem type
- Higher ranks require more resources

### Rank Examples

```text
Rank 8 Sapphire: +656 Armor Penetration
Rank 8 Topaz:    +656 Resistance
Rank 9 Tourmaline: +380 Damage
```

## Socket System

### Available Slots

- Set items only (not legendary items)
- One gem per socket
- Multiple sockets possible per item

### Set Item Locations

1. Neck
2. Waist
3. Hands
4. Feet
5. Rings (2 slots)
6. Bracers (2 slots)

## Combat Rating Impact

Secondary gems contribute to Combat Rating through:

1. Direct stat contributions
2. Rank-based CR scaling
3. Set item synergies

## Build Considerations

### PvE Focus

- Prioritize damage gems for speed clearing
- Balance with defensive gems for higher difficulties
- Consider content-specific requirements

### PvP Focus

- Higher emphasis on resistance gems
- Balance between offense and defense
- Consider crowd control interactions

## Data Structure

### Static Data (in indexed/)

Located in `data/indexed/gems/`:

- Base stats per rank
- Progression requirements
- Combat rating contributions
- Socket rules

### Dynamic Data (in GitHub Gists)

Player-specific gem data includes:

- Owned gems and ranks
- Socket assignments
- Total stat contributions

## API Implementation Notes

When implementing secondary gem features:

1. Track gem inventory and ranks
2. Calculate stat contributions
3. Manage socket assignments
4. Update combat rating
5. Consider build synergies
6. Handle upgrade mechanics

## Future Documentation Needs

### Research Required

- [ ] Complete effects for Ruby, Citrine, and Aquamarine
- [ ] Document exact rank progression values
- [ ] List resource requirements for ranking up
- [ ] Detail any special socket rules
- [ ] Document any gem-specific limitations
