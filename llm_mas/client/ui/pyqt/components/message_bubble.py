"""Base class for message bubbles in PyQt6."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class MessageBubble(QWidget):
    """Base class for a chat message bubble."""

    def __init__(self, message: str):
        super().__init__()
        self.message = message
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
