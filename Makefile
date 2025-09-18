.PHONY: help install install-dev test lint format clean build docs run-examples

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev]"
	pip install -r requirements.txt

test:  ## Run tests
	pytest kraftbot/tests/ -v

test-coverage:  ## Run tests with coverage
	pytest kraftbot/tests/ --cov=kraftbot --cov-report=html --cov-report=term-missing

lint:  ## Run linting
	black --check kraftbot/
	isort --check-only kraftbot/
	mypy kraftbot/

format:  ## Format code
	black kraftbot/
	isort kraftbot/

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

build:  ## Build package
	python -m build

docs:  ## Generate documentation (placeholder)
	@echo "Documentation generation not implemented yet"

run-examples:  ## Run example scripts
	@echo "Running basic usage example..."
	python kraftbot/examples/basic_usage.py
	@echo "\nRunning MCP integration example..."
	python kraftbot/examples/mcp_integration.py
	@echo "\nRunning model comparison example..."
	python kraftbot/examples/model_comparison.py

cli-chat:  ## Start CLI chat
	python main.py chat

cli-models:  ## Show available models
	python main.py models

cli-status:  ## Show system status
	python main.py status

cli-prompts:  ## List available prompts
	python main.py prompts

cli-create-prompt:  ## Create a new prompt (name=prompt_name template=default|coding|creative|analytical)
	python main.py create-prompt $(name) --template $(template)

cli-show-prompt:  ## Show prompt contents (name=prompt_name)
	python main.py show-prompt $(name)


# Development shortcuts
dev-install: install-dev  ## Alias for install-dev
dev-test: test-coverage   ## Alias for test-coverage  
dev-format: format lint   ## Format and lint code