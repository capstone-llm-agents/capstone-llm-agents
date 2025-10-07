# agent_chat_screen.py
from PyQt6.QtWidgets import QWidget
from base_chat_screen import BaseChatScreen


class AgentChatScreen(BaseChatScreen):
    """Read-only chat screen for agent↔agent conversations."""

    def __init__(self, client, conversation, on_back=None):
        super().__init__(client, conversation, title="Agent Conversation", on_back=on_back)
