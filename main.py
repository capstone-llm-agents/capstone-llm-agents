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
from llm_mas.utils.config import ConfigManager


def main() -> None:
    """Run the main application logic."""
    mas = MAS()

    mas.add_agent(EXAMPLE_AGENT)
    mas.add_agent(CALENDAR_AGENT)
    mas.add_agent(TRAVEL_PLANNER_AGENT)
    mas.add_agent(WEBSEARCH_AGENT)

    agent1 = TRAVEL_PLANNER_AGENT
    agent2 = CALENDAR_AGENT
    agent3 = EXAMPLE_AGENT

    mcp_client = MCPClient()
    mcp_client.add_connected_server(SSEConnectedServer("http://localhost:8080/sse"))
    mcp_client.add_connected_server(SSEConnectedServer("http://localhost:8081/sse"))

    config = None
    try:
        config = ConfigManager("./data/config.yaml")
    except Exception as e:
        msg = f"Failed to initialize configuration manager. {e} \n\n Please update or create a valid `config.yaml` file. You can run `python setup.py` to create the config via a CLI."  # noqa: E501
        raise RuntimeError(msg) from e

    client = Client("Test User", mas, mcp_client, config)

    # user
    user = client.user

    # friendships
    user.add_friend(agent3)
    agent3.add_friend(agent2)
    agent3.add_friend(agent1)

    app = TextualApp(client)
    app.run()


if __name__ == "__main__":
    main()
