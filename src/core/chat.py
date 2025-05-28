from core.entity import Entity
from storage.serialisable import Serialisable


import json


class ChatMessage:
    """A chat message in a conversation."""

    def __init__(self, who: Entity, content: str):
        self.who = who
        self.content = content


class ChatHistory(Serialisable):
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

    def to_dict(self) -> dict:
        """Convert the ChatHistory object to a dictionary."""

        # messages
        messages = [
            {"who": message.who.to_dict(), "content": message.content}
            for message in self.messages
        ]

        # as json str
        messages = json.dumps(messages, default=lambda o: o.to_dict(), indent=2)

        return {"messages": messages}

    @classmethod
    def from_dict(cls, data: dict):
        """Create a ChatHistory object from a dictionary."""
        chat_history = cls()

        # load messages from json str
        messages = json.loads(data["messages"])

        for message in messages:
            chat_history.add_message(
                ChatMessage(Entity.from_dict(message["who"]), message["content"])
            )

        return chat_history
