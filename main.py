"""Main entry point for the capstone-llm-agents project."""

from components.agents.example_agent import EXAMPLE_AGENT
from components.agents.websearch_agent import WEBSEARCH_AGENT
from llm_mas.client.account.client import Client
from llm_mas.client.ui.textual_app.app import TextualApp
from llm_mas.mas.mas import MAS
from llm_mas.mcp_client.client import MCPClient
from llm_mas.mcp_client.connected_server import SSEConnectedServer


def main() -> None:
    """Run the main application logic."""
    mas = MAS()

    mas.add_agent(WEBSEARCH_AGENT)
    mas.add_agent(EXAMPLE_AGENT)

    mas.conversation_manager.start_conversation("General")

    mcp_client = MCPClient()
    server = SSEConnectedServer("http://localhost:8080/sse")
    mcp_client.add_connected_server(server)
    client = Client("Test User", mas, mcp_client)
    app = TextualApp(client)
    app.run()


if __name__ == "__main__":
    main()
