"""The connected server module provides a simple API to a dedicated MCP server instance."""

from abc import abstractmethod
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from mcp import ClientSession, Implementation, Resource, Tool
from mcp.client.sse import sse_client
from mcp.types import BlobResourceContents, ContentBlock, TextResourceContents
from pydantic import AnyUrl


class ConnectedServer:
    """A class to manage a connection to an MCP server."""

    def __init__(self, server_url: str) -> None:
        """Initialize the connected server with the given URL."""
        self.server_url = server_url

    async def list_tools(self, session: ClientSession) -> list[Tool]:
        """List available tools on the MCP server."""
        response = await session.list_tools()
        return response.tools

    async def list_resources(self, session: ClientSession) -> list[Resource]:
        """List available resources on the MCP server."""
        response = await session.list_resources()
        return response.resources

    async def call_tool(self, session: ClientSession, tool_name: str, params: dict) -> list[ContentBlock]:
        """Call a tool on the MCP server."""
        res = await session.call_tool(tool_name, params)

        if res.isError:
            msg = f"Error calling tool {tool_name}"
            raise RuntimeError(msg)

        return res.content

    async def read_resource(
        self,
        session: ClientSession,
        resource_uri: AnyUrl | str,
    ) -> list[TextResourceContents | BlobResourceContents]:
        """Read a resource from the MCP server."""
        if isinstance(resource_uri, str):
            resource_uri = AnyUrl(resource_uri)

        res = await session.read_resource(resource_uri)
        return res.contents

    async def initialize(self, session: ClientSession) -> Implementation:
        """Initialize the connected server."""
        res = await session.initialize()
        return res.serverInfo

    @abstractmethod
    @asynccontextmanager
    async def connect(self) -> AsyncGenerator[ClientSession]:
        """Connect to the MCP server and return a session."""
        msg = "Subclasses must implement the connect method."
        raise NotImplementedError(msg)
        yield


class SSEConnectedServer(ConnectedServer):
    """A class to manage a connection to an MCP server using Server-Sent Events (SSE)."""

    def __init__(self, server_url: str) -> None:
        """Initialize the SSE connected server with the given URL."""
        super().__init__(server_url)

    @asynccontextmanager
    async def connect(self) -> AsyncGenerator[ClientSession]:
        """Connect to the MCP server using SSE."""
        try:
            async with sse_client(url=self.server_url) as streams:  # noqa: SIM117
                async with ClientSession(read_stream=streams[0], write_stream=streams[1]) as session:
                    yield session
        except Exception as e:
            msg = f"Failed to connect to the server at {self.server_url} - {e}"
            raise ConnectionError(msg) from e
