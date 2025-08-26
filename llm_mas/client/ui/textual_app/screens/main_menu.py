"""The main menu screen of the textual app."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header

from llm_mas.client.account.client import Client
from llm_mas.client.ui.textual_app.screens.agent_list import AgentListScreen
from llm_mas.client.ui.textual_app.screens.chat_screen import ChatScreen
from llm_mas.client.ui.textual_app.screens.mcp_client import MCPClientScreen


class MainMenu(Screen):
    """Main menu screen of the application."""

    def __init__(self, client: Client) -> None:
        """Initialize the main menu with a client."""
        super().__init__()
        self.client = client

    def compose(self) -> ComposeResult:
        """Compose the main menu layout."""
        yield Header(show_clock=True)
        with Vertical():
            yield Button("Talk to Assistant Agent", id="talk_agent")
            yield Button("MCP Client Info", id="mcp_client_info")
            yield Button("List Agents", id="list_agents")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses to navigate to different screens."""
        if event.button.id == "list_agents":
            self.app.push_screen(AgentListScreen(self.client))
        elif event.button.id == "talk_agent":
            self.app.push_screen(ChatScreen(self.client))
        elif event.button.id == "mcp_client_info":
            self.app.push_screen(MCPClientScreen(self.client))
