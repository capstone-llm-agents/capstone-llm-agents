from core.capabiliity_manager import AgentCapabilities
from core.chat import Query, QueryResponse
from core.entity import Entity


class Agent(Entity):
    """A class representing an agent with various capabilities."""

    def __init__(
        self, name: str, description: str, role: str, capabilities: AgentCapabilities
    ):
        super().__init__(name, description, role)

        # capabilities
        self.capabilties = capabilities

    def handle_query(self, query: Query) -> QueryResponse:
        """Handle a query by executing it and returning the result."""

        # TODO use the capabilities to handle the query

        # NOTE: this should be able to be implemented now, but still working on it
        raise NotImplementedError("handle_query not implemented")

    def get_capabilities(self) -> AgentCapabilities:
        """Get the capabilities of the agent."""
        return self.capabilties
