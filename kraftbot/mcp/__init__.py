"""
Model Context Protocol (MCP) integration for KraftBot.
"""

from .manager import MCPManager
from .servers import MCPServerConfig

__all__ = [
    "MCPManager",
    "MCPServerConfig",
]