# base_chat_screen.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QFrame, QVBoxLayout
from PyQt6.QtCore import Qt

from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.mas.agent import Agent


class BaseChatScreen(QWidget):
    """Base chat screen showing conversation history and back button."""

    def __init__(self, client, conversation, title="Conversation", on_back=None):
        super().__init__()
        self.client = client
        self.conversation = conversation
        self.on_back = on_back

        layout = QVBoxLayout(self)

        # header
        header = QLabel(title)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # top bar with back button
        top_bar = QHBoxLayout()
        back_btn = QPushButton("<< Back")
        back_btn.clicked.connect(self._back_clicked)
        top_bar.addWidget(back_btn)
        layout.addLayout(top_bar)

        # scrollable chat area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.scroll_area.setWidget(self.chat_widget)

        layout.addWidget(self.scroll_area)

        # footer placeholder
        footer = QLabel("— End —")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

        # load history
        self._load_history()

    def _load_history(self):
        for message in self.conversation.chat_history.messages:
            bubble = self._make_bubble(message)
            if bubble:
                self.chat_layout.addWidget(bubble)

    def _make_bubble(self, message):
        """Return QLabel as message bubble."""
        if message.role == "user":
            return self._user_bubble(message.content)
        if message.role == "assistant":
            agent = message.sender
            if not isinstance(agent, Agent):
                APP_LOGGER.warning("Assistant message sender invalid")
                return QLabel(f"[Invalid Agent] {message.content}")
            return self._agent_bubble(agent, message.content)
        return QLabel(f"[Unknown role] {message.content}")

    def _user_bubble(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("background:#4b4b4b; color:#FFFFFF; border-radius:10px; padding:8px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        lbl.setWordWrap(True)
        return lbl

    def _agent_bubble(self, agent, text):
        lbl = QLabel(f"{agent.name}: {text}")
        lbl.setStyleSheet("background:#3b3b6b; color:#FFFFFF; border-radius:10px; padding:8px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        lbl.setWordWrap(True)
        return lbl

    def _back_clicked(self):
        if self.on_back:
            self.on_back()
