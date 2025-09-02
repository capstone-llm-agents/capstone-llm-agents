"""The user class represents a user in the multi-agent system."""

from llm_mas.mas.entity import Entity


class User(Entity):
    """Base class for users in the MAS."""

    def __init__(self, name: str, description: str) -> None:
        """Initialize the user with a name."""
        super().__init__(name, role="user", description=description)
