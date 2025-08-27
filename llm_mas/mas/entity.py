"""An entity is a User or an Agent in the MAS."""

from __future__ import annotations


class Entity:
    """Base class for entities in the MAS."""

    def __init__(self, name: str, role: str) -> None:
        """Initialize the entity with a name."""
        self.name = name
        self.role = role

        # friends
        self.friends: set[Entity] = set()

    def get_name(self) -> str:
        """Return the name of the entity."""
        return self.name

    def get_role(self) -> str:
        """Return the role of the entity."""
        return self.role

    def add_friend(self, friend: Entity) -> None:
        """Add a friend to the entity."""
        # two-way friendship
        self.friends.add(friend)
        if self not in friend.friends:
            friend.add_friend(self)
