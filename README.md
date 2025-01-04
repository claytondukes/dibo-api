# DIBO (Diablo Immortal Build Optimizer)

A comprehensive API for analyzing Diablo Immortal game data and generating optimal build recommendations. The tool considers various game elements including gems, essences, and their interactions to suggest the most effective character builds.

## Features

The main purpose of the project is to provide a tool that may be used
to generate builds based on the user's request. 
For example:

- Raid build
- PVE
- PvP
- Fast Farm
- Survivabilty
- Single-Target DPS
- Maximum buff uptime
- etc.

The system takes into account the base descriptions of weapons, 
skills, sets, etc. and then analyzes the synergies between all 
components including enchantments, curses, gems, auxillary gems, reforges, and skill essences. 

It can also allow an input of player inventory so that it can generate a personalized build based on what you own or don't own. 

For example:

```
{
  "owned_gems": {
    "5_star": [
      {
        "name": "Blessing of the Worthy",
        "rank": 6,
        "quality": 5
      },
    "2_star": [
      {
        "name": "Cutthroat's Grin",
        "rank": 8,
      },
      {
        "name": "Fervent Fang",
        "rank": 9,
      },
      "1_star": [
      {
        "name": "Berserker's Eye",
        "rank": 7,
      }
    ]
  }
}
```


## API Features

- GitHub OAuth authentication (✅ implemented)
- Cloudflare Workers backend

## Documentation

### Setup and Configuration
- [Cloudflare Setup](docs/cloudflare.md) - Worker and DNS configuration Guide
- [API v1 Documentation](docs/v1.md) - REST API endpoints and usage

### Game Systems
- [Game Mechanics](docs/game/mechanics.md) - Core game systems and build types
- [Skills Guide](docs/game/skills.md) - Comprehensive skill system documentation
- [Auxiliary Gems](docs/game/aux_gems.md) - Detailed explanation of the auxiliary gem system

## Project Structure

```
.
├── api/                      # API
├── data                      # Input Data
│   ├── indexed               # JSON Indexed data from raw inputs
│   ├── legacy                # Original CSV files
│   └── raw                   # Raw JSON files used for generating indexes
├── docs/                     # Documentation
│   ├── api/                  # API documentation
│   ├── game/                 # Game mechanics documentation
├── tests/                    # Tests
│   ├── api/                  # API tests
│   └── fixtures/             # Test fixtures
```


## Development

### Prerequisites
- Python 3.13+
- Cloudflare account
- GitHub account (for OAuth)

### Quick Start
1. Clone the repository
2. `cp .env.example .env`
3. Profit! (I should probably document this more ;))

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## [TODO] UI Features

- Manual Builder
- Build sharing via GitHub Gists
- Community build library
