"""Module for serialisable objects."""


class Serialisable:
    """An abstract base class for serialisable objects."""

    def to_dict(self) -> dict:
        """Convert the object to a dictionary."""
        raise NotImplementedError("Subclasses must implement this method.")

    @classmethod
    def from_dict(cls, data: dict):
        """Create an object from a dictionary."""
        raise NotImplementedError("Subclasses must implement this method.")
