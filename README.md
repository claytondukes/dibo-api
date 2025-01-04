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
- Inventory Management via GitHub Gists (✅ implemented)
- Build Generation (🚧 in progress)
- Cloudflare Workers backend

## Documentation

### Setup and Configuration
- [Cloudflare Setup](docs/cloudflare.md) - Worker and DNS configuration Guide
- [API Documentation](docs/api/v1.md) - Complete API reference with implemented and planned endpoints

### Game Systems
- [Game Mechanics](docs/game/mechanics.md) - Core game systems and build types
- [Skills Guide](docs/game/skills.md) - Comprehensive skill system documentation
- [Auxiliary Gems](docs/game/aux_gems.md) - Detailed explanation of the auxiliary gem system
- [Equipment Sets](docs/game/sets.md) - Complete guide to equipment sets and their bonuses

## Managing Your Inventory with GitHub Gists

DIBO uses GitHub Gists to store and manage your personal inventory. This provides a secure, version-controlled way to maintain your inventory data.

### Setting Up Your Inventory

1. Create a new GitHub Gist named `gems.json` with your inventory data:

```json
{
  "Berserker's Eye": {
    "owned_rank": 10,
    "quality": null
  },
  "Blessing of the Worthy": {
    "owned_rank": 3,
    "quality": "2"
  }
}
```

2. The gist can be either public or private
3. When you authenticate with DIBO, it will automatically find and use your `gems.json` gist

### Authentication Flow

1. Click the "Login with GitHub" button
2. Authorize DIBO to access your GitHub account (requires `gist` scope)
3. Your inventory will be automatically loaded from your gist

### API Endpoints

#### Get Inventory

```http
GET /auth/inventory
Authorization: Bearer <your_token>
```

Response:
```json
{
  "Berserker's Eye": {
    "owned_rank": 10,
    "quality": null
  },
  ...
}
```

If no inventory gist is found, an empty object `{}` will be returned.

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
