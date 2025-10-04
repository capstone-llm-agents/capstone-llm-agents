"""A fragment that can be sent over the network."""

from enum import Enum, auto
from typing import Any


class FragmentSource(Enum):
    """The source of a fragment."""

    UNKNOWN = auto()

    USER = auto()
    SYSTEM = auto()
    AGENT = auto()


class FragmentKindSerializable:
    """A serializable version of FragmentKind."""

    def __init__(self, name: str, content: dict[str, Any], description: str | None = None) -> None:
        """Initialize a FragmentKindSerializable with a name."""
        self.name = name
        self.content = content
        self.description = description


class NetworkFragment:
    """A fragment that can be sent over the network."""

    def __init__(
        self,
        name: str,
        kind: FragmentKindSerializable,
        description: str | None = None,
        source: FragmentSource = FragmentSource.UNKNOWN,
    ) -> None:
        """Initialize a network fragment with a name, description, kind, and source."""
        self.name = name
        self.kind = kind
        self.description = description
        self.source = source

    def serialize(self) -> dict[str, Any]:
        """Serialize the network fragment to a dictionary."""
        return {
            "name": self.name,
            "kind": {
                "name": self.kind.name,
                "content": self.kind.content,
                "description": self.kind.description,
            },
            "description": self.description,
            "source": self.source.name,
        }
