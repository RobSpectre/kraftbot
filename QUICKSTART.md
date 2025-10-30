# Kraftbot Quick Start Guide

Get up and running with Kraftbot in 5 minutes!

## 1. Install

```bash
# Install the package
pip install -e .

# Or use make
make install-dev
```

## 2. Configure

```bash
# Set your API key
export OPENROUTER_API_KEY=your_key_here
```

## 3. Start Chatting

```bash
# Basic usage
kraftbot chat

# With specific strategy
kraftbot chat -p aggressive

# With specific model
kraftbot chat -m anthropic/claude-3.5-sonnet
```

## 4. Run Tests

```bash
# Quick test to verify streaming + MCP work together
make test-quick

# Run all tests
make test

# Run with coverage
make test-cov
```

## Common Commands

### CLI Commands

```bash
kraftbot chat              # Start interactive chat
kraftbot ask "question"    # Quick one-off question
kraftbot prompts          # List available strategies
kraftbot status           # Check system status
kraftbot --help           # Show all options
```

### In-Chat Commands

```
exit, quit, q      # End session
clear              # Clear conversation history
tools              # Show MCP server status
help               # Show in-chat help
```

### Development Commands

```bash
make test              # Run all tests
make test-streaming    # Test streaming functionality
make test-mcp          # Test MCP integration
make test-unit         # Unit tests only (fast)
make lint              # Check code quality
make format            # Format code
```

## Available Strategies

| Strategy | Use Case |
|----------|----------|
| `default` | General use with tokenbowl tools |
| `aggressive` | High-risk championship push |
| `conservative` | Safe, consistent plays |
| `analytical` | Data-driven decisions |

## Testing Features

### Streaming Tests

Verify streaming works correctly:
```bash
pytest tests/test_streaming_mcp.py::TestStreamingIntegration -v
```

### MCP Tests

Verify MCP integration:
```bash
pytest tests/test_streaming_mcp.py::TestMCPManager -v
```

### Both Together

Verify streaming and MCP work together:
```bash
pytest tests/test_streaming_mcp.py::TestMCPAndStreamingCombination -v
```

## Troubleshooting

### API Key Issues
```bash
# Check if key is set
echo $OPENROUTER_API_KEY

# Verify in status
kraftbot status
```

### MCP Connection Issues
```bash
# Check MCP status
kraftbot chat
# Then type: tools
```

### Test Failures
```bash
# Run with verbose output
kraftbot chat -v

# Check specific test
pytest tests/test_streaming_mcp.py::test_name -v -s
```

## Example Usage

```bash
# Start with aggressive strategy and Claude
kraftbot chat -p aggressive -m anthropic/claude-3.5-sonnet

# In chat:
You: Should I start my backup RB in my flex?
# ... streaming response ...

You: tools
# Shows MCP server status

You: clear
# Clears conversation history

You: What about trading for an injured player?
# Continues with new conversation

You: exit
# Ends session
```

## Next Steps

1. ✅ Install and configure
2. ✅ Run `kraftbot chat` to test basic functionality
3. ✅ Run `make test-quick` to verify tests work
4. ✅ Try different prompt strategies
5. ✅ Run full test suite with `make test`

Happy fantasy footballing! 🏈
