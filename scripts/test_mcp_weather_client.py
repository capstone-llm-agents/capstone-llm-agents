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

            # call weather tool
            result = await session.call_tool("obtain_weather_details", {"prompt": "What is the weather in Pakenham victoria tomorrow at 3pm as well as what will the weather be in paris on the 4th of september 2025."})
            print("Weather creation result:", result)




if __name__ == "__main__":
    asyncio.run(main())
