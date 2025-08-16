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

    # TODO: Actual implementation to find the assistant agent
    def get_assistant_agent(self) -> Agent | None:
        """Return the first agent that is an assistant agent."""
        if not self.agents:
            return None
        return self.agents[0]
