"""The main menu screen of the textual app."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header

from llm_mas.client.account.client import Client
from llm_mas.client.ui.textual_app.screens.agent_list import AgentListScreen
from llm_mas.client.ui.textual_app.screens.conversation_screen import ConversationsScreen
from llm_mas.client.ui.textual_app.screens.mcp_client import MCPClientScreen
from llm_mas.client.ui.textual_app.screens.upload_screen import UploadScreen
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
            yield Button("View Conversations", id="view_conversations")
            yield Button("Upload Files/Folders", id="upload_files")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses to navigate to different screens."""
        # example agent to agent conversation

        if event.button.id == "list_agents":
            self.app.push_screen(AgentListScreen(self.client))
        elif event.button.id == "talk_agent":
            self.app.push_screen(UserChatScreen(self.client, conversation=Conversation("User Assistant Chat")))
        elif event.button.id == "mcp_client_info":
            self.app.push_screen(MCPClientScreen(self.client))
        elif event.button.id == "view_conversations":
            self.app.push_screen(
                ConversationsScreen(
                    self.client,
                    conversations=self.client.mas.conversation_manager.get_all_conversations(),
                ),
            )
        elif event.button.id == "upload_files":
            self.app.push_screen(UploadScreen())
