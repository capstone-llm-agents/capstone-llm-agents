"""Test script to check that the MCP server can be connected to and used via SSE."""

import asyncio

from mcp import ClientSession
from mcp.client.sse import sse_client
from pydantic import AnyUrl

async def main() -> None:
    """Run the main client script."""
    server_url = "http://localhost:8082/sse"

    async with sse_client(url=server_url) as streams:  # noqa: SIM117
        async with ClientSession(read_stream=streams[0], write_stream=streams[1]) as session:
            print("Initializing session...")
            await session.initialize()

            # list available tools
            response = await session.list_tools()
            print("Available tools:", [tool.name for tool in response.tools])

            # call weather tool
            result = await session.call_tool("create_pdf_file", {"prompt": "I plan to go to the beach tomorrow morning, have lunch at the fish and chips shop as well as go to the movies at night. can you put my schedule into a pdf file?"})
            print("Weather creation result:", result)




if __name__ == "__main__":
    asyncio.run(main())
