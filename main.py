"""Main entry point for the capstone-llm-agents project."""

import asyncio

from components.agents.assistant_agent import ASSISTANT_AGENT
from components.agents.calendar_agent import CALENDAR_AGENT
from components.agents.travel_planner_agent import TRAVEL_PLANNER_AGENT
from components.agents.weather_agent import WEATHER_AGENT
from components.agents.websearch_agent import WEBSEARCH_AGENT
from llm_mas.client.account.client import Client
from llm_mas.client.ui.textual_app.app import TextualApp
from llm_mas.mas.mas import MAS
from llm_mas.mcp_client.client import MCPClient
from llm_mas.mcp_client.connected_server import SSEConnectedServer
from llm_mas.utils.config.general_config import GeneralConfig


def main() -> None:
    """Run the main application logic."""
    mas = MAS()

    mas.add_agent(ASSISTANT_AGENT)
    mas.add_agent(TRAVEL_PLANNER_AGENT)
    mas.add_agent(CALENDAR_AGENT)
    mas.add_agent(WEATHER_AGENT)
    mas.add_agent(WEBSEARCH_AGENT)

    mcp_client = MCPClient()
    mcp_client.add_connected_server(SSEConnectedServer("http://localhost:8080/sse"))
    mcp_client.add_connected_server(SSEConnectedServer("http://localhost:8081/sse"))

    config = None
    try:
        config = GeneralConfig("./config/models.yaml", "./config/vector.yaml")
    except Exception as e:
        msg = f"Failed to initialize configuration manager. {e} \n\n Please update or create the valid configuration files. It is recommended to run `python init_config.py` to create the config via a CLI."  # noqa: E501
        raise RuntimeError(msg) from e

    client = Client("Test User", mas, mcp_client, config)

    # user
    user = client.user

    # friendships
    user.add_friend(ASSISTANT_AGENT)
    ASSISTANT_AGENT.add_friend(WEATHER_AGENT)
    ASSISTANT_AGENT.add_friend(CALENDAR_AGENT)
    ASSISTANT_AGENT.add_friend(TRAVEL_PLANNER_AGENT)
    ASSISTANT_AGENT.add_friend(WEBSEARCH_AGENT)

    app = TextualApp(client)
    app.run()

    # shutdown
    asyncio.run(app.on_shutdown())


if __name__ == "__main__":
    main()
