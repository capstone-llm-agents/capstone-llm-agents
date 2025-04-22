"""Module for MAS Tool class and its components."""

from typing import Callable


class Tool:
    """A Tool is a function that can be called by an agent"""

    def __init__(self, name: str, description: str, func: Callable):
        """
        Initialise the Tool with a name.

        Args:
            name (str): The name of the tool.
        """
        self.name = name
        """The name of the tool."""
        self.description = description
        """The description of the tool."""
        self.func = func
        """The function that the tool represents."""

    def get_caller(self):
        """Get the caller of the tool."""
        raise NotImplementedError(
            "This method should be implemented in a subclass of Tool."
        )

    def get_executor(self):
        """Get the executor of the tool."""
        raise NotImplementedError(
            "This method should be implemented in a subclass of Tool."
        )
