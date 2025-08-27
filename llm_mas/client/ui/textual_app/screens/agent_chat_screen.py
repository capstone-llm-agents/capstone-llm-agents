"""Screen for agent to agent conversations in read-only mode."""

from textual import events
from textual.app import ComposeResult

from llm_mas.client.account.client import Client
from llm_mas.client.ui.textual_app.screens.base_chat_screen import BaseChatScreen
from llm_mas.mas.conversation import Conversation


class AgentChatScreen(BaseChatScreen):
    """Read-only chat screen for agent to agent conversations."""

    def __init__(self, client: Client, conversation: Conversation) -> None:
        """Initialize with client and conversation."""
        super().__init__(client, conversation, title="Agent Conversation")

    def compose(self) -> ComposeResult:
        """Compose the chat screen layout without input field."""
        yield from super().compose()

    def on_key(self, event: events.Key) -> None:
        """Handle escape key to go back."""
        if event.key == "escape":
            self.app.pop_screen()
