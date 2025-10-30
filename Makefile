.PHONY: help install install-dev test test-unit test-integration test-streaming test-mcp test-cov lint format clean build run chat

help:
	@echo "Kraftbot Development Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make install          Install package in production mode"
	@echo "  make install-dev      Install package with development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make test-integration Run integration tests (requires API key)"
	@echo "  make test-streaming   Run streaming tests"
	@echo "  make test-mcp         Run MCP integration tests"
	@echo "  make test-cov         Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run linters (black, isort, mypy)"
	@echo "  make format           Format code with black and isort"
	@echo ""
	@echo "Development:"
	@echo "  make run              Run kraftbot CLI"
	@echo "  make chat             Start interactive chat session"
	@echo "  make clean            Clean build artifacts"
	@echo "  make build            Build package distribution"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-unit:
	pytest tests/ -v -m "not integration"

test-integration:
	@echo "Running integration tests (requires OPENROUTER_API_KEY)..."
	pytest tests/test_streaming_mcp.py::TestStreamingIntegration -v

test-streaming:
	@echo "Running streaming tests..."
	pytest tests/test_streaming_mcp.py -k "streaming" -v

test-mcp:
	@echo "Running MCP integration tests..."
	pytest tests/test_streaming_mcp.py::TestMCPManager -v
	pytest tests/test_streaming_mcp.py::TestMCPAndStreamingCombination -v

test-cov:
	pytest tests/ --cov=kraftbot --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	@echo "Running black..."
	black --check kraftbot/ tests/
	@echo "Running isort..."
	isort --check-only kraftbot/ tests/
	@echo "Running mypy..."
	mypy kraftbot/

format:
	@echo "Formatting with black..."
	black kraftbot/ tests/
	@echo "Formatting with isort..."
	isort kraftbot/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

run:
	kraftbot --help

chat:
	kraftbot chat

# Quick test for streaming + MCP together
test-quick:
	@echo "Running quick streaming + MCP tests..."
	pytest tests/test_streaming_mcp.py::TestKraftbotAgent::test_agent_initialization -v
	pytest tests/test_streaming_mcp.py::TestKraftbotAgent::test_agent_initialize_with_mcp -v
	pytest tests/test_streaming_mcp.py::TestMCPManager::test_mcp_manager_init -v
