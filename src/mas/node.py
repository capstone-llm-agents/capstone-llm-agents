"""Module for MAS Node class"""

from mas.agent import MASAgent
from mas.task import Task


class MASNode:
    """A class representing a node in the MAS where an agent or chat of multiple agents work together to achieve a common goal."""

    def __init__(
        self,
        name: str,
        task: Task,
        previous_node: "MASNode" | None = None,
    ):
        """
        Initialise the MASNode with a name.

        Args:
            name (str): The name of the node.
            task (Task): The task associated with the node.
            previous_node (MASNode | None): The previous node in the MAS.
        """
        self.name = name
        """The name of the node."""
        self.task = task
        """The task associated with the node."""
        self.previous_node = previous_node
        """The previous node in the MAS."""


class SingleAgentNode(MASNode):
    """A class representing a single agent node in the MAS."""

    def __init__(
        self,
        name: str,
        task: Task,
        agent: MASAgent,
        previous_node: MASNode | None = None,
    ):
        """
        Initialise the SingleAgentNode with a name.

        Args:
            name (str): The name of the node.
            task (Task): The task associated with the node.
            agent (MASAgent): The agent associated with the node.
            previous_node (MASNode | None): The previous node in the MAS.
        """
        super().__init__(name, task, previous_node)
        self.agent = agent
        """The agent associated with the node."""
