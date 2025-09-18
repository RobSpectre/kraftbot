"""
MCP server manager for handling multiple MCP server connections.
"""

from typing import Any, Dict, List, Optional

from pydantic_ai.mcp import MCPServerSSE, MCPServerStdio

from .servers import MCPServerConfig, MCPServerInfo, MCPTransportType


class MCPManager:
    """Manager for MCP server connections and lifecycle"""

    def __init__(self):
        """Initialize the MCP manager"""
        self._servers: Dict[str, Any] = {}
        self._configs: Dict[str, MCPServerConfig] = {}

    def add_stdio_server(
        self,
        command: str,
        args: List[str],
        tool_prefix: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Add an MCP server using STDIO transport

        Args:
            command: Command to run the server
            args: Arguments for the command
            tool_prefix: Optional prefix for tool names to avoid conflicts
            name: Optional name for the server (auto-generated if not provided)
            **kwargs: Additional configuration options

        Returns:
            str: Server name/identifier
        """
        server_name = name or f"stdio_{command.replace('/', '_')}"

        config = MCPServerConfig(
            name=server_name,
            transport_type=MCPTransportType.STDIO,
            command=command,
            args=args,
            tool_prefix=tool_prefix,
            **kwargs,
        )

        server = MCPServerStdio(
            command=command,
            args=args,
            tool_prefix=tool_prefix,
            allow_sampling=config.allow_sampling,
        )

        self._servers[server_name] = server
        self._configs[server_name] = config

        return server_name

    def add_sse_server(
        self,
        url: str,
        tool_prefix: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Add an MCP server using Server-Sent Events (SSE) transport

        Args:
            url: URL of the SSE server
            tool_prefix: Optional prefix for tool names to avoid conflicts
            name: Optional name for the server (auto-generated if not provided)
            **kwargs: Additional configuration options

        Returns:
            str: Server name/identifier
        """
        server_name = (
            name or f"sse_{url.split('//')[-1].replace('/', '_').replace(':', '_')}"
        )

        config = MCPServerConfig(
            name=server_name,
            transport_type=MCPTransportType.SSE,
            url=url,
            tool_prefix=tool_prefix,
            **kwargs,
        )

        server = MCPServerSSE(url=url, tool_prefix=tool_prefix)

        self._servers[server_name] = server
        self._configs[server_name] = config

        return server_name

    def remove_server(self, name: str) -> bool:
        """
        Remove an MCP server

        Args:
            name: Name of the server to remove

        Returns:
            bool: True if server was removed, False if not found
        """
        if name in self._servers:
            del self._servers[name]
            del self._configs[name]
            return True
        return False

    def get_servers(self) -> List[Any]:
        """Get list of all server instances for PydanticAI agent"""
        return list(self._servers.values())

    def get_server_names(self) -> List[str]:
        """Get list of all server names"""
        return list(self._servers.keys())

    def get_server_info(self, name: str) -> Optional[MCPServerInfo]:
        """Get information about a specific server"""
        if name not in self._servers:
            return None

        config = self._configs[name]

        return MCPServerInfo(
            name=config.name,
            transport_type=config.transport_type.value,
            tool_prefix=config.tool_prefix,
            status="connected",  # TODO: Implement actual status checking
            tools_count=0,  # TODO: Implement tool counting
        )

    def get_all_server_info(self) -> List[MCPServerInfo]:
        """Get information about all servers"""
        return [self.get_server_info(name) for name in self._servers.keys()]

    def get_available_tools(self) -> List[str]:
        """Get list of all available tools from all servers"""
        # TODO: Implement actual tool discovery from MCP servers
        tools = []
        for name, config in self._configs.items():
            prefix = config.tool_prefix or ""
            # This is a placeholder - in reality we'd query the server for its tools
            tools.append(f"{prefix}_example_tool" if prefix else "example_tool")
        return tools

    def get_server_by_name(self, name: str) -> Optional[Any]:
        """Get server instance by name"""
        return self._servers.get(name)

    def clear_all_servers(self):
        """Remove all servers"""
        self._servers.clear()
        self._configs.clear()

    def __len__(self) -> int:
        """Get number of connected servers"""
        return len(self._servers)

    def __contains__(self, name: str) -> bool:
        """Check if server exists"""
        return name in self._servers
