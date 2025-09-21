"""Tests for configuration settings."""

import os
import pytest
from kraftbot.config.settings import settings


class TestSettings:
    """Test configuration settings."""

    def test_settings_attributes(self):
        """Test that settings has required attributes."""
        assert hasattr(settings, "openrouter_api_key")
        assert hasattr(settings, "default_model")
        assert hasattr(settings, "enable_logfire")
        assert hasattr(settings, "cli_width")
        assert hasattr(settings, "cli_color")

    def test_api_key_configuration_check(self):
        """Test API key configuration check."""
        # This depends on environment, so we test the method exists
        result = settings.is_api_key_configured()
        assert isinstance(result, bool)

    def test_logfire_configuration_check(self):
        """Test Logfire configuration check."""
        result = settings.is_logfire_configured()
        assert isinstance(result, bool)

    def test_environment_validation(self):
        """Test environment validation method."""
        env_status = settings.validate_environment()
        assert isinstance(env_status, dict)
        assert "openrouter_api_key" in env_status or len(env_status) > 0

    def test_available_models(self):
        """Test that available models are defined."""
        assert hasattr(settings, "available_models")
        assert isinstance(settings.available_models, dict)
        assert len(settings.available_models) > 0

    def test_get_model_config(self):
        """Test getting model configuration."""
        # Get first available model
        first_model = next(iter(settings.available_models.keys()))
        config = settings.get_model_config(first_model)

        assert config is not None
        assert hasattr(config, "provider")

        # Test non-existent model
        config = settings.get_model_config("non-existent-model")
        assert config is None