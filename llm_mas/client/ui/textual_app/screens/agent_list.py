"""The agent list screen of the textual app."""

from textual import events
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from llm_mas.client.account.client import Client


class AgentListScreen(Screen):
    """Screen to display a list of agents."""

    def __init__(self, client: Client) -> None:
        """Initialize the agent list screen with a client."""
        super().__init__()
        self.client = client

    def compose(self) -> ComposeResult:
        """Compose the agent list layout."""
        yield Header(name="Agent List")
        agents: list[str] = [agent.name for agent in self.client.get_mas().get_agents()]
        content: str = "\n".join(agents)
        yield Static(content)
        yield Footer()

    def on_key(self, event: events.Key) -> None:
        """Handle key events for navigation."""
        if event.key == "escape":
            self.app.pop_screen()
