# Rune System

## TODO Items

### Research Needed

- [ ] Document rune types and effects
- [ ] List available rune slots per gear piece
- [ ] Document rune stacking rules
- [ ] Explain rune upgrade system (if any)
- [ ] List rune acquisition methods
- [ ] Document rune transfer system

### Implementation Questions

1. How many rune slots can each gear piece have?
2. Do runes have quality levels or ranks?
3. Can runes be transferred between items?
4. Are there class-specific runes?
5. How do runes interact with other gear modifications?
6. What's the relationship between runes and combat rating?

### Data Structure Needs

- Rune definitions
- Slot configurations
- Effect calculations
- Stacking rules
- Transfer mechanics

## Current Understanding

Basic system components that we know:

1. Runes provide attribute and stat bonuses
2. Multiple rune slots available per item
3. Known effects include:
   - "Base attribute of equipped item increased by 8.0%"
   - "Damage taken while moving decreased by 3.0%"
   - "Attack Speed increased by 4.0%"
   - "Skill cooldowns reduced by 4.0%"

## API Considerations

When implementing rune-related features:

1. Need to track individual rune assignments
2. Calculate cumulative effects
3. Handle rune modifications
4. Integrate with gear system
5. Consider build optimization
