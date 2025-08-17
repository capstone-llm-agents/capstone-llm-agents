"""An entity is a User or an Agent in the MAS."""


class Entity:
    """Base class for entities in the MAS."""

    def __init__(self, name: str, role: str) -> None:
        """Initialize the entity with a name."""
        self.name = name
        self.role = role

    def get_name(self) -> str:
        """Return the name of the entity."""
        return self.name
