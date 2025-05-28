from core.agent import Agent
from core.chat import ChatHistory
from core.query import Query
from core.entity import HumanUser


class CommunicationProtocol:
    """Communication Protocol creates a new query from a response."""

    # TODO: supported by Sprint 3

    def __init__(self, user: HumanUser):
        self.user = user

    def create_query(self, chat_history: ChatHistory, agents: list[Agent]) -> Query:
        """Create a new query from the chat history."""
        raise NotImplementedError("create_query not implemented")
