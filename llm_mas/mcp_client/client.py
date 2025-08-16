"""The MCP client module provides a client for interacting with many MCP servers."""

from llm_mas.mcp_client.connected_server import ConnectedServer


class MCPClient:
    """A client for interacting with MCP servers."""

    def __init__(self) -> None:
        """Initialize the MCP client."""
        self.connected_servers: list[ConnectedServer] = []

    def add_connected_server(self, server: ConnectedServer) -> None:
        """Add a connected server to the MCP client."""
        self.connected_servers.append(server)
