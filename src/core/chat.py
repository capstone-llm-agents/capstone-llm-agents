from core.entity import Entity


class ChatMessage:
    """A chat message in a conversation."""

    def __init__(self, who: Entity, content: str):
        self.who = who
        self.content = content


class ChatHistory:
    """A list of chat messages in a conversation."""

    messages: list[ChatMessage]

    def __init__(self):
        self.messages = []

    def add_message(self, message: ChatMessage):
        """Add a message to the chat history."""
        self.messages.append(message)

    def get_messages(self) -> list[ChatMessage]:
        """Get all messages in the chat history."""
        return self.messages

    def clear(self):
        """Clear the chat history."""
        self.messages = []

    def get_last_message(self) -> ChatMessage | None:
        """Get the last message in the chat history."""
        if self.messages:
            return self.messages[-1]
        return None

    def get_last_n_messages(self, n: int) -> list[ChatMessage]:
        """Get the last n messages in the chat history."""
        if n <= 0:
            return []

        count = min(n, len(self.messages))
        return self.messages[-count:]
