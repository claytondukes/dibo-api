# Build Templates Reference

This directory contains reference templates that were originally used to define common build patterns for both PvE and PvP content. These templates have been moved to the documentation as reference material rather than being used directly in the build generation system.

## Why Reference Only?

The DiBO API is designed to intelligently determine optimal builds based on complex game dynamics, including:

- Player class and level
- Content type (PvE/PvP)
- Team composition
- Enemy types and mechanics
- Current meta
- Player playstyle preferences
- Combat Rating requirements
- Normalized vs non-normalized scaling

Having predefined templates could potentially limit the API's ability to:

1. Discover new, more optimal combinations
2. Adapt to meta changes
3. Consider unique player circumstances
4. Account for gem resonance at different star levels
5. Handle edge cases and special scenarios

## Template Organization

While these templates are not used in production, they serve as valuable reference material for:

```text
build_templates/
├── pve/                 # PvE-focused templates
│   ├── raid.json       # Raid optimization examples
│   ├── dps.json        # Pure damage examples
│   └── farm.json       # Farming efficiency examples
│
└── pvp/                 # PvP-focused templates
    ├── survival.json   # Survival build examples
    ├── counter.json    # Counter-damage examples
    ├── control.json    # Crowd control examples
    ├── dps.json        # Burst damage examples
    └── dot.json        # DOT-focused examples
```

## Usage Guidelines

These templates can be used as:

1. Reference for common synergy patterns
2. Examples of effective gem combinations
3. Documentation of proven strategies
4. Starting points for theory crafting
5. Historical record of meta builds

## Contributing

While these templates are no longer used in production, they are still maintained as reference material. When contributing:

1. Document the reasoning behind gem combinations
2. Include relevant meta context
3. Note any specific content requirements
4. Explain synergy mechanics
5. Consider both solo and group implications

## Related Documentation
- [Gem System Overview](../../game/gems.md)
- [Combat Mechanics](../../game/combat.md)
- [Build Generation](../../api/build_generation.md)
