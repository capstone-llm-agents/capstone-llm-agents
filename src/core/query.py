from capabilities.knowledge_base import Knowledge
from capabilities.memory import Memory
from core.chat import ChatMessage
from core.entity import Entity


class Query(ChatMessage):
    """A query in a conversation."""

    def __init__(
        self,
        sender: Entity,
        recipient: Entity,
        content: str,
        memories: list[Memory] | None = None,
        knowledge: list[Knowledge] | None = None,
    ):
        super().__init__(recipient, content)
        self.sender = sender
        self.recipient = recipient
        self.memories = memories or []
        self.knowledge = knowledge or []


class QueryResponse(ChatMessage):
    """A response to a query in a conversation."""
