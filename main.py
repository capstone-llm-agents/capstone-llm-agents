"""Main entry point for the capstone-llm-agents project."""

from components.agents.calendar_agent import CALENDAR_AGENT
from components.agents.example_agent import EXAMPLE_AGENT
from components.agents.travel_planner_agent import TRAVEL_PLANNER_AGENT
from components.agents.websearch_agent import WEBSEARCH_AGENT
from llm_mas.client.account.client import Client
from llm_mas.client.ui.textual_app.app import TextualApp
from llm_mas.mas.mas import MAS
from llm_mas.mcp_client.client import MCPClient
from llm_mas.mcp_client.connected_server import SSEConnectedServer


def main() -> None:
    """Run the main application logic."""
    mas = MAS()

    mas.add_agent(CALENDAR_AGENT)

    mas.add_agent(EXAMPLE_AGENT)

    mas.add_agent(TRAVEL_PLANNER_AGENT)
    mas.add_agent(WEBSEARCH_AGENT)

    # TODO: remove this test conversation  # noqa: TD003
    mas.conversation_manager.start_conversation("AgentToAgentChat")

    agent_to_agent_conversation = mas.conversation_manager.get_conversation("AgentToAgentChat")

    agent1 = TRAVEL_PLANNER_AGENT
    agent2 = CALENDAR_AGENT
    agent3 = EXAMPLE_AGENT

    agent_to_agent_conversation.add_message(
        agent1,
        content="Hello, I am planning a trip and need to schedule some events. Can you help me with that?",
    )
    agent_to_agent_conversation.add_message(
        agent2,
        content="Sure! I can help you schedule events. What dates are you looking at for your trip?",
    )
    agent_to_agent_conversation.add_message(agent1, content="I'm looking at traveling from June 10th to June 20th.")

    mas.conversation_manager.start_conversation("DefaultChat")

    mcp_client = MCPClient()
    server = SSEConnectedServer("http://localhost:8080/sse")
    mcp_client.add_connected_server(server)
    server = SSEConnectedServer("http://localhost:8081/sse")
    mcp_client.add_connected_server(server)
    client = Client("Test User", mas, mcp_client)

    # user
    user = client.user

    # friendships
    user.add_friend(agent3)
    agent3.add_friend(agent2)

    app = TextualApp(client)
    app.run()


if __name__ == "__main__":
    main()
