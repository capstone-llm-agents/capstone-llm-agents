"""The test script creates the basic Client and connects to an MCP server."""

import asyncio

from components.actions.retrieve_knowledge import RetrieveKnowledge
from components.actions.simple_response import SimpleResponse
from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.base.narrowers.graph_narrower import GraphBasedNarrower
from llm_mas.action_system.base.selectors.llm_selector import LLMSelector
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.client.account.client import Client
from llm_mas.mas.agent import Agent
from llm_mas.mas.mas import MAS
from llm_mas.mcp_client.client import MCPClient
from llm_mas.mcp_client.connected_server import SSEConnectedServer
from llm_mas.model_providers.ollama.call_llm import call_llm
from llm_mas.tools.tool_action_creator import DefaultToolActionCreator
from llm_mas.tools.tool_manager import ToolManager
from llm_mas.tools.tool_narrower import DefaultToolNarrower

action_space = ActionSpace()
narrower = GraphBasedNarrower()
selector = LLMSelector(call_llm)

# tools
tool_narrower = DefaultToolNarrower()
tool_creator = DefaultToolActionCreator()
tool_manager = ToolManager(
    tool_narrower,
)

agent = Agent("TestAgent", action_space, narrower, selector, tool_manager)

# add some actions
agent.add_action(SimpleResponse())
agent.add_action(StopAction())
agent.add_action(RetrieveKnowledge())


narrower.add_default_action(SimpleResponse())
narrower.add_default_action(RetrieveKnowledge())

# add some edges
narrower.add_action_edge(RetrieveKnowledge(), [SimpleResponse()])
narrower.add_action_edge(SimpleResponse(), [StopAction()])

mas = MAS()
mas.add_agent(agent)

mcp_client = MCPClient()

test_server = SSEConnectedServer("http://localhost:8080/sse")

client = Client("Test User", mas, mcp_client)


def print_to_console(*args, **kwargs):  # noqa: ANN002, ANN003, ANN201
    """Print messages to the console."""
    print(*args, **kwargs)  # noqa: T201


async def main() -> None:
    """Run the main client script."""
    print_to_console(f"Client username: {client.get_username()}")
    print_to_console(f"MAS instance: {client.get_mas()}")

    async with test_server.connect() as session:
        # List available tools
        tools = await test_server.list_tools(session)
        print_to_console("Available tools:", [tool.name for tool in tools])

        # List resources
        resources = await test_server.list_resources(session)
        print_to_console("Resources:", resources)

        # Call tool
        result = await test_server.call_tool(session, "greet", {"name": "Alice"})
        print_to_console("Greeting result:", result[0] if result else "No content")

        # Get "hello" resource
        hello_resource = await test_server.read_resource(session, "resource://hello")
        print_to_console("Hello resource content:", hello_resource[0] if hello_resource else "No content")


if __name__ == "__main__":
    asyncio.run(main())
