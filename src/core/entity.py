from storage.serialisable import Serialisable


class Entity(Serialisable):
    """An entity in a conversation."""

    def __init__(self, name: str, description: str, role: str):
        self.name = name
        self.description = description
        self.role = role

    # TODO idk if this ok or not, but it works for now
    # because we want to load saved entities and we can't recreate the same instance
    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.name == other.name and self.role == other.role

    def __str__(self):
        return f"{self.name}"

    # TODO again could have consequences if we have two entities with the same name and role
    def __hash__(self):
        """Hash based on name and role."""
        return hash((self.name, self.role))

    def to_dict(self) -> dict:
        """Convert the Entity object to a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "role": self.role,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create an Entity object from a dictionary."""
        return cls(data["name"], data["description"], data["role"])


class HumanUser(Entity):
    """A human user in a conversation."""

    def __init__(self, name: str, description: str):
        super().__init__(name, description, "user")
