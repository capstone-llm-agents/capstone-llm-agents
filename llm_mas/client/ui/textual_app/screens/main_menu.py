"""The main menu screen of the textual app."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header

from components.agents.calendar_agent import CALENDAR_AGENT
from components.agents.travel_planner_agent import TRAVEL_PLANNER_AGENT
from llm_mas.client.account.client import Client
from llm_mas.client.ui.textual_app.screens.agent_chat_screen import AgentChatScreen
from llm_mas.client.ui.textual_app.screens.agent_list import AgentListScreen
from llm_mas.client.ui.textual_app.screens.mcp_client import MCPClientScreen
from llm_mas.client.ui.textual_app.screens.user_chat_screen import UserChatScreen
from llm_mas.mas.conversation import Conversation


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
            yield Button("Agent to Agent Conversation", id="agent_to_agent")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses to navigate to different screens."""
        # example agent to agent conversation
        agent_to_agent_conversation = Conversation()

        agent1 = TRAVEL_PLANNER_AGENT
        agent2 = CALENDAR_AGENT

        agent_to_agent_conversation.add_message(
            agent1,
            content="Hello, I am planning a trip and need to schedule some events. Can you help me with that?",
        )
        agent_to_agent_conversation.add_message(
            agent2,
            content="Sure! I can help you schedule events. What dates are you looking at for your trip?",
        )
        agent_to_agent_conversation.add_message(agent1, content="I'm looking at traveling from June 10th to June 20th.")

        if event.button.id == "list_agents":
            self.app.push_screen(AgentListScreen(self.client))
        elif event.button.id == "talk_agent":
            self.app.push_screen(UserChatScreen(self.client, conversation=Conversation()))
        elif event.button.id == "mcp_client_info":
            self.app.push_screen(MCPClientScreen(self.client))
        elif event.button.id == "agent_to_agent":
            self.app.push_screen(
                AgentChatScreen(
                    self.client,
                    conversation=agent_to_agent_conversation,
                ),
            )
