# Kraftbot - Fantasy Football AI Assistant

A professional Python package providing a Langchain-based conversational AI agent for fantasy football assistance, featuring OpenRouter integration, MCP server support, streaming responses, and comprehensive testing.

## Features

- **🤖 Multi-Model Support**: Compatible with any model available on OpenRouter (GPT-4, Claude, Llama, etc.)
- **🔌 MCP Server Integration**: Connects to Tokenbowl MCP server for fantasy football data tools
- **📝 Multiple Strategy Prompts**: Choose from aggressive, conservative, analytical, or custom strategies
- **💬 Conversational Memory**: Maintains context throughout your chat session
- **⚡ Streaming Responses**: See answers generated in real-time
- **📊 Comprehensive Token Tracking**: Monitors input, output, reasoning, and tool-use tokens
- **🎨 Rich Terminal Interface**: Beautiful CLI with command history and auto-suggestions
- **✅ Fully Tested**: Comprehensive test suite for streaming + MCP integration
- **📦 Professional Packaging**: Modern Python package with proper structure

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/kraftbot.git
cd kraftbot

# Install in development mode
make install-dev

# Or install normally
make install
```

### Quick Install

```bash
pip install -e .
```

## Configuration

1. Set up your OpenRouter API key:

```bash
export OPENROUTER_API_KEY=your_api_key_here
```

Or create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your API key
```

