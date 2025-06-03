from core.agent import Agent
from core.chat import ChatHistory
from core.entity import Entity
from core.mas import MAS


class Space:
    """A space holds some entities and a chat history between them."""

    name: str
    entities: list[Entity]
    chat_history: ChatHistory

    def __init__(self, name: str, mas: MAS):
        self.name = name
        self.entities = []
        self.chat_history = ChatHistory()
        self.mas = mas

    def get_entities(self) -> list[Entity]:
        """Get all entities in the space."""
        return self.entities

    def get_chat_history(self) -> ChatHistory:
        """Get the chat history in the space."""
        return self.chat_history

    def add_entity(self, entity: Entity):
        """Add an entity to the space."""
        if entity not in self.entities:
            self.entities.append(entity)


class MASSpace(Space):
    """A space that is part of a Multi-Agent System (MAS)."""

    assistant: Agent
    """The assistant agent talks to the user."""

    discovery_agent: Agent
    """The discovery agent helps the assistant find other agents outside the MAS."""

    def __init__(self, name: str, mas: MAS, assistant: Agent, discovery_agent: Agent):
        super().__init__(name, mas)
        self.assistant = assistant
        self.discovery_agent = discovery_agent
