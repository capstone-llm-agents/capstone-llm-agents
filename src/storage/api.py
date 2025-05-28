"""API layer to interact with the storage system."""

from core.agent import Agent
from core.chat import ChatHistory
from storage.storage import AppStorage


class StorageAPI:
    """A class to interact with the storage system."""

    def __init__(self, db_path: str):
        self.storage = AppStorage([], ChatHistory())
        self.db_path = db_path

    def start(self):
        """Initialise the storage system."""
        self.storage = AppStorage.load_from_sql_db(self.db_path)

    def save(self):
        """Save the current state of the storage system."""
        print("Saving storage to database...")
        self.storage.save_to_sql_db(self.db_path)

    def add_agent(self, agent: "Agent"):
        """Add an agent to the storage system."""
        self.storage.add_agent(agent)

    def get_chat_history(self) -> ChatHistory:
        """Get the chat history from the storage system."""
        return self.storage.chat_history
