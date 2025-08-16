"""The Multi-Agent System (MAS) contains a system of agents that can collaborate to achieve complex tasks."""

from llm_mas.mas.agent import Agent


class MAS:
    """The MAS class represents the multi-agent system."""

    def __init__(self) -> None:
        """Initialize the MAS with an empty list of agents."""
        self.agents: list[Agent] = []

    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the MAS."""
        self.agents.append(agent)

    def get_agents(self) -> list[Agent]:
        """Return the list of agents in the MAS."""
        return self.agents
