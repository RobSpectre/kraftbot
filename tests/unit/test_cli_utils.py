"""Tests for CLI utility functions."""

import pytest
from unittest.mock import patch, MagicMock
from kraftbot.cli.utils import console, check_environment, display_response
from kraftbot.core.models import AgentResponse


class TestCLIUtils:
    """Test CLI utility functions."""

    def test_console_exists(self):
        """Test that console object is properly initialized."""
        assert console is not None
        assert hasattr(console, "print")

    @patch("kraftbot.cli.utils.settings")
    def test_check_environment(self, mock_settings):
        """Test environment checking function."""
        # Mock settings methods
        mock_settings.validate_environment.return_value = {
            "openrouter_api": {"status": "✅ [green]Configured[/green]"}
        }
        mock_settings.is_api_key_configured.return_value = True

        result = check_environment()
        assert result is True

        # Test when API key is not configured
        mock_settings.is_api_key_configured.return_value = False
        result = check_environment()
        assert result is False

    def test_display_response(self):
        """Test response display function."""
        # Create a test response
        response = AgentResponse(
            response="Test response content",
            confidence=0.9,
            tools_used=["tool1"],
            metadata={"test": "data"}
        )

        # Test that the function runs without error
        # We can't easily test the visual output, but we can ensure it doesn't crash
        try:
            display_response(response, 1.5)
        except Exception as e:
            pytest.fail(f"display_response raised an exception: {e}")

    def test_display_response_with_callable(self):
        """Test display_response with callable response."""
        # Create a mock response with callable response field
        class MockResponse:
            def __init__(self):
                self.response = lambda: "Callable response"

        response = MockResponse()

        try:
            display_response(response, 1.0)
        except Exception as e:
            pytest.fail(f"display_response with callable raised an exception: {e}")

    @patch("kraftbot.cli.utils.settings")
    def test_display_model_table(self, mock_settings):
        """Test model table display."""
        from kraftbot.cli.utils import display_model_table

        # Mock available models
        mock_model_config = MagicMock()
        mock_model_config.provider = "OpenAI"
        mock_model_config.strengths = ["reasoning", "coding", "analysis"]
        mock_model_config.speed = "Fast"
        mock_model_config.cost = "$$"

        mock_settings.available_models = {
            "gpt-4": mock_model_config
        }

        # Test that the function runs without error
        try:
            display_model_table()
        except Exception as e:
            pytest.fail(f"display_model_table raised an exception: {e}")

    @patch("kraftbot.cli.utils.settings")
    def test_display_system_status(self, mock_settings):
        """Test system status display."""
        from kraftbot.cli.utils import display_system_status

        # Mock settings
        mock_settings.openrouter_api_key = "test_key"
        mock_settings.default_model = "gpt-4"

        try:
            display_system_status()
        except Exception as e:
            pytest.fail(f"display_system_status raised an exception: {e}")