"""The source of a fragment."""

from enum import Enum, auto


class FragmentSource(Enum):
    """The source of a fragment."""

    UNKNOWN = auto()

    USER = auto()
    SYSTEM = auto()
    AGENT = auto()
