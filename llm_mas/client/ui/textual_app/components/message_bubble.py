"""The message bubble component of the textual app."""

from textual.widget import Widget


class MessageBubble(Widget):
    """Base class for message bubble widgets."""

    def __init__(self, message: str) -> None:
        """Initialize the message bubble."""
        super().__init__()
        self.message = message
