# DIBO API (Diablo Immortal Build Optimizer)

A RESTful API for analyzing Diablo Immortal game data and generating optimal build recommendations. The API processes game data including gems, essences, and their interactions to suggest the most effective character builds.

## Features

- **Build Generation & Analysis**
  - Generate optimized builds based on playstyle (Raid, PvP, PvE)
  - Analyze existing builds for optimization opportunities
  - Consider synergies between skills, gems, and equipment

- **Game Data Access**
  - Class-specific skills and essences
  - Equipment sets and bonuses
  - Gem stats and synergies
  - Build constraints and requirements

- **Inventory Management**
  - Store personal inventory in GitHub Gists
  - Track owned gems and their ranks
  - Consider available items for build recommendations

- **Authentication**
  - Secure GitHub OAuth 2.0
  - JWT-based authorization
  - User profile management

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

```
dibo-api/
├── api/                 # API implementation
│   ├── auth/           # Authentication endpoints
│   ├── builds/         # Build generation logic
│   └── data/           # Data management
├── data/               # Game data
│   └── indexed/        # Processed game data
├── tests/              # Test suites
└── docs/               # Documentation
    └── api/            # API documentation
```

## Documentation

- [API Reference](docs/api/v1.md) - Complete API documentation
- [Game Mechanics](docs/game/mechanics.md) - Core game systems

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Blizzard Entertainment for Diablo Immortal
- The Diablo Immortal community for their support and feedback
