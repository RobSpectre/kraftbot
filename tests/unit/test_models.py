"""Tests for core data models."""

import pytest
from kraftbot.core.models import AgentResponse, AgentDependencies


class TestAgentResponse:
    """Test AgentResponse model."""

    def test_agent_response_creation(self):
        """Test creating an AgentResponse."""
        response = AgentResponse(response="Test response")
        assert response.response == "Test response"

    def test_agent_response_str_representation(self):
        """Test string representation of AgentResponse."""
        response = AgentResponse(response="Test response")
        str_repr = str(response)
        assert "Test response" in str_repr


class TestAgentDependencies:
    """Test AgentDependencies dataclass."""

    def test_agent_dependencies_creation(self):
        """Test creating AgentDependencies."""
        deps = AgentDependencies(
            user_id="test_user",
            session_id="test_session",
            metadata={"key": "value"}
        )

        assert deps.user_id == "test_user"
        assert deps.session_id == "test_session"
        assert deps.metadata == {"key": "value"}

    def test_agent_dependencies_defaults(self):
        """Test AgentDependencies with default metadata."""
        deps = AgentDependencies(
            user_id="test_user",
            session_id="test_session"
        )

        assert deps.user_id == "test_user"
        assert deps.session_id == "test_session"
        assert deps.metadata == {}