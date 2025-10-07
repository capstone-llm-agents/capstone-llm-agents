"""Main entry point for the PyQt6 LLM MAS application."""

from llm_mas.client.account.client import Client
from llm_mas.client.ui.pyqt.app import run_app
from llm_mas.mas.mas import MAS
from llm_mas.mcp_client.client import MCPClient
from llm_mas.mcp_client.connected_server import SSEConnectedServer
from components.agents.example_agent import ASSISTANT_AGENT
from components.agents.calendar_agent import CALENDAR_AGENT
from components.agents.weather_agent import WEATHER_AGENT
#from components.agents.travel_planner_agent import TRAVEL_PLANNER_AGENT
from components.agents.websearch_agent import WEBSEARCH_AGENT


def main():
    # Initialize MAS
    mas = MAS()
    mas.add_agent(ASSISTANT_AGENT)
    mas.add_agent(CALENDAR_AGENT)
    mas.add_agent(WEATHER_AGENT)
    #mas.add_agent(TRAVEL_PLANNER_AGENT)
    mas.add_agent(WEBSEARCH_AGENT)

    # MCP client
    mcp_client = MCPClient()
    server1 = SSEConnectedServer("http://localhost:8080/sse")
    server2 = SSEConnectedServer("http://localhost:8081/sse")
    mcp_client.add_connected_server(server1)
    mcp_client.add_connected_server(server2)

    # Create client
    client = Client("Test User", mas, mcp_client)

    # Setup friendships
    user = client.user
    user.add_friend(ASSISTANT_AGENT)
    ASSISTANT_AGENT.add_friend(WEATHER_AGENT)
    ASSISTANT_AGENT.add_friend(CALENDAR_AGENT)
    #ASSISTANT_AGENT.add_friend(TRAVEL_PLANNER_AGENT)
    ASSISTANT_AGENT.add_friend(WEBSEARCH_AGENT)


    # AGENT NETWORK SCREEN TEST just for more connections

    CALENDAR_AGENT.add_friend(WEATHER_AGENT)

    # Run PyQt6 app
    run_app(client)


if __name__ == "__main__":
    main()
