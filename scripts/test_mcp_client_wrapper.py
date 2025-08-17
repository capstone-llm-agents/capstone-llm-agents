"""The test client wrapper script connects to an MCP server using SSE and performs various operations."""

import asyncio

from llm_mas.mcp_client.connected_server import SSEConnectedServer

server = SSEConnectedServer("http://localhost:8080/sse")


async def main() -> None:
    """Run the main client script."""
    async with server.connect() as session:
        tools = await server.list_tools(session)
        print("Available tools:", [tool.name for tool in tools])

        resources = await server.list_resources(session)
        print("Resources:", resources)

        result = await server.call_tool(session, "greet", {"name": "Alice"})
        print("Greeting result:", result[0] if result else "No content")

        hello_resource = await server.read_resource(session, "resource://hello")
        print("Hello resource content:", hello_resource[0] if hello_resource else "No content")


if __name__ == "__main__":
    asyncio.run(main())