Get your API key from [OpenRouter](https://openrouter.ai/keys)

## Usage

### Interactive Chat

```bash
# Start chat with default settings
kraftbot chat

# Use specific strategy and model
kraftbot chat -p aggressive -m anthropic/claude-3.5-sonnet

# Disable MCP integration
kraftbot chat --no-mcp

# Disable streaming for full responses
kraftbot chat --no-stream

# Enable verbose output
kraftbot chat -v
```

### Quick Questions

```bash
# Ask a single question
kraftbot ask -p default "Should I start Justin Jefferson this week?"

# With specific model
kraftbot ask -p analytical -m openai/gpt-4o "Analyze my roster"
```

### List Available Prompts

```bash
kraftbot prompts
```

### Check System Status

```bash
kraftbot status
```

### In-Chat Commands

While in a chat session:
- `exit`, `quit`, `q` - End the session
- `clear` - Clear conversation history
- `tools` - Show MCP server and tool status
- `help` - Show in-chat help

## Available Prompt Strategies

Kraftbot includes multiple pre-configured strategies:

| Prompt | Description |
|--------|-------------|
| **default** | Comprehensive strategy for league 1266471057523490816 with tokenbowl tools |
| **aggressive** | High-risk/high-reward approach for championship runs |
| **conservative** | Risk-averse strategy focusing on consistency |
| **analytical** | Data-driven approach with statistical analysis |
| **few_shot** | Example-based learning approach |
| **kimi_k2** | Custom configuration strategy |

## MCP Integration

The Tokenbowl MCP server provides fantasy football tools:

- `get_league_info` - Retrieve league settings and configuration
- `get_roster` - Get roster information for any team
- `get_matchup` - View weekly matchups and scores
- `get_players` - Access player stats and projections
- `get_transactions` - Review trades and waiver moves
- `get_trending_players` - See who's hot in fantasy

**Note**: MCP integration provides tool awareness to guide analysis. Full tool calling requires extended implementation.

## Development

### Running Tests

```bash
# Run all tests
make test

# Run only unit tests (no API calls)
make test-unit

# Run integration tests (requires API key)
make test-integration

# Run streaming tests
make test-streaming

# Run MCP integration tests
make test-mcp

# Run tests with coverage
make test-cov
```

### Code Quality

```bash
# Run linters
make lint

# Format code
make format
```

### Project Structure

```
kraftbot/
├── kraftbot/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent.py          # Main agent with streaming support
│   │   └── models.py          # Data models and structures
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── manager.py         # MCP server manager
│   ├── cli/
│   │   ├── __init__.py
│   │   └── app.py             # CLI application
│   └── utils/
│       ├── __init__.py
│       └── prompts.py         # Prompt loading utilities
├── tests/
│   ├── __init__.py
│   └── test_streaming_mcp.py  # Tests for streaming + MCP
├── prompts/                    # Strategy prompt files
│   ├── default.md
│   ├── aggressive.md
│   ├── conservative.md
│   └── analytical.md
├── pyproject.toml              # Modern Python packaging
├── setup.py                    # Backwards compatibility
├── pytest.ini                  # Test configuration
├── Makefile                    # Development tasks
├── mcp_config.yaml            # MCP server configuration
└── README.md                   # This file
```

## Architecture

### Core Components

**`kraftbot.core.agent.KraftbotAgent`**
- Main agent class with conversation memory
- Supports both streaming and non-streaming modes
- Handles MCP server integration
- Manages system prompt augmentation with tool info

**`kraftbot.mcp.manager.MCPManager`**
- Manages MCP server connections
- Checks server availability
- Provides tool descriptions for system prompts

**`kraftbot.cli.app`**
- Professional CLI with click
- Multiple commands: chat, ask, prompts, status
- Rich terminal interface with colors and formatting

### Data Flow

1. CLI command initializes `KraftbotAgent` with user preferences
2. Agent checks MCP server availability asynchronously
3. System prompt is augmented with available tool information
4. User input is processed with full conversation context
5. Response streams back with token tracking
6. Memory is updated for next interaction

## Testing Strategy

The test suite verifies:

✅ **Unit Tests**
- MCP manager initialization and configuration
- Agent initialization with/without MCP
- Prompt loading and management
- Token counting

✅ **Integration Tests**
- Real API calls with streaming
- MCP server connectivity
- Streaming with MCP enabled
- Alternating between streaming and non-streaming modes

✅ **Compatibility Tests**
- Streaming and MCP working together
- System prompt includes MCP tools when available
- Memory consistency across modes

Run tests with:
```bash
make test              # All tests
make test-streaming    # Streaming-specific
make test-mcp          # MCP-specific
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | Yes |
| `ENABLE_MCP` | Enable/disable MCP integration | No (default: true) |
| `VERBOSE` | Enable verbose logging | No (default: false) |

## Popular Models

Compatible with all OpenRouter models:

- `openai/gpt-4o` - Latest GPT-4 with vision
- `openai/gpt-4o-mini` - Fast and cost-effective
- `anthropic/claude-3.5-sonnet` - Excellent reasoning
- `anthropic/claude-3-opus` - Most capable Claude
- `meta-llama/llama-3.1-70b-instruct` - Open source powerhouse
- `google/gemini-pro-1.5` - Google's latest

See [OpenRouter Models](https://openrouter.ai/models) for the full list.

## Example Session

```bash
$ kraftbot chat -p aggressive -m anthropic/claude-3.5-sonnet

╭─────────────────────────────────────────╮
│ Kraftbot Fantasy Football Assistant     │
│ Model: anthropic/claude-3.5-sonnet      │
│ Prompt: aggressive                      │
│ MCP: Enabled                            │
│ Streaming: Enabled                      │
│                                         │
│ Commands: exit, quit, clear, tools, help│
╰─────────────────────────────────────────╯

You: Should I trade away my RB1 for a WR1 upgrade?

Thinking...

That's a classic aggressive championship move! Let me break down the considerations...

[Streaming response continues...]

You: tools

MCP Server Status:

• tokenbowl: connected
  Fantasy football data for Sleeper leagues
  Tools:
    - get_league_info
    - get_roster
    - get_matchup
    - get_players
    - get_transactions
    - get_trending_players

You: exit
Goodbye! May your fantasy team prosper!
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Format code: `make format`
6. Submit a pull request

## License

MIT License - Use freely for your fantasy football domination!

## Support

- Report issues on [GitHub Issues](https://github.com/yourusername/kraftbot/issues)
- Check documentation with `kraftbot --help`
- Run system check with `kraftbot status`

---

**Remember**: Kraftbot provides advice based on AI analysis. The final lineup decisions are yours. Good luck with your fantasy season! 🏈🏆
