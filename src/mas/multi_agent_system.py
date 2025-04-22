"""Module for Multi-Agent System (MAS)"""

from mas.agent import MASAgent
from mas.base_resource import BaseResource
from mas.query.mas_query import MASQuery
from mas.resource_manager import ResourceManager
from mas.task_manager import TaskManager


class MultiAgentSystem:
    """A class representing a Multi-Agent System (MAS).

    The MAS contains:
        A collection of agents that can interact with each other and perform tasks (possibly nodes).
        A resource manager that knows about all the resources in the system.
        A task manager that knows about all the tasks in the system.
    """

    def __init__(self):
        """
        Initialise the Multi-Agent System (MAS).
        """
        self.agents: list[MASAgent] = []
        """List of agents in the MAS."""

        self.resource_manager = ResourceManager()
        """The resource manager for the MAS."""

        self.task_manager = TaskManager()
        """The task manager for the MAS."""

    def solve_query(self, query: MASQuery) -> BaseResource:
        """
        Solve a query using the MAS.

        Args:
            query (MASQuery): The query to be solved.

        Returns:
            BaseResource: The resource obtained from solving the query.
        """

    def add_agent(self, agent: MASAgent):
        """
        Add an agent to the MAS.

        Args:
            agent (MASAgent): The agent to be added.
        """
        self.agents.append(agent)
