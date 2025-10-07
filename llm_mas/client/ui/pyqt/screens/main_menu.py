# main_menu.py (fixed)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from llm_mas.client.account.client import Client
from llm_mas.client.ui.pyqt.screens.user_chat_screen import UserChatScreen
from llm_mas.client.ui.pyqt.screens.mcp_client import MCPClientScreen
from llm_mas.client.ui.pyqt.screens.agent_list import AgentListScreen
from llm_mas.client.ui.pyqt.screens.conversation_screen import ConversationsScreen
from llm_mas.client.ui.pyqt.screens.agent_network_screen import AgentNetworkScreen
from llm_mas.mas.conversation import Conversation
from llm_mas.mas.checkpointer import CheckPointer
from llm_mas.mas.agentstate import State
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
        self.mcp_client_btn = QPushButton("MCP Client Info")
        self.list_agents_btn = QPushButton("List Agents")
        self.view_conversations_btn = QPushButton("View Conversations")
        self.agent_network_btn = QPushButton("Agent Network")

        layout.addWidget(self.talk_agent_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.mcp_client_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.list_agents_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.view_conversations_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.agent_network_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()

        layout.setSpacing(40)

        # width
        for btn in [self.talk_agent_btn, self.mcp_client_btn, self.list_agents_btn, self.view_conversations_btn, self.agent_network_btn]:
            btn.setMaximumWidth(200)

        # Connect signals
        self.talk_agent_btn.clicked.connect(self._on_talk_agent)
        self.mcp_client_btn.clicked.connect(self._on_mcp_client)
        self.list_agents_btn.clicked.connect(self._on_list_agents)
        self.view_conversations_btn.clicked.connect(self._on_view_conversations)
        self.agent_network_btn.clicked.connect(self._on_agent_network)


    # Navigation handlers
    def _on_talk_agent(self):
        """Navigate to user chat screen."""

        self.nav.navigate.emit("user_chat", {"conversation": Conversation("User Assistant Chat")})

    def _on_mcp_client(self):
        """Navigate to MCP client info screen."""
        self.nav.navigate.emit("mcp_client", None)

    def _on_list_agents(self):
        """Navigate to agent list screen."""
        self.nav.navigate.emit("agent_list", None)

    def _on_view_conversations(self):
        """Navigate to conversations screen."""
        self.nav.navigate.emit("conversations", None)

    def _on_agent_network(self):
        self.nav.navigate.emit("agent_network", None)
