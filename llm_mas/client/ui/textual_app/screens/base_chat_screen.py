"""Refactored chat screens for user↔agent and agent↔agent conversations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from llm_mas.client.ui.textual_app.components.agent_message_bubble import AgentMessage
from llm_mas.client.ui.textual_app.components.user_message_bubble import UserMessage
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.mas.agent import Agent

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from llm_mas.client.account.client import Client
    from llm_mas.mas.conversation import Conversation, Message


class BaseChatScreen(Screen):
    """Base chat screen showing conversation history and back button."""

    CSS_PATH = "../styles/screen.tcss"

    def __init__(self, client: Client, conversation: Conversation, title: str = "Conversation") -> None:
        """Initialize with client, conversation, and title."""
        super().__init__()
        self.client = client
        self.conversation = conversation
        self.chat_container: ScrollableContainer
        self.title = title

    def compose(self) -> ComposeResult:
        """Compose the chat screen layout."""
        yield Header(name=self.title)

        self.chat_container = ScrollableContainer(id="chat-container")
        yield self.chat_container

        yield Footer()

    def on_mount(self) -> None:
        """Render all messages from conversation history."""
        for message in self.conversation.chat_history.messages:
            bubble = self._make_bubble(message)
            if bubble:
                self.chat_container.mount(bubble)

    def _make_bubble(self, message: Message) -> Static | UserMessage | AgentMessage | None:
        """Return the right bubble widget based on role."""
        if message.role == "user":
            return UserMessage(message.content)
        if message.role == "assistant":
            agent = message.sender

            if not agent:
                APP_LOGGER.warning("Assistant message without sender agent, cannot create bubble")
                return Static(f"[No Agent] {message.content}")

            if not isinstance(agent, Agent):
                APP_LOGGER.warning("Assistant message sender is not an Agent instance")
                return Static(f"[Invalid Agent] {message.content}")
            return AgentMessage(agent, message.content)

        APP_LOGGER.warning(f"Unknown message role: {message.role}")
        return Static(f"[Unknown role] {message.content}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Back button returns to conversations screen."""
        if event.button.id == "back-btn":
            self.app.pop_screen()
