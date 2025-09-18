"""
KraftBot - Advanced PydanticAI Agent with OpenRouter & MCP Support

A powerful AI agent framework that combines PydanticAI with OpenRouter for multi-model
access and Model Context Protocol (MCP) for external tool integration.
"""

__version__ = "1.0.0"
__author__ = "KraftBot Team"
__email__ = "kraftbot@example.com"

from .core.agent import PydanticAIAgent
from .core.models import AgentResponse, AgentDependencies
from .config.settings import Settings

__all__ = [
    "PydanticAIAgent",
    "AgentResponse", 
    "AgentDependencies",
    "Settings",
    "__version__",
]