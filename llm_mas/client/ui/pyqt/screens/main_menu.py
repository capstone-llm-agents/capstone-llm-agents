"""Main menu screen for PyQt6 app with navigation."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from llm_mas.client.account.client import Client
from llm_mas.mas.conversation import Conversation


class MainMenu(QWidget):
    """Main menu for PyQt6 app with navigation."""

    def __init__(self, client: Client, nav) -> None:
        super().__init__()
        self.client = client
        self.nav = nav  # this is NavigationManager now - app.py
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout()
        layout.addStretch()
        self.setLayout(layout)

        # Buttons
        self.talk_agent_btn = QPushButton("Talk to Assistant Agent")
        self.mcp_client_btn = QPushButton("MCP Client Info")
        self.view_conversations_btn = QPushButton("View Conversations")
        self.agent_network_btn = QPushButton("Agent Network")

        layout.addWidget(self.talk_agent_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.mcp_client_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.view_conversations_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.agent_network_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()

        layout.setSpacing(40)

        # width
        for btn in [self.talk_agent_btn, self.mcp_client_btn, self.view_conversations_btn, self.agent_network_btn]:
            btn.setMaximumWidth(200)

        # Connect signals
        self.talk_agent_btn.clicked.connect(self._on_talk_agent)
        self.mcp_client_btn.clicked.connect(self._on_mcp_client)
        self.view_conversations_btn.clicked.connect(self._on_view_conversations)
        self.agent_network_btn.clicked.connect(self._on_agent_network)

    # Navigation handlers
    def _on_talk_agent(self) -> None:
        """Navigate to user chat screen."""
        self.nav.navigate.emit("user_chat", {"conversation": Conversation("User Assistant Chat")})

    def _on_mcp_client(self) -> None:
        """Navigate to MCP client info screen."""
        self.nav.navigate.emit("mcp_client", None)


    def _on_view_conversations(self) -> None:
        """Navigate to conversations screen."""
        self.nav.navigate.emit("conversations", None)

    def _on_agent_network(self) -> None:
        """Navigate to agent network screen."""
        self.nav.navigate.emit("agent_network", None)
