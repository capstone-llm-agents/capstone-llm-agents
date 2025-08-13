"""Test script to check that the MCP server can be connected to and used via SSE."""

import asyncio

from mcp import ClientSession
from mcp.client.sse import sse_client
from pydantic import AnyUrl


async def main() -> None:
    """Run the main client script."""
    server_url = "http://localhost:8080/sse"

    async with sse_client(url=server_url) as streams:  # noqa: SIM117
        async with ClientSession(read_stream=streams[0], write_stream=streams[1]) as session:
            print("Initializing session...")
            await session.initialize()

            # list available tools
            response = await session.list_tools()
            print("Available tools:", [tool.name for tool in response.tools])

            # list resources
            resources = await session.list_resources()
            print("Resources:", resources)

            # call tool
            result = await session.call_tool("greet", {"name": "Alice"})
            print("Greeting result:", result.content)

            # get "hello" resource
            hello_resource = await session.read_resource(AnyUrl("resource://hello"))
            print("Hello resource content:", hello_resource.contents)


if __name__ == "__main__":
    asyncio.run(main())
