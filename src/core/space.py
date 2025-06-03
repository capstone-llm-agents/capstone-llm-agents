from core.chat import ChatHistory
from core.entity import Entity
from core.mas import MAS


class Space:
    """A space holds some entities and a chat history between them."""

    entities: list[Entity]
    chat_history: ChatHistory

    def __init__(self, mas: MAS):
        self.entities = []
        self.chat_history = ChatHistory()
        self.mas = mas

    def get_entities(self) -> list[Entity]:
        """Get all entities in the space."""
        return self.entities

    def get_chat_history(self) -> ChatHistory:
        """Get the chat history in the space."""

        # TODO remove this spoof and get the chat history from the space not MAS
        return self.mas.chat_history
