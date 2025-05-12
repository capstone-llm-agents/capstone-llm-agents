from core.chat import ChatHistory, Query


class CommunicationProtocol:
    """Communication Protocol creates a new query from a response."""

    # TODO: supported by Sprint 3

    def create_query(self, chat_history: ChatHistory) -> Query:
        """Create a new query from the chat history."""
        raise NotImplementedError("create_query not implemented")
