"""
Simplified KraftBot agent implementation.
"""

import asyncio
import time

# Apply compatibility patch for PydanticAI
from contextlib import nullcontext
from typing import Optional

if not hasattr(asyncio, "nullcontext"):
    asyncio.nullcontext = nullcontext

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

from ..config.settings import settings
from ..mcp.manager import MCPManager
from .models import AgentResponse
from .observability import LogfireConfig


class PydanticAIAgent:
    """
    Simplified KraftBot agent with minimal complexity
    """

    def __init__(
        self,
        openrouter_api_key: str,
        model_name: str = "anthropic/claude-3.5-sonnet",
        system_prompt: Optional[str] = None,
        enable_logfire: bool = True,
    ):
        """
        Initialize the agent with OpenRouter provider
        """
        self.openrouter_api_key = openrouter_api_key
        self.model_name = model_name

        # Initialize Logfire if enabled
        self.logfire = None
        if enable_logfire:
            try:
                self.logfire = LogfireConfig(
                    service_name="kraftbot-simplified", service_version="1.0.0"
                )
            except Exception as e:
                print(f"⚠️  Logfire initialization failed: {e}")

        # Initialize MCP manager and load servers
        self.mcp_manager = MCPManager()
        self._initialize_mcp_servers()

        # Configure the OpenRouter model
        self.model = OpenAIChatModel(
            model_name,
            provider=OpenRouterProvider(api_key=openrouter_api_key),
        )

        # Use default system prompt if none provided
        if not system_prompt:
            system_prompt = f"""You are KraftBot, an elite fantasy football strategist for manager {settings.default_manager_name} in league {settings.default_league_id}.

Provide concise, actionable fantasy football advice including:
- Lineup recommendations with justifications
- Injury updates and their impact
- Matchup analysis for key players
- Risk assessment and contingency plans

Format responses clearly with bullet points."""

        # Create the simple agent with MCP tools
        self.agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            toolsets=self.mcp_manager.get_servers(),
            retries=0,
        )

    def _initialize_mcp_servers(self):
        """Initialize MCP servers based on configuration"""
        if settings.enable_mcp_server:
            try:
                # Configure tokenbowl-mcp SSE server
                self.mcp_manager.add_sse_server(
                    url="https://tokenbowl-mcp.haihai.ai/sse",
                    tool_prefix="tokenbowl",
                    name="tokenbowl_mcp",
                )
                if settings.verbose_logging:
                    print(
                        f"✅ Loaded MCP SSE server: tokenbowl-mcp at https://tokenbowl-mcp.haihai.ai/sse"
                    )
            except Exception as e:
                if settings.verbose_logging:
                    print(f"⚠️  Failed to load MCP server: {e}")

    async def run(
        self, prompt: str, user_id: str = "user", session_id: str = "default"
    ) -> AgentResponse:
        """
        Run the agent with a given prompt - let Logfire handle all observability automatically
        """
        try:
            result = await self.agent.run(prompt)

            # Handle potential method vs property issue with result.output
            output_text = result.output
            if callable(output_text):
                output_text = output_text()

            return AgentResponse(response=str(output_text))

        except Exception as e:
            # Provide more helpful error messages
            error_msg = str(e)
            if "finish_reason" in error_msg and "error" in error_msg:
                error_msg = "API Error: The model service returned an error response. This could be due to API limits, model availability, or service issues. Please try again or use a different model."
            elif "validation error" in error_msg.lower():
                error_msg = f"API Response Error: {error_msg}"
            elif "api key" in error_msg.lower():
                error_msg = "API Key Error: Please check your OpenRouter API key is valid and has sufficient credits."

            return AgentResponse(response=f"Error: {error_msg}")

    async def run_stream(
        self, prompt: str, user_id: str = "user", session_id: str = "default"
    ):
        """
        Run the agent with streaming output
        """
        try:
            async with self.agent.run_stream(prompt) as stream:
                async for token in stream:
                    yield token
        except Exception as e:
            # Provide more helpful error messages
            error_msg = str(e)
            if "finish_reason" in error_msg and "error" in error_msg:
                error_msg = "API Error: The model service returned an error response. This could be due to API limits, model availability, or service issues. Please try again or use a different model."
            elif "validation error" in error_msg.lower():
                error_msg = f"API Response Error: {error_msg}"
            elif "api key" in error_msg.lower():
                error_msg = "API Key Error: Please check your OpenRouter API key is valid and has sufficient credits."

            yield f"Error: {error_msg}"
