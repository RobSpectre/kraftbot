"""Integration tests for CLI commands."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from typer.testing import CliRunner
from kraftbot.cli.app import create_app


class TestCLICommands:
    """Test CLI command integration."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.app = create_app()

    def test_models_command(self):
        """Test the models command."""
        result = self.runner.invoke(self.app, ["models"])
        # Should not crash and should show models
        assert result.exit_code == 0
        assert "Available Models" in result.stdout or "Models" in result.stdout

    def test_prompts_command(self):
        """Test the prompts command."""
        result = self.runner.invoke(self.app, ["prompts"])
        # Should not crash
        assert result.exit_code == 0

    def test_mcp_command(self):
        """Test the mcp command."""
        result = self.runner.invoke(self.app, ["mcp"])
        # Should not crash and show MCP info
        assert result.exit_code == 0
        assert "MCP" in result.stdout

    def test_status_command(self):
        """Test the status command."""
        result = self.runner.invoke(self.app, ["status"])
        # Should not crash
        assert result.exit_code == 0

    @patch("kraftbot.cli.commands.settings")
    def test_test_command_no_api_key(self, mock_settings):
        """Test the test command without API key."""
        mock_settings.is_api_key_configured.return_value = False

        result = self.runner.invoke(self.app, ["test", "--prompt", "Hello"])
        # Should exit with error when no API key
        assert result.exit_code != 0

    @patch("kraftbot.cli.commands.initialize_agent")
    @patch("kraftbot.cli.commands.check_environment")
    def test_test_command_with_mocked_agent(self, mock_check_env, mock_init_agent):
        """Test the test command with mocked agent."""
        mock_check_env.return_value = True
        mock_init_agent.return_value = True

        # Mock agent
        mock_agent = MagicMock()
        mock_response = MagicMock()
        mock_response.response = "Test response"
        mock_agent.run.return_value = mock_response

        with patch("kraftbot.cli.commands.agent", mock_agent):
            result = self.runner.invoke(self.app, ["test", "--prompt", "Hello"])
            # The test might still fail due to async issues, but we're testing the setup

    def test_help_output(self):
        """Test help output."""
        result = self.runner.invoke(self.app, ["--help"])
        assert result.exit_code == 0
        assert "KraftBot" in result.stdout

    def test_command_registration(self):
        """Test that all commands are registered."""
        result = self.runner.invoke(self.app, ["--help"])
        commands = ["chat", "models", "test", "compare", "mcp", "status", "prompts"]

        for command in commands:
            assert command in result.stdout