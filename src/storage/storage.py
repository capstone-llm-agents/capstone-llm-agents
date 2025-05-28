from core.agent import Agent
from core.chat import ChatHistory
from core.entity import Entity
from storage.serialisable import Serialisable

from storage.sql import SQLMapper


class AppStorage(Serialisable):
    """Stores the app's data."""

    agents: list[Agent]
    chat_history: ChatHistory

    def __init__(self, agents: list[Agent], chat_history: ChatHistory):
        self.agents = agents
        self.chat_history = chat_history

    def add_agent(self, agent: Agent):
        """Add an agent to the storage."""
        self.agents.append(agent)

    def set_chat_history(self, chat: ChatHistory):
        """Set the chat history for the app."""
        self.chat_history = chat

    def to_dict(self) -> dict:
        """Convert the AppStorage object to a dictionary."""
        return {
            "agents": [agent.to_dict() for agent in self.agents],
            "chat_history": self.chat_history.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create an AppStorage object from a dictionary."""

        # TODO: Agent.from_dict calls Entity.from_dict, which does not have some of the agent details
        # maybe we need to decouple the capabilities from the base agent details
        # because we can't store the capabilities as serialisable data

        chat_history = ChatHistory.from_dict(data["chat_history"])
        agents = [Entity.from_dict(agent) for agent in data["agents"]]
        return cls(agents, chat_history)

    def save_to_sql_db(self, db_path: str):
        """Save the AppStorage object to an SQLite database."""

        # TODO kinda weird how we load and clear table but its fine for now

        # one table for agents, one for chat history
        with SQLMapper(db_path, "agents") as agent_mapper:
            # clear table, only save the latest agent
            agent_mapper.clear_table()

            for agent in self.agents:
                agent_mapper.save(agent)

        with SQLMapper(db_path, "chat_history") as chat_mapper:
            # clear table, only save the latest chat history
            chat_mapper.clear_table()
            chat_mapper.save(self.chat_history)

    @classmethod
    def load_from_sql_db(cls, db_path: str) -> "AppStorage":
        """Load the AppStorage object from an SQLite database."""
        with SQLMapper(db_path, "agents") as agent_mapper:
            agents = agent_mapper.load(Entity)

        with SQLMapper(db_path, "chat_history") as chat_mapper:
            chat_history = chat_mapper.load(ChatHistory)

            if not chat_history:
                chat_history = ChatHistory()
            else:
                chat_history = chat_history[0]

        return cls(agents, chat_history)
