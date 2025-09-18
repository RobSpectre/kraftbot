# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation and Setup
- `make install-dev` - Install package with development dependencies
- `make install` - Install package in production mode
- Environment setup: Copy `.env.example` to `.env` and configure API keys

### Testing and Quality Assurance
- `make test` - Run tests with pytest
- `make test-coverage` - Run tests with coverage reporting
- `make lint` - Run linting (black, isort, mypy)
- `make format` - Format code using black and isort

### CLI Commands
- `python main.py chat` - Interactive chat session
- `python main.py chat --prompt aggressive` - Chat with specific system prompt
- `python main.py models` - List available OpenRouter models
- `python main.py status` - Show system configuration status
- `python main.py prompts` - List available system prompts

### Build and Distribution
- `make build` - Build package for distribution
- `make clean` - Clean build artifacts

## Architecture Overview

KraftBot is a **simplified** Python package providing a PydanticAI agent with OpenRouter integration and MCP (Model Context Protocol) support for fantasy football analysis. The architecture has been streamlined for reliability and maintainability:

### Core Components

**kraftbot/core/** - Core agent functionality
- `agent.py` - **Simplified** `PydanticAIAgent` class with minimal complexity
- `models.py` - Pydantic data models (`AgentResponse`, `AgentDependencies`)
- `observability.py` - Basic Logfire integration for telemetry

**kraftbot/cli/** - Command-line interface
- `app.py` - Main CLI application using Typer
- `commands.py` - Core CLI command implementations (chat, models, test, compare)
- `utils.py` - CLI utilities and Rich formatting

**kraftbot/mcp/** - MCP server integration
- `manager.py` - `MCPManager` class for handling MCP server connections
- `servers.py` - MCP server configurations and transport types (STDIO/SSE)

**kraftbot/config/** - Configuration management
- `settings.py` - Environment variables and settings handling

**kraftbot/prompts/** - System prompt management  
- `default.md` - Default fantasy football prompt for 718Rob
- `aggressive.md` - High-risk/high-reward strategy prompt
- `conservative.md` - Safe, consistent strategy prompt
- `analytical.md` - Data-driven statistical analysis prompt

**kraftbot/utils/** - Utility functions
- `prompt_loader.py` - System prompt loading from Markdown files

### Key Design Patterns

1. **Simplified Agent Pattern**: The `PydanticAIAgent` class provides minimal, reliable PydanticAI wrapper
2. **MCP Manager Pattern**: Centralized management of MCP server connections
3. **Structured Responses**: All agent responses follow the `AgentResponse` Pydantic model  
4. **Markdown Prompt System**: System prompts stored in `kraftbot/prompts/*.md` files
5. **CLI Architecture**: Typer-based modular command structure with Rich formatting

### Data Flow

1. CLI commands create `PydanticAIAgent` instances with OpenRouter provider
2. Agent uses `MCPManager` to connect to sleeper-mcp-server for fantasy football tools
3. Built-in system prompt configures agent for fantasy football analysis
4. Optional Logfire integration provides observability
5. Responses return structured `AgentResponse` objects with metadata

### Environment Configuration

Required environment variables:
- `OPENROUTER_API_KEY` - OpenRouter API key for model access
- `LOGFIRE_WRITE_TOKEN` - Optional Logfire token for telemetry

MCP Server Configuration:
- `ENABLE_MCP_SERVER` - Enable/disable automatic MCP server loading (default: true)
- `MCP_SERVER_COMMAND` - Command to run MCP server (default: python)
- `MCP_SERVER_ARGS` - Arguments for MCP server command (default: -m sleeper_mcp_server)

The agent supports multiple OpenRouter models including Claude, GPT-4, and Llama variants.

### System Prompt Management

KraftBot supports multiple system prompts stored as Markdown files:

**Available Prompts:**
- **`default`** - Balanced fantasy football strategy for 718Rob
- **`aggressive`** - High-risk/high-reward approach for championship runs
- **`conservative`** - Safe, consistent strategy to avoid busts
- **`analytical`** - Data-driven approach with statistical focus

**Usage:**
```bash
# List available prompts
python main.py prompts

# Use predefined prompt by name
python main.py chat --prompt aggressive
python main.py chat --prompt conservative
python main.py chat --prompt analytical

# Use custom prompt file by path
python main.py chat --prompt /path/to/my_prompt.md
python main.py chat --prompt ./custom_prompts/my_strategy.md
```

**Creating New Prompts:**
1. **For predefined prompts**: Create a new `.md` file in `kraftbot/prompts/` directory
2. **For custom prompts**: Create a `.md` file anywhere on your filesystem
3. Write the system prompt using Markdown formatting
4. The prompt loader automatically cleans markdown for LLM consumption
5. **Use by name**: `python main.py chat --prompt my_prompt` (looks in kraftbot/prompts/)
6. **Use by path**: `python main.py chat --prompt /full/path/to/prompt.md`

### Simplified Architecture Benefits

The simplified architecture provides:
- **Reliability**: Eliminated complex error handling that caused variable scope issues
- **Maintainability**: Reduced from 295 lines to 130 lines in core agent
- **Performance**: Faster initialization without complex validation loops
- **Clarity**: Single-purpose agent focused on fantasy football analysis

### Important Implementation Notes

**Logfire Observability**: Currently disabled due to instrumentation compatibility issues:
- `logfire.instrument_pydantic_ai()` and `logfire.instrument_mcp()` cause tracing errors
- Error: `no_auto_trace() missing 1 required positional argument: 'x'`
- Logfire configuration works but instrumentation is commented out

**Async/Sync Pattern in CLI**: The CLI commands use a specific pattern to handle async operations:
- Core agent operations are async (using PydanticAI)
- CLI commands are sync functions (required by Typer)
- Use `asyncio.run()` to bridge sync CLI functions to async agent calls
- Example: `response = asyncio.run(agent.run(user_input, user_id, session_id))`

**AsyncIO Compatibility**: Applied compatibility patch for PydanticAI:
- Patches `asyncio.nullcontext` to use `contextlib.nullcontext`
- Resolves AttributeError in PydanticAI library

**Entry Points**: The package can be run via:
- `kraftbot` command (when installed)
- `python main.py` (from repository root)
- Direct CLI module: `python -m kraftbot.cli.app`

**MCP Server Integration**: 
- **Status**: Enabled by default for Sleeper fantasy football functionality
- **Command**: Uses `python -m sleeper_mcp_server` for MCP server execution
- **Configuration**: Enabled via `ENABLE_MCP_SERVER=true` (default)
- **Tools**: Provides sleeper-prefixed tools for fantasy football data access
- **Note**: If issues occur, can be disabled by setting `ENABLE_MCP_SERVER=false`