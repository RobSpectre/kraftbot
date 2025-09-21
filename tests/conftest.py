"""Pytest configuration and fixtures."""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    original_vars = {}
    test_vars = {
        "OPENROUTER_API_KEY": "test_api_key",
        "LOGFIRE_WRITE_TOKEN": "test_logfire_token",
    }

    # Store original values
    for key in test_vars:
        original_vars[key] = os.environ.get(key)

    # Set test values
    for key, value in test_vars.items():
        os.environ[key] = value

    yield test_vars

    # Restore original values
    for key, original_value in original_vars.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def sample_prompt_file(temp_dir):
    """Create a sample prompt file for testing."""
    prompt_content = """# Sample Fantasy Football Prompt

You are a fantasy football expert. Provide advice on:
- Player recommendations
- Injury analysis
- Matchup insights

Be concise and actionable."""

    prompt_file = Path(temp_dir) / "sample.md"
    prompt_file.write_text(prompt_content)
    return prompt_file


@pytest.fixture(autouse=True)
def disable_logfire():
    """Disable Logfire for tests to avoid external dependencies."""
    with pytest.MonkeyPatch().context() as m:
        # Mock logfire to prevent actual initialization
        m.setattr("kraftbot.core.observability.logfire", None)
        yield