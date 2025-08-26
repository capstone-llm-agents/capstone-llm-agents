"""Tool manager for managing and retrieving tools."""

from mcp import Tool
from mcp.types import ContentBlock

from llm_mas.mcp_client.connected_server import ConnectedServer
from llm_mas.tools.tool_narrower import ToolNarrower


class ToolManager:
    """Manager class for handling tools."""

    def __init__(self, narrower: ToolNarrower) -> None:
        """Initialize the tool manager."""
        self.tools: dict[str, tuple[Tool, ConnectedServer]] = {}
        self.connected_servers: set[ConnectedServer] = set()
        self.narrower = narrower

    def is_known_server(self, server: ConnectedServer) -> bool:
        """Check if the server is known."""
        return server in self.connected_servers

    def add_tool(self, tool: Tool, server: ConnectedServer) -> None:
        """Add a tool to the manager."""
        if tool.name in self.tools:
            msg = f"Tool '{tool.name}' already exists."
            raise ValueError(msg)
        self.tools[tool.name] = (tool, server)
        self.connected_servers.add(server)

    async def call_tool(self, tool_name: str, params: dict) -> list[ContentBlock]:
        """Call a tool with the given parameters."""
        if tool_name not in self.tools:
            msg = f"Tool '{tool_name}' does not exist."
            raise ValueError(msg)

        tool, server = self.tools[tool_name]
        async with server.connect() as session:
            await session.initialize()
            return await server.call_tool(session, tool_name, params)

    async def init_tools_from_server(self, server: ConnectedServer) -> None:
        """Initialize a new server and add its tools."""
        if self.is_known_server(server):
            return

        async with server.connect() as session:
            await session.initialize()
            tools = await server.list_tools(session)
            for tool in tools:
                self.add_tool(tool, server)

        self.connected_servers.add(server)

    def get_tools_from_server(self, server: ConnectedServer) -> list[Tool]:
        """Get all tools from a specific server."""
        if not self.is_known_server(server):
            return []

        return [tool for tool, srv in self.tools.values() if srv == server]

    def get_all_tools(self) -> list[Tool]:
        """Get all tools managed by the tool manager."""
        return [tool for tool, _ in self.tools.values()]
