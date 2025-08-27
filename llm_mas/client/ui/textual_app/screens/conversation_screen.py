"""Conversation list screen for user↔agent and agent↔agent conversations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from llm_mas.client.ui.textual_app.screens.agent_chat_screen import AgentChatScreen
from llm_mas.client.ui.textual_app.screens.user_chat_screen import UserChatScreen
from llm_mas.logging.loggers import APP_LOGGER

if TYPE_CHECKING:
    from textual import events
    from textual.app import ComposeResult

    from llm_mas.client.account.client import Client
    from llm_mas.mas.conversation import Conversation


class ConversationsScreen(Screen):
    """Screen listing user and agent conversations."""

    CSS_PATH = "../styles/screen.tcss"

    def __init__(self, client: Client, conversations: list[Conversation]) -> None:
        """Initialize with client and list of conversations."""
        super().__init__()
        self.client = client
        self.conversations = conversations
        self.user_container: ScrollableContainer
        self.agent_container: ScrollableContainer

    def compose(self) -> ComposeResult:
        """Compose the conversations screen layout."""
        yield Header(name="Conversations")

        with Horizontal(id="conv-header-bar"):
            yield Button("+", id="add-btn")
            yield Button("Clear Conversations", id="clear-btn")

        # Scrollable containers for each section
        yield Static("My Conversations", classes="section-title")

        self.user_container = ScrollableContainer(id="user-conv-container")
        yield self.user_container

        yield Static("Agent Conversations", classes="section-title")
        self.agent_container = ScrollableContainer(id="agent-conv-container")
        yield self.agent_container

        yield Footer()

    def on_mount(self) -> None:
        """Populate conversation lists into their containers."""
        for conversation in self.conversations:
            btn = Button(conversation.name, id=f"conv-{conversation.name}", classes="conversation-btn")
            if conversation.is_user_conversation():
                self.user_container.mount(btn)
            else:
                self.agent_container.mount(btn)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button actions."""
        if event.button.id == "add-btn":
            self.client.mas.conversation_manager.start_conversation("NewConversation")

            conversation = self.client.mas.conversation_manager.get_conversation("NewConversation")

            self.app.pop_screen()
            self.app.push_screen(UserChatScreen(self.client, conversation=conversation))

        elif event.button.id == "clear-btn":
            # TODO: implement clearing conversations  # noqa: TD003
            APP_LOGGER.info("Clear conversations clicked")
        elif event.button.id and event.button.id.startswith("conv-"):
            conv_name = event.button.label

            conversation = self.client.mas.conversation_manager.get_conversation(str(conv_name))

            if conversation.is_user_conversation():
                self.app.pop_screen()
                self.app.push_screen(UserChatScreen(self.client, conversation=conversation))
            else:
                self.app.pop_screen()
                self.app.push_screen(AgentChatScreen(self.client, conversation=conversation))

    # esc key
    def on_key(self, event: events.Key) -> None:
        """Handle key events for navigation."""
        if event.key == "escape":
            self.app.pop_screen()
