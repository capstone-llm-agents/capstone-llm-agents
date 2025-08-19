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

            # call tool
            result = await session.call_tool("create_ics_callender", {"tasks": "Maths at 10am for two hours, english at 6pm for 1 hour and history at 12pm tommorow"})
            print("Callender creation result:", result.content)




if __name__ == "__main__":
    asyncio.run(main())
