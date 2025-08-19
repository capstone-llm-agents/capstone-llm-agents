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

            # call callender creation tool
            ics_file = "my_callender.ics"
            result = await session.call_tool("create_ics_callender", {"tasks": "Maths at 10am for two hours, english at 6pm for 1 hour and history at 12pm tommorow", "ics_file": ics_file})
            print("Callender creation result:", result.content)

            # call callender reading tool
            ics_file_read = "my_callender.ics"
            result = await session.call_tool("read_calender", {"file_name": ics_file_read})
            print("Read callender output:", result.content)

            # call callender read and creation tool
            ics_file1 = "my_callender.ics"
            ics_file2 = "my_callender_reformatted.ics"
            result = await session.call_tool("create_ics_callender_with_context", {"tasks": "Between maths and english book me a 1 hour meeting with Anton.", "file_name_read": ics_file1, "file_name_write": ics_file2})
            print("Reformeted callender creation result:", result.content)




if __name__ == "__main__":
    asyncio.run(main())
