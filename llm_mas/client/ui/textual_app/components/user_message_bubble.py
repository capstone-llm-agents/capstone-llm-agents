"""A message bubble widget for user messages."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from llm_mas.client.ui.textual_app.components.message_bubble import MessageBubble


class UserMessage(MessageBubble):
    """A message bubble widget for user messages."""

    def compose(self) -> ComposeResult:
        """Compose the user message bubble."""
        with Horizontal(classes="user-message-container"):
            yield Static("", classes="spacer")  # Spacer to push message to right
            with Vertical(classes="user-message-bubble"):
                yield Static("You", classes="message-sender")
                yield Static(self.message, classes="message-content")
