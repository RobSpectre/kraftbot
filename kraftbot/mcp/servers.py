"""
MCP server configurations and utilities.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class MCPTransportType(str, Enum):
    """MCP server transport types"""

    STDIO = "stdio"
    SSE = "sse"
    HTTP = "http"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""

    name: str
    transport_type: MCPTransportType
    tool_prefix: Optional[str] = None

    # STDIO specific
    command: Optional[str] = None
    args: Optional[List[str]] = None

    # HTTP/SSE specific
    url: Optional[str] = None

    # Additional options
    timeout: int = 30
    allow_sampling: bool = True

    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.transport_type == MCPTransportType.STDIO:
            if not self.command:
                raise ValueError("STDIO transport requires 'command'")
        elif self.transport_type in (MCPTransportType.SSE, MCPTransportType.HTTP):
            if not self.url:
                raise ValueError(f"{self.transport_type} transport requires 'url'")


class MCPServerInfo(BaseModel):
    """Information about a connected MCP server"""

    name: str
    transport_type: str
    tool_prefix: Optional[str]
    status: str  # "connected", "disconnected", "error"
    tools_count: int
    last_used: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        """Pydantic configuration"""

        use_enum_values = True
