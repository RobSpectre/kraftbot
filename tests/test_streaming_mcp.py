"""
Tests for streaming and MCP integration working together

These tests verify that:
1. Streaming works correctly with and without MCP
2. MCP server connectivity is properly detected
3. Both streaming and non-streaming modes handle MCP awareness
4. Memory is correctly maintained across both modes
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock

from kraftbot.core.agent import KraftbotAgent
from kraftbot.core.models import TokenCounter, AgentResponse, MCPServerInfo
from kraftbot.mcp.manager import MCPManager


# Test API key - use mock or environment variable
TEST_API_KEY = os.getenv('OPENROUTER_API_KEY', 'test_key_for_mocking')
TEST_MODEL = "openai/gpt-4o-mini"
TEST_PROMPT = "You are a test assistant."


class TestMCPManager:
    """Tests for MCP manager functionality"""

    def test_mcp_manager_init(self):
        """Test MCP manager initialization"""
        manager = MCPManager()
        assert manager.config is not None
        assert 'servers' in manager.config
        assert 'global' in manager.config

    @pytest.mark.asyncio
    async def test_tokenbowl_server_check(self):
        """Test checking tokenbowl server status"""
        manager = MCPManager()
        server_info = await manager.check_tokenbowl_server()

        assert isinstance(server_info, MCPServerInfo)
        assert server_info.name == "tokenbowl"
        assert server_info.status in ["connected", "unavailable"]

        if server_info.status == "connected":
            assert len(server_info.tools) > 0
            assert server_info.url is not None

    @pytest.mark.asyncio
    async def test_mcp_initialization(self):
        """Test MCP manager server initialization"""
        manager = MCPManager()
        await manager.initialize_servers(verbose=False)

        assert len(manager.servers) >= 0
        assert isinstance(manager.get_mcp_status(), str)

    def test_mcp_tools_description(self):
        """Test generating tools description"""
        manager = MCPManager()

        # Add a mock server
        manager.servers.append(MCPServerInfo(
            name="test_server",
            status="connected",
            tools=["tool1", "tool2"],
            description="Test server"
        ))

        description = manager.get_tools_description()
        assert "test_server" in description.lower()
        assert "tool1" in description


class TestKraftbotAgent:
    """Tests for Kraftbot agent with streaming and MCP"""

    @pytest.fixture
    def agent(self):
        """Create a test agent"""
        agent = KraftbotAgent(
            model_name=TEST_MODEL,
            api_key=TEST_API_KEY,
            system_prompt=TEST_PROMPT,
            mcp_enabled=True,
            verbose=False
        )
        return agent

    @pytest.fixture
    def agent_no_mcp(self):
        """Create a test agent without MCP"""
        agent = KraftbotAgent(
            model_name=TEST_MODEL,
            api_key=TEST_API_KEY,
            system_prompt=TEST_PROMPT,
            mcp_enabled=False,
            verbose=False
        )
        return agent

    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent.model_name == TEST_MODEL
        assert agent.base_system_prompt == TEST_PROMPT
        assert agent.mcp_enabled is True
        assert isinstance(agent.token_counter, TokenCounter)
        assert isinstance(agent.mcp_manager, MCPManager)

    def test_agent_no_mcp_initialization(self, agent_no_mcp):
        """Test agent initialization without MCP"""
        assert agent_no_mcp.mcp_enabled is False

    @pytest.mark.asyncio
    async def test_agent_initialize_with_mcp(self, agent):
        """Test async initialization with MCP"""
        await agent.initialize()

        # Check if system prompt was updated with MCP tools (if available)
        assert agent.system_prompt is not None

        mcp_status = agent.mcp_manager.get_mcp_status()
        assert mcp_status in ["Disabled", "Unavailable", "Connected (1 server)", "Partial (0/1 servers)"]

    @pytest.mark.asyncio
    async def test_agent_initialize_without_mcp(self, agent_no_mcp):
        """Test async initialization without MCP"""
        await agent_no_mcp.initialize()

        # System prompt should not have MCP tools
        assert agent_no_mcp.system_prompt == TEST_PROMPT

    def test_get_current_week(self, agent):
        """Test fantasy week calculation"""
        week = agent.get_current_week()
        assert isinstance(week, str)
        # Should be one of the valid week types
        valid_weeks = ["Pre-Season", "Week", "Playoffs", "Off-Season"]
        assert any(valid in week for valid in valid_weeks)

    def test_memory_operations(self, agent):
        """Test memory clearing"""
        # Add something to memory
        agent.memory.chat_memory.add_user_message("Test message")
        agent.memory.chat_memory.add_ai_message("Test response")

        assert len(agent.memory.chat_memory.messages) == 2

        # Clear memory
        agent.clear_memory()

        assert len(agent.memory.chat_memory.messages) == 0

    def test_get_mcp_status_info(self, agent):
        """Test getting MCP status information"""
        status = agent.get_mcp_status_info()

        assert isinstance(status, dict)
        assert 'enabled' in status
        assert 'status' in status
        assert 'servers' in status
        assert status['enabled'] == agent.mcp_enabled


@pytest.mark.skipif(not TEST_API_KEY or TEST_API_KEY == 'test_key_for_mocking',
                    reason="Requires valid OPENROUTER_API_KEY for integration tests")
class TestStreamingIntegration:
    """Integration tests for streaming with real API calls"""

    @pytest.fixture
    def live_agent(self):
        """Create agent with real API key"""
        agent = KraftbotAgent(
            model_name=TEST_MODEL,
            api_key=TEST_API_KEY,
            system_prompt=TEST_PROMPT,
            mcp_enabled=True,
            verbose=False
        )
        return agent

    @pytest.mark.asyncio
    async def test_non_streaming_response(self, live_agent):
        """Test non-streaming chat response"""
        await live_agent.initialize()

        response = await live_agent.chat("Say 'Hello, this is a test'")

        assert isinstance(response, AgentResponse)
        assert response.content is not None
        assert len(response.content) > 0
        assert response.response_time > 0
        assert isinstance(response.tokens, dict)
        assert 'input_tokens' in response.tokens
        assert 'output_tokens' in response.tokens

    @pytest.mark.asyncio
    async def test_streaming_response(self, live_agent):
        """Test streaming chat response"""
        await live_agent.initialize()

        chunks = []
        async for chunk in live_agent.chat_stream("Say 'Hello, streaming test'"):
            chunks.append(chunk)

        # Verify we got streaming chunks
        assert len(chunks) > 0

        # Verify full response was assembled
        full_response = "".join(chunks)
        assert len(full_response) > 0

        # Verify memory was updated
        assert len(live_agent.memory.chat_memory.messages) == 2  # User + AI

    @pytest.mark.asyncio
    async def test_streaming_with_mcp_enabled(self, live_agent):
        """Test that streaming works with MCP enabled"""
        await live_agent.initialize()

        # Get MCP status
        mcp_status = live_agent.mcp_manager.get_mcp_status()

        # Stream a response
        chunks = []
        async for chunk in live_agent.chat_stream("What is 2+2?"):
            chunks.append(chunk)

        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0

        # Verify MCP didn't interfere with streaming
        assert "Error" not in full_response or "streaming" not in full_response.lower()

    @pytest.mark.asyncio
    async def test_alternating_streaming_and_normal(self, live_agent):
        """Test alternating between streaming and non-streaming modes"""
        await live_agent.initialize()

        # Non-streaming request
        response1 = await live_agent.chat("Count to 3")
        assert response1.content is not None

        # Streaming request
        chunks = []
        async for chunk in live_agent.chat_stream("What comes after 3?"):
            chunks.append(chunk)
        assert len(chunks) > 0

        # Another non-streaming request
        response2 = await live_agent.chat("What comes after 4?")
        assert response2.content is not None

        # Verify memory has all interactions
        assert len(live_agent.memory.chat_memory.messages) == 6  # 3 user + 3 AI


class TestMCPAndStreamingCombination:
    """Tests specifically for MCP and streaming working together"""

    @pytest.fixture
    def agent_with_mcp(self):
        """Agent with MCP enabled"""
        agent = KraftbotAgent(
            model_name=TEST_MODEL,
            api_key=TEST_API_KEY,
            system_prompt=TEST_PROMPT,
            mcp_enabled=True,
            verbose=False
        )
        return agent

    @pytest.mark.asyncio
    async def test_mcp_info_in_streaming_context(self, agent_with_mcp):
        """Test that MCP info is available during streaming"""
        await agent_with_mcp.initialize()

        # Check MCP status before streaming
        initial_status = agent_with_mcp.get_mcp_status_info()

        # Mock streaming to avoid API calls
        with patch.object(agent_with_mcp, 'streaming_llm') as mock_llm:
            # Setup mock to yield chunks
            async def mock_astream(*args, **kwargs):
                class MockChunk:
                    def __init__(self, content):
                        self.content = content

                for chunk in ["Hello", " ", "World"]:
                    yield MockChunk(chunk)

            mock_llm.astream = mock_astream

            # Stream a response
            chunks = []
            async for chunk in agent_with_mcp.chat_stream("Test"):
                chunks.append(chunk)

            # Check MCP status after streaming
            final_status = agent_with_mcp.get_mcp_status_info()

            # MCP status should be consistent
            assert initial_status['enabled'] == final_status['enabled']

    @pytest.mark.asyncio
    async def test_system_prompt_includes_mcp_tools(self, agent_with_mcp):
        """Test that system prompt includes MCP tools when available"""
        await agent_with_mcp.initialize()

        # If MCP is connected, system prompt should mention tools
        if agent_with_mcp.mcp_manager.is_connected():
            assert "MCP Tools" in agent_with_mcp.system_prompt or "tools" in agent_with_mcp.system_prompt.lower()

    def test_mcp_disabled_agent_has_no_tools(self):
        """Test that agent with MCP disabled doesn't include tool info"""
        agent = KraftbotAgent(
            model_name=TEST_MODEL,
            api_key=TEST_API_KEY,
            system_prompt=TEST_PROMPT,
            mcp_enabled=False,
            verbose=False
        )

        status = agent.get_mcp_status_info()
        assert status['enabled'] is False
        assert len(status['servers']) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
