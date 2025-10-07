# conversations_screen.py (PyQt6 version)
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem
from llm_mas.client.account.client import Client
from llm_mas.mas.conversation import Conversation

class ConversationsScreen(QWidget):
    """Screen to display all conversations (PyQt6)."""

    def __init__(self, client: Client, nav: QWidget, conversations: list[Conversation]):
        super().__init__()
        self.client = client
        self.nav = nav
        self.conversations = conversations

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Top bar with back button
        top_bar = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(lambda: self.nav.navigate.emit("main_menu", None))
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        header = QLabel("Conversations")
        layout.addWidget(header)

        self.convo_list = QListWidget()
        layout.addWidget(self.convo_list)

        self._populate_conversations()

    def _populate_conversations(self):
        for convo in self.conversations:
            item = QListWidgetItem(convo.name)
            self.convo_list.addItem(item)

    def _go_back(self):
        self.nav.setCentralWidget(self.nav.main_menu)
