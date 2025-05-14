from capabilities.knowledge_base import Document
from core.agent import Agent
from core.chat import ChatHistory


class AppStorage:
    """Stores the app's data."""

    agents: list[Agent]
    chats: list[ChatHistory]
    agent_chats: dict[Agent, list[ChatHistory]]
    documents: list[Document]

    def __init__(self):
        self.agents = []
        self.chats = []
        self.agent_chats = {}
        self.documents = []
