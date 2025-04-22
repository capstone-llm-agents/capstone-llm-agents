"""Module for AG2 MAS Tool"""

from typing import Callable
from mas.ag2.ag2_agent import AG2MASAgent
from mas.tool import Tool


class AG2Tool(Tool):
    """A class representing a tool in a Multi-Agent System (MAS) using the Autogen2 framework."""

    def __init__(
        self,
        name: str,
        description: str,
        func: Callable,
        caller: AG2MASAgent,
        executor: AG2MASAgent,
    ):
        """
        Initialise the AG2Tool with a name.

        Args:
            name (str): The name of the tool.
            description (str): The description of the tool.
            func (Callable): The function that the tool represents.
            caller (AG2MasAgent): The agent that calls the tool.
            executor (AG2MasAgent): The agent that executes the tool.
        """
        super().__init__(name, description, func)
        self.caller = caller
        """The agent that calls the tool."""
        self.executor = executor
        """The agent that executes the tool."""

    def get_caller(self) -> AG2MASAgent:
        """Get the caller of the tool."""
        return self.caller

    def get_executor(self) -> AG2MASAgent:
        """Get the executor of the tool."""
        return self.executor
