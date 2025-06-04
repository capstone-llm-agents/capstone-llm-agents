from core.agent import Agent
from core.chat import ChatHistory, ChatMessage
from core.entity import Entity, HumanUser


class Space:
    """A space holds some entities and a chat history between them."""

    name: str
    entities: list[Entity]
    chat_history: ChatHistory

    def __init__(self, name: str):
        self.name = name
        self.entities = []
        self.chat_history = ChatHistory()

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

    def add_chat_message(self, message: ChatMessage):
        """Add a chat message to the chat history."""
        self.chat_history.add_message(message)


class UserSpace(Space):
    """A space where the user can interact with an assistant agent."""

    user: HumanUser
    assistant_agent: Agent

    def __init__(self, name: str, assistant_agent: Agent, user: HumanUser):
        super().__init__(name)

        self.user = user

        self.assistant_agent = assistant_agent
        self.add_entity(assistant_agent)


class MainSpace(Space):
    """A main space that holds all the agents, and the assistant agent."""

    assistant_agent: Agent
    discovery_agent: Agent | None

    def __init__(
        self,
        name: str,
        assistant_agent: Agent,
        all_agents: list[Agent],
        discovery_agent: Agent | None = None,
    ):
        super().__init__(name)

        self.assistant_agent = assistant_agent
        self.discovery_agent = discovery_agent

        for agent in all_agents:
            self.add_entity(agent)

    def get_agents(self) -> list[Agent]:
        """Get all agents in the main space."""
        return [entity for entity in self.entities if isinstance(entity, Agent)]


class DiscoverySpace(Space):
    """A space that holds the discovery agents for different domains."""

    discovery_agents: list[Agent]

    def __init__(self, name: str, discovery_agents: list[Agent]):
        super().__init__(name)

        self.discovery_agents = discovery_agents

        for agent in discovery_agents:
            self.add_entity(agent)
