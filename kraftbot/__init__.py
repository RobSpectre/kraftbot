"""
Kraftbot - Fantasy Football AI Assistant

A Langchain-based conversational AI agent for fantasy football assistance with
OpenRouter integration, MCP server support, and comprehensive token tracking.
"""

__version__ = "1.0.0"
__author__ = "Kraftbot Team"

from kraftbot.core.agent import KraftbotAgent
from kraftbot.core.models import TokenCounter, AgentResponse

__all__ = ["KraftbotAgent", "TokenCounter", "AgentResponse"]
