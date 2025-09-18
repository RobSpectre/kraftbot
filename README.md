# 🏈 KraftBot - Fantasy Football Management Agent

[![CI](https://github.com/RobSpectre/kraftbot/actions/workflows/ci.yml/badge.svg)](https://github.com/RobSpectre/kraftbot/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/RobSpectre/kraftbot/branch/main/graph/badge.svg)](https://codecov.io/gh/RobSpectre/kraftbot)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A specialized AI agent for managing fantasy football teams, built with PydanticAI and integrated with Sleeper API via MCP (Model Context Protocol). KraftBot provides intelligent lineup optimization, waiver wire analysis, trade recommendations, and strategic guidance for your fantasy football league.

## ✨ Features

- **🎯 Beautiful CLI**: Built with Typer and Rich for maximum visual appeal
- **🤖 OpenRouter Integration**: Access multiple LLM providers through OpenRouter's unified API
- **🔌 MCP Server Support**: Connect to external tools and services via MCP servers
- **📊 Logfire Observability**: Full instrumentation with Logfire for monitoring and debugging
- **🔒 Type Safety**: Structured responses using Pydantic models
- **🛠️ Tool System**: Built-in tools with support for external MCP tools
- **📝 Custom System Prompts**: Load specialized prompts from Markdown files
- **⚡ Async Support**: Full asynchronous operation for better performance
- **🎨 Rich Formatting**: Beautiful tables, progress bars, and animations

## 📦 Installation

### Option 1: Install from source
```bash
git clone https://github.com/example/kraftbot.git
cd kraftbot
make install-dev  # or pip install -e .
```

### Option 2: Install from PyPI (when published)
```bash
pip install kraftbot
```

### Option 3: Development Installation  
```bash
git clone https://github.com/example/kraftbot.git
cd kraftbot
make install-dev
```

## 🔧 Configuration

Set your environment variables:
```bash
export OPENROUTER_API_KEY="your-api-key-here"
export LOGFIRE_WRITE_TOKEN="your-logfire-token"  # Optional but recommended
```

Or create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
# Edit .env with your API keys
```

## 🎯 CLI Usage

### Interactive Chat
Start a beautiful interactive chat session:
```bash
kraftbot chat
# or: python main.py chat
# or: make cli-chat
```

With custom model:
```bash
kraftbot chat --model "openai/gpt-4"
```

### List Available Models
See all available models and their capabilities:
```bash
kraftbot models
# or: make cli-models
```

### Test a Model
Quick test with any model:
```bash
kraftbot test --model "anthropic/claude-3.5-sonnet" --prompt "Hello, world!"
```

### Compare Models
Compare responses across multiple models:
```bash
kraftbot compare --prompt "Explain quantum computing" --model "anthropic/claude-3.5-sonnet" --model "openai/gpt-4"
```

### MCP Information
Learn about MCP integration:
```bash
kraftbot mcp
```

### System Status
Check system configuration and environment:
```bash
kraftbot status
# or: make cli-status
```

### 📝 System Prompt Management
Manage custom system prompts from Markdown files:

#### List Available Prompts
```bash
kraftbot prompts
```

#### Create a New Prompt
```bash
kraftbot create-prompt my_prompt --template coding
# Templates: default, coding, creative, analytical
```

#### Show Prompt Contents
```bash  
kraftbot show-prompt coding_assistant
```

#### Use Custom Prompt in Chat
```bash
kraftbot chat --prompt-file coding_assistant
# or: kraftbot test --prompt-file data_analyst --prompt "Analyze this data"
```

#### Validate All Prompts
```bash
kraftbot validate-prompts
```

## 📚 Programmatic Usage

```python
import asyncio
from kraftbot import PydanticAIAgent

async def main():
    # Create agent with custom system prompt from file
    agent = PydanticAIAgent(
        openrouter_api_key="your-api-key",
        model_name="anthropic/claude-3.5-sonnet",
        enable_logfire=True,  # Uses LOGFIRE_WRITE_TOKEN env var
        system_prompt_file="coding_assistant"  # Load from markdown file
    )
    
    # Or use explicit system prompt
    agent_explicit = PydanticAIAgent(
        openrouter_api_key="your-api-key",
        model_name="openai/gpt-4",
        system_prompt="You are a helpful coding assistant..."
    )
    
    # Run a query
    response = await agent.run(
        prompt="Help me optimize this Python function",
        user_id="user123",
        session_id="session1"
    )
    
    print(f"Response: {response.response}")
    print(f"Confidence: {response.confidence}")
    print(f"Tools used: {response.tools_used}")
    print(f"Response time: {response.response_time}s")

if __name__ == "__main__":
    asyncio.run(main())
```

### Adding MCP Servers

#### STDIO Server (e.g., MCP Run Python)
```python
# Add Python execution server
agent.add_mcp_server_stdio(
    'deno',
    [
        'run',
        '-N', '-R=node_modules', '-W=node_modules', '--node-modules-dir=auto',
        'jsr:@pydantic/mcp-run-python',
        'stdio'
    ],
    tool_prefix='python',
    name='python_executor'
)
```

#### SSE Server
```python  
# Add weather service server
agent.add_mcp_server_sse(
    url='http://localhost:3001/sse',
    tool_prefix='weather',
    name='weather_service'
)
```

## Available Models

You can use any model available through OpenRouter. Popular options include:

- `anthropic/claude-3.5-sonnet`
- `openai/gpt-4`
- `openai/gpt-4-turbo`
- `meta-llama/llama-3.1-70b-instruct`
- `google/gemini-pro`

## Response Structure

The agent returns structured responses with the following fields:

```python
class AgentResponse(BaseModel):
    response: str              # Main response text
    confidence: float          # Confidence level (0.0-1.0)
    tools_used: List[str]      # Tools that were used
    metadata: Dict[str, Any]   # Additional metadata
```

## Built-in Tools

The agent comes with several built-in tools:

- **get_user_context**: Retrieves user and session information
- **calculate**: Performs basic mathematical calculations

## MCP Server Integration

The Model Context Protocol (MCP) allows the agent to connect to external services and tools. Common MCP servers include:

- **MCP Run Python**: Execute Python code in a sandboxed environment
- **Weather Services**: Get weather information
- **Database Connectors**: Query databases
- **Web Search**: Search the internet
- **File Operations**: Read and write files

## Example: Complete Setup

```python
#!/usr/bin/env python3
import asyncio
import os
from pydantic_ai_agent import PydanticAIWithOpenRouterMCP

async def main():
    # Initialize agent
    agent = PydanticAIWithOpenRouterMCP(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        model_name="anthropic/claude-3.5-sonnet"
    )
    
    # Add MCP servers if available
    # agent.add_mcp_server_stdio('python', ['mcp_python_server.py'])
    
    # Interactive loop
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit']:
            break
            
        response = await agent.run(
            prompt=user_input,
            user_id="interactive_user",
            session_id="cli_session"
        )
        
        print(f"Agent: {response.response}")
        if response.confidence < 0.7:
            print(f"(Low confidence: {response.confidence:.2f})")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔧 Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)
- `LOGFIRE_WRITE_TOKEN`: Your Logfire token for observability (optional but highly recommended)

## 🎨 CLI Features

The CLI includes many visual enhancements:

- **🌈 Rich formatting**: Beautiful tables, panels, and syntax highlighting
- **⏳ Loading animations**: Smooth spinners and progress bars
- **📊 Real-time metrics**: Response times, confidence scores, and tool usage
- **🎯 Interactive prompts**: User-friendly input with auto-completion
- **📱 Responsive design**: Adapts to different terminal sizes
- **🔍 Environment checking**: Automatic validation of API keys and configuration

## 📊 Logfire Integration

When `LOGFIRE_WRITE_TOKEN` is set, KraftBot automatically:

- **📈 Instruments PydanticAI**: Tracks all agent interactions and tool calls
- **🔌 Monitors MCP servers**: Logs server connections and tool executions  
- **⏱️ Records timing**: Measures response times and performance metrics
- **🐛 Captures errors**: Detailed error logging for debugging
- **📋 Tracks usage**: Token consumption and API call statistics

Access your logs at: https://logfire.pydantic.dev/

## Error Handling

The agent includes comprehensive error handling for:
- API connection issues
- Invalid model names
- MCP server connection failures
- Tool execution errors

## 🛠️ Development

### Quick Start
```bash
git clone https://github.com/example/kraftbot.git
cd kraftbot
make install-dev
```

### Available Commands
```bash
make help                 # Show all available commands
make install             # Install package
make install-dev         # Install with development dependencies  
make test                # Run tests
make test-coverage       # Run tests with coverage
make lint                # Run linting
make format              # Format code
make clean               # Clean build artifacts
make build               # Build package
make run-examples        # Run example scripts
```

### Running Examples
```bash
# Run all examples
make run-examples

# Or run individually
python kraftbot/examples/basic_usage.py
python kraftbot/examples/mcp_integration.py
python kraftbot/examples/model_comparison.py
```

### Running Tests
```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
pytest kraftbot/tests/test_agent.py -v
```

### Module Structure
```
kraftbot/
├── __init__.py              # Main package exports
├── core/                    # Core agent functionality
│   ├── agent.py            # Main PydanticAIAgent class
│   ├── models.py           # Pydantic data models
│   └── observability.py    # Logfire integration
├── cli/                     # CLI interface
│   ├── app.py              # Main CLI application
│   ├── commands.py         # CLI command implementations
│   └── utils.py            # CLI utilities and formatting
├── mcp/                     # MCP integration
│   ├── manager.py          # MCP server manager
│   └── servers.py          # MCP server configurations
├── config/                  # Configuration management
│   └── settings.py         # Settings and environment handling
├── utils/                   # General utilities
│   └── helpers.py          # Helper functions
├── tests/                   # Test suite
├── examples/               # Example scripts
└── ...
```

### Extending KraftBot

1. **Add new tools**:
```python
@agent.tool
async def my_custom_tool(ctx: RunContext[AgentDependencies], param: str) -> str:
    """Custom tool description"""
    return f"Processed: {param}"
```

2. **Add new MCP servers**:
```python
agent.add_mcp_server_stdio('my_server', ['my_command', 'args'])
```

3. **Extend response models**:
```python
class CustomAgentResponse(AgentResponse):
    custom_field: str = Field(description="Custom field")
```

4. **Add new CLI commands**:
```python
@app.command()
def my_command():
    """My custom command"""
    pass
```

## 🧪 Testing

The project includes comprehensive tests covering:
- Core agent functionality
- MCP server management  
- Configuration handling
- CLI interface components

## 📄 License

This project is provided as an example and educational resource under the MIT License.