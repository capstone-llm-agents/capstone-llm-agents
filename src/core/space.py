from core.chat import ChatHistory
from core.entity import Entity


class Space:
    """A space holds some entities and a chat history between them."""

    entities: list[Entity]
    chat_history: ChatHistory

    def __init__(self):
        self.entities = []
        self.chat_history = ChatHistory()

    def get_entities(self) -> list[Entity]:
        """Get all entities in the space."""
        return self.entities

    def get_chat_history(self) -> ChatHistory:
        """Get the chat history in the space."""
        return self.chat_history
