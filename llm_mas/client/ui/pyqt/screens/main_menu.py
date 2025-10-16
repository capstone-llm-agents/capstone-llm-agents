"""Main menu screen for PyQt6 app."""

import asyncio

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QPushButton, QVBoxLayout, QWidget

from llm_mas.client.account.client import Client
from llm_mas.mas.agentstate import State
from llm_mas.mas.checkpointer import CheckPointer
from llm_mas.mas.conversation import Conversation


class MainMenu(QWidget):
    """Main menu for PyQt6 app with navigation."""

    def __init__(self, client: Client, checkpoint: CheckPointer, nav) -> None:
        super().__init__()
        self.client = client
        self.checkpoint = checkpoint
        self.nav = nav  # this is NavigationManager now - app.py
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout()
        layout.addStretch()
        self.setLayout(layout)

        # Buttons
        self.talk_agent_btn = QPushButton("Talk to Assistant Agent")
        self.agent_network_btn = QPushButton("Agent Network")
        self.friends_btn = QPushButton("Friends")
        self.upload_kb_btn = QPushButton("Upload to Knowledge Base")
        self.mcp_client_btn = QPushButton("MCP Client Info")
        self.view_conversations_btn = QPushButton("View Conversations")

        layout.addWidget(self.talk_agent_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.agent_network_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.friends_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.upload_kb_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.mcp_client_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.view_conversations_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()

        layout.setSpacing(40)

        # width
        for btn in [
            self.talk_agent_btn,
            self.agent_network_btn,
            self.friends_btn,
            self.mcp_client_btn,
            self.view_conversations_btn,
        ]:
            btn.setMaximumWidth(200)

        # Connect signals
        self.talk_agent_btn.clicked.connect(self._on_talk_agent)
        self.agent_network_btn.clicked.connect(self._on_agent_network)
        self.friends_btn.clicked.connect(self._on_friends)
        self.upload_kb_btn.clicked.connect(self._on_upload_kb)
        self.mcp_client_btn.clicked.connect(self._on_mcp_client)
        self.view_conversations_btn.clicked.connect(self._on_view_conversations)

    # Navigation handlers
    def _on_talk_agent(self) -> None:
        """Navigate to user chat screen."""
        conversation = self.client.mas.conversation_manager.start_or_get_conversation("User Assistant Chat")

        self.nav.navigate.emit("user_chat", {"conversation": conversation})

    def _on_mcp_client(self) -> None:
        """Navigate to MCP client info screen."""
        self.nav.navigate.emit("mcp_client", None)

    def _on_view_conversations(self) -> None:
        """Navigate to conversations screen."""
        self.nav.navigate.emit("conversations", None)

    def _on_agent_network(self) -> None:
        """Navigate to agent network screen."""
        self.nav.navigate.emit("agent_network", None)

    def _on_friends(self) -> None:
        """Navigate to friends screen."""
        self.nav.navigate.emit("friends", None)

    def _on_upload_kb(self) -> None:
        """Navigate to upload screen."""
        self.nav.navigate.emit("upload_kb", None)
