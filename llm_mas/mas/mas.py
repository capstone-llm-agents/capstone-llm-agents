"""The Multi-Agent System (MAS) contains a system of agents that can collaborate to achieve complex tasks."""

from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.mas.agent import Agent
from llm_mas.mas.conversation import ConversationManager


class MAS:
    """The MAS class represents the multi-agent system."""

    def __init__(self) -> None:
        """Initialize the MAS with an empty list of agents."""
        self.agents: list[Agent] = []
        self.conversation_manager = ConversationManager()

        self.assistant_agent: Agent | None = None
        self.discovery_agent: Agent | None = None

    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the MAS."""
        self.agents.append(agent)

    def get_agents(self) -> list[Agent]:
        """Return the list of agents in the MAS."""
        return self.agents

    def get_assistant_agent(self) -> Agent | None:
        """Return the assistant agent if set, otherwise None."""
        if self.assistant_agent is None:
            APP_LOGGER.warning("Assistant agent not set in MAS. Call set_assistant_agent() to configure.")
        return self.assistant_agent

    def set_assistant_agent(self, agent: Agent) -> None:
        """Set the assistant agent and ensure it is part of the MAS."""
        if agent not in self.agents:
            self.add_agent(agent)
        self.assistant_agent = agent

    def get_discovery_agent(self) -> Agent | None:
        """Return the first agent that is a discovery agent."""
        if not self.agents:
            return None
        return self.discovery_agent or self.agents[0]

    def set_discovery_agent(self, agent: Agent) -> None:
        """Set the discovery agent and ensure it is part of the MAS."""
        if agent not in self.agents:
            self.add_agent(agent)
        self.discovery_agent = agent
