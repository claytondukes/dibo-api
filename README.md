# DIBO API (Diablo Immortal Build Optimizer)

A RESTful API for analyzing Diablo Immortal game data and generating optimal build recommendations. The API processes game data including gems, essences, and their interactions to suggest the most effective character builds.

## Features

- **Game Data Access**
  - [x] Class-specific skills and essences
  - [x] Equipment sets and bonuses
  - [x] Gem stats and synergies
  - [x] Build constraints and requirements

- **Inventory Management**
  - [x] Store personal inventory in GitHub Gists
  - [x] Track owned gems and their ranks
  - [x] Consider available items for build recommendations

- **Authentication**
  - [x] Secure GitHub OAuth 2.0
  - [x] JWT-based authorization
  - [x] User profile management

## Implementation Plans

- [Equipment System](docs/implementation/EQUIPMENT_SYSTEM.md) - Comprehensive plan for the equipment and set bonus system

## Quick Start

1. **Prerequisites**
   - GitHub account for authentication
   - Python 3.13+
   - Valid GitHub OAuth credentials

2. **Setup**

   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/dibo-api.git
   cd dibo-api

   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Set up environment variables
   cp .env.example .env
   ```

3. **Configuration**

   ```env
   # Required environment variables
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   GITHUB_CALLBACK_URL=https://your-api-domain/auth/github/callback
   ```

## Project Structure

```text
dibo-api/
├── api/                 # API implementation
│   ├── auth/           # Authentication endpoints
│   ├── builds/         # Build generation logic
│   ├── core/           # Core functionality
│   ├── models/         # Data models and schemas
│   ├── routes/         # API routes
│   ├── services/       # Business logic
│   └── utils/          # Utility functions
├── data/               # Game data
│   └── indexed/        # Processed game data
│       └── classes/    # Character class data
├── tests/              # Test suites
├── docs/               # Documentation
│   └── api/           # API documentation
└── .github/            # GitHub templates and workflows
    └── ISSUE_TEMPLATE/ # Issue templates
```

## Documentation

- [API Reference](docs/api/v1.md) - Complete API documentation
- [Game Mechanics](docs/game/mechanics.md) - Core game systems

## Roadmap

### Data Management

- [x] Core game data indexing
  - [x] Character classes and skills
  - [x] Equipment and set bonuses
  - [x] Gems and their progression
  - [x] Stats and synergies

- [x] Data validation and constraints
  - [x] Build requirements
  - [x] Equipment compatibility
  - [x] Skill combinations
  - [x] Gem restrictions

- [x] Advanced Data Features
  - [x] Real-time data updates via GitHub Gists
  - [x] Versioned data schemas
  - [x] Custom data extensions

### API Improvements

- [x] Performance optimizations
  - [x] Efficient data loading
  - [x] Response caching
  - [x] Query optimization

- [x] API Security
  - [x] Rate limiting
  - [x] Input validation
  - [x] Error handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### Character Class Data

I need help implementing JSON data files for additional character classes. See our [Character Class Data Implementation](.github/ISSUE_TEMPLATE/character_class_data.md)
template for details on how to contribute.

Current status:

- [x] Barbarian - Complete reference implementation
- [ ] Wizard - Not started
- [ ] Necromancer - Not started
- [ ] Crusader - Not started
- [ ] Blood Knight - Not started
- [ ] Tempest - Not started
- [ ] Demon Hunter - Not started
- [ ] Monk - Not started

### Commit Message Format

Use semantic commit messages with the following prefixes:

- `feat:` New feature
- `fix:` Bug fix
- `tweak:` Minor adjustments
- `style:` Code style updates
- `refactor:` Code restructure
- `perf:` Performance improvement
- `test:` Test updates
- `docs:` Documentation updates
- `chore:` Maintenance tasks
- `ci:` CI/CD changes
- `build:` Build system changes
- `revert:` Revert changes
- `hotfix:` Urgent fixes
- `init:` New project/feature
- `merge:` Branch merges
- `wip:` Work in progress
- `release:` Release preparation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Blizzard Entertainment for Diablo Immortal
- The Diablo Immortal community for their support and feedback
- My awesome f'n clan :)
