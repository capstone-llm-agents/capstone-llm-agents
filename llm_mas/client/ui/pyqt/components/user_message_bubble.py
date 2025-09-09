"""User message bubble for PyQt6."""

from PyQt6.QtWidgets import QLabel
from .message_bubble import MessageBubble

class UserMessage(MessageBubble):
    """A message bubble for user messages."""

    def __init__(self, message: str):
        super().__init__(message)
        sender_label = QLabel("You")
        content_label = QLabel(self.message)
        self.layout.addWidget(sender_label)
        self.layout.addWidget(content_label)
