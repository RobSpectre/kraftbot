# 🏈 KraftBot - Fantasy Football Management Agent

[![CI](https://github.com/RobSpectre/kraftbot/actions/workflows/ci.yml/badge.svg)](https://github.com/RobSpectre/kraftbot/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/RobSpectre/kraftbot/branch/main/graph/badge.svg)](https://codecov.io/gh/RobSpectre/kraftbot)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
A specialized AI agent for managing fantasy football teams, built with PydanticAI and integrated with Sleeper API via MCP (Model Context Protocol). KraftBot provides intelligent lineup optimization, waiver wire analysis, trade recommendations, and strategic guidance for your fantasy football league.

## ✨ Features

- **🏆 Fantasy Football Expertise**: Specialized AI agent trained for fantasy football strategy and analysis
- **📊 Sleeper Integration**: Direct access to your Sleeper league data via MCP server
- **🎯 Multiple Strategy Modes**: Choose from aggressive, conservative, analytical, or default approaches
- **💡 Intelligent Recommendations**: Lineup optimization, waiver pickups, and trade analysis
- **🎨 Beautiful CLI**: Built with Typer and Rich for an excellent command-line experience
- **🤖 Multi-Model Support**: Access multiple LLMs through OpenRouter integration
- **📈 Season-Long Strategy**: Balance weekly wins with long-term championship goals

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/your-username/kraftbot.git
cd kraftbot
```

2. **Install dependencies**:
```bash
make install-dev
```

3. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
- `OPENROUTER_API_KEY` - Get from [OpenRouter](https://openrouter.ai/)
- `LOGFIRE_WRITE_TOKEN` - Optional, for observability

### Basic Usage

**Start an interactive chat session**:
```bash
python main.py chat
```

**Test with a specific prompt**:
```bash
python main.py test --prompt "Analyze my Week 1 lineup"
```

**List available models**:
```bash
python main.py models
```

**Check system status**:
```bash
python main.py status
```

## 🎯 Strategy Modes

KraftBot supports multiple fantasy football strategy approaches via built-in prompt files:

### Available Strategies

- **`default`** - Balanced approach for optimal weekly and season-long performance
- **`aggressive`** - High-risk, high-reward strategy for championship runs
- **`conservative`** - Safe, consistent approach to avoid busts
- **`analytical`** - Data-driven decisions based on advanced metrics

### Using Strategy Modes

```bash
# Use a specific strategy
python main.py chat --prompt aggressive
python main.py chat --prompt conservative
python main.py chat --prompt analytical

# List all available prompts
python main.py prompts

# Test with custom strategy
python main.py test --system-prompt aggressive --prompt "Should I start Ja'Marr Chase this week?"
```

### Custom Strategies

Create your own strategy by adding a `.md` file to `kraftbot/prompts/` or use any external file:

```bash
# Use custom prompt file
python main.py chat --prompt /path/to/my_strategy.md
```

## 🔌 Sleeper Integration

KraftBot automatically connects to a Sleeper MCP server to access your fantasy football data:

- **League Information**: Rosters, matchups, standings
- **Player Data**: Stats, projections, availability
- **Waiver Wire**: Available free agents and their potential
- **Trade Analysis**: Evaluate potential trades with other managers

The MCP integration is enabled by default. To disable:
```bash
ENABLE_MCP_SERVER=false python main.py chat
```

## 📋 CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `chat` | Interactive chat session | `python main.py chat --prompt aggressive` |
| `test` | Test a specific prompt | `python main.py test --prompt "Analyze my lineup"` |
| `models` | List available AI models | `python main.py models` |
| `prompts` | Show available strategy prompts | `python main.py prompts` |
| `status` | System configuration status | `python main.py status` |
| `compare` | Compare responses across models | `python main.py compare --prompt "Trade advice"` |
| `mcp` | MCP integration information | `python main.py mcp` |

## 🎮 Example Usage

### Weekly Lineup Analysis
```bash
python main.py chat --prompt analytical
# Then ask: "Should I start Justin Jefferson or Tyreek Hill this week?"
```

### Waiver Wire Strategy
```bash
python main.py test --prompt "Who should I pick up from waivers this week?"
```

### Trade Evaluation
```bash
python main.py chat --prompt conservative
# Then ask: "Should I trade my RB1 for two WR2s?"
```

### Multi-Model Comparison
```bash
python main.py compare --prompt "Rank my RBs for this week" --model "anthropic/claude-3.5-sonnet" --model "openai/gpt-4"
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with:
```bash
# Required
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional
LOGFIRE_WRITE_TOKEN=your_logfire_token
ENABLE_MCP_SERVER=true
MCP_SERVER_COMMAND=python
MCP_SERVER_ARGS=-m sleeper_mcp_server
```

### Available Models

Popular models for fantasy football analysis:
- `anthropic/claude-3.5-sonnet` (Recommended for detailed analysis)
- `openai/gpt-4` (Great for strategic thinking)
- `openai/gpt-4-turbo` (Fast responses)
- `meta-llama/llama-3.1-70b-instruct` (Alternative option)

View all available models: `python main.py models`

## 🛠️ Development

### Development Commands

```bash
make install-dev     # Install with dev dependencies
make test           # Run tests
make test-coverage  # Run tests with coverage
make lint           # Run linting (black, isort, mypy)
make format         # Format code
make clean          # Clean build artifacts
make build          # Build package
```

### Project Structure

```
kraftbot/
├── kraftbot/
│   ├── core/           # Core agent functionality
│   ├── cli/            # Command-line interface
│   ├── mcp/            # Sleeper MCP integration
│   ├── prompts/        # Fantasy football strategy prompts
│   ├── config/         # Configuration management
│   └── utils/          # Utility functions
├── main.py             # CLI entry point
└── pyproject.toml      # Project configuration
```

## 🎯 What KraftBot Can Help With

- **Weekly Lineup Decisions**: Start/sit recommendations based on matchups and projections
- **Waiver Wire Strategy**: Identify valuable pickups before others notice
- **Trade Analysis**: Evaluate trade proposals and find win-win deals
- **Season Planning**: Balance short-term gains with championship strategy
- **Matchup Analysis**: Understand opponent weaknesses and exploit them
- **Player Evaluation**: Deep dives into player performance and trends
- **League Strategy**: Adapt tactics based on your league's scoring and tendencies

## 📈 Fantasy Football Expertise

KraftBot's default behavior is optimized for fantasy football management with knowledge of:

- **Scoring Systems**: PPR, Half-PPR, Standard scoring
- **Positional Strategy**: RB scarcity, WR depth, streaming strategies
- **Matchup Analysis**: Vegas lines, pace of play, weather conditions
- **Player Health**: Injury reports and their fantasy implications
- **Advanced Metrics**: Target share, red zone usage, snap counts
- **Season Trends**: Strength of schedule, playoff implications

## 📄 License

MIT License - See LICENSE file for details.

---

**Built for fantasy football managers who want to dominate their leagues with AI-powered insights.**