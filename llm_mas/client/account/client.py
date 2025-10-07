"""The client module defines the client account functionality for the MAS."""

from llm_mas.mas.agent import Agent
from llm_mas.mas.mas import MAS
from llm_mas.mas.user import User
from llm_mas.mcp_client.client import MCPClient
from llm_mas.utils.config.general_config import GeneralConfig


class Client:
    """The Client class represents a user account in the MAS."""

    def __init__(self, username: str, mas: MAS, mcp_client: MCPClient, config: GeneralConfig) -> None:
        """Initialize the client with a username."""
        self.mas = mas
        self.mcp_client = mcp_client
        self.user = User(name=username, description="A user of the multi-agent system.")
        self.config = config

    def get_username(self) -> str:
        """Return the username of the client."""
        return self.user.get_name()

    def get_mas(self) -> MAS:
        """Return the MAS instance associated with the client."""
        return self.mas

    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the MAS associated with the client."""
        self.mas.add_agent(agent)

    def get_agents(self) -> list[Agent]:
        """Return the list of agents in the MAS associated with the client."""
        return self.mas.get_agents()

    def get_assistant_agent(self) -> Agent | None:
        """Return the assistant agent in the MAS associated with the client."""
        return self.mas.get_assistant_agent()

    def get_discovery_agent(self) -> Agent | None:
        """Return the discovery agent in the MAS associated with the client."""
        return self.mas.get_discovery_agent()
