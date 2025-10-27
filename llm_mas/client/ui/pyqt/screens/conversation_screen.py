# conversations_screen.py (PyQt6 version)
import random

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from llm_mas.client.account.client import Client
from llm_mas.client.ui.pyqt.screens.agent_chat_screen import AgentChatScreen
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.mas.conversation import Conversation


class ConversationsScreen(QWidget):
    """Screen to display all conversations (PyQt6)."""

    def __init__(self, client: Client, nav: QWidget, conversations: list[Conversation]):
        super().__init__()
        self.client = client
        self.nav = nav
        self.conversations = conversations
        self.stacked_widget = None
        self.main_view = None

        self._init_ui()

    def _init_ui(self):
        # Create a stacked widget to switch between list view and agent chat view
        self.stacked_widget = QStackedWidget()

        # Main view (list of conversations)
        self.main_view = QWidget()
        layout = QVBoxLayout()
        self.main_view.setLayout(layout)

        # Top bar with back, add, and clear buttons
        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(lambda: self.nav.navigate.emit("main_menu", None))
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()

        self.add_btn = QPushButton("+")
        self.add_btn.clicked.connect(self._add_conversation)
        top_bar.addWidget(self.add_btn)

        self.clear_btn = QPushButton("Clear Conversations")
        self.clear_btn.clicked.connect(self._clear_conversations)
        top_bar.addWidget(self.clear_btn)

        layout.addLayout(top_bar)

        # Header
        header = QLabel("Conversations")
        layout.addWidget(header)

        # User conversations section
        user_section_label = QLabel("My Conversations")
        user_section_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(user_section_label)

        self.user_convo_list = QListWidget()
        self.user_convo_list.itemClicked.connect(self._on_user_conversation_clicked)
        layout.addWidget(self.user_convo_list)

        # Agent conversations section
        agent_section_label = QLabel("Agent Conversations")
        agent_section_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(agent_section_label)

        self.agent_convo_list = QListWidget()
        self.agent_convo_list.itemClicked.connect(self._on_agent_conversation_clicked)
        layout.addWidget(self.agent_convo_list)

        self._populate_conversations()

        # Add main view to stacked widget
        self.stacked_widget.addWidget(self.main_view)

        # Set up the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def _get_display_name(self, convo: Conversation) -> str:
        """Generate a friendly display name for a conversation."""
        if convo.is_user_conversation():
            # For user conversations, show first user message or "New Chat"
            if convo.chat_history.messages:
                first_msg = convo.chat_history.messages[0]
                if first_msg.role == "user":
                    # Truncate long messages
                    preview = first_msg.content[:50]
                    if len(first_msg.content) > 50:
                        preview += "..."
                    return preview
            return "New Chat"
        else:
            # For agent conversations, show participant names
            if convo.participants:
                names = [p.name for p in convo.participants]
                return " ↔ ".join(names)
            return convo.name

    def _populate_conversations(self):
        """Populate conversations into user and agent lists."""
        self.user_convo_list.clear()
        self.agent_convo_list.clear()

        for convo in self.conversations:
            display_name = self._get_display_name(convo)
            item = QListWidgetItem(display_name)
            # Store conversation object in item data
            item.setData(1, convo)

            if convo.is_user_conversation():
                self.user_convo_list.addItem(item)
            else:
                self.agent_convo_list.addItem(item)

    def _on_user_conversation_clicked(self, item: QListWidgetItem):
        """Handle click on user conversation - navigate using existing nav system."""
        conversation = item.data(1)
        APP_LOGGER.info(f"Opening user conversation: {conversation.name}")
        # Use existing navigation system
        self.nav.navigate.emit("user_chat", {"conversation": conversation})

    def _on_agent_conversation_clicked(self, item: QListWidgetItem):
        """Handle click on agent conversation - show agent chat screen inline."""
        conversation = item.data(1)
        APP_LOGGER.info(f"Opening agent conversation: {conversation.name}")

        # Create agent chat screen with back callback
        agent_chat = AgentChatScreen(self.client, conversation, on_back=self._back_to_list)

        # Add to stacked widget and show it
        self.stacked_widget.addWidget(agent_chat)
        self.stacked_widget.setCurrentWidget(agent_chat)

    def _back_to_list(self):
        """Return to the conversation list view."""
        # Switch back to main view
        self.stacked_widget.setCurrentWidget(self.main_view)

        # Remove any agent chat screens (keep only main view)
        while self.stacked_widget.count() > 1:
            widget = self.stacked_widget.widget(1)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()

    def _add_conversation(self):
        """Add a new conversation and navigate to it."""
        conversation_id = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=6))
        conversation_name = f"Conversation-{conversation_id}"

        APP_LOGGER.info(f"Creating new conversation: {conversation_name}")
        self.client.mas.conversation_manager.start_conversation(conversation_name)

        conversation = self.client.mas.conversation_manager.get_conversation(conversation_name)
        self.conversations = self.client.mas.conversation_manager.get_all_conversations()

        # Refresh the lists
        self._populate_conversations()

        # Navigate to the new conversation
        self.nav.navigate.emit("user_chat", {"conversation": conversation})

    def _clear_conversations(self):
        """Clear all conversations."""
        APP_LOGGER.info("Clearing all conversations")
        self.client.mas.conversation_manager.clear_conversations()
        self.conversations = self.client.mas.conversation_manager.get_all_conversations()
        self._populate_conversations()

    def _go_back(self):
        self.nav.setCentralWidget(self.nav.main_menu)
