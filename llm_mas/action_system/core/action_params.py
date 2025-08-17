"""ActionParams module defines the ActionParams class for defining parameters used in actions."""

from typing import Any


class ActionParams:
    """Base class for action parameters."""

    def __init__(self) -> None:
        """Initialize the action parameters."""
        self.params: dict[str, Any] = {}

    def set_param(self, key: str, value: Any) -> None:  # noqa: ANN401
        """Set a parameter value."""
        self.params[key] = value

    def get_param(self, key: str) -> Any:  # noqa: ANN401
        """Get a parameter value."""
        return self.params.get(key)

    def has_param(self, key: str) -> bool:
        """Check if a parameter exists."""
        return key in self.params

    def copy(self) -> "ActionParams":
        """Create a copy of the action parameters."""
        new_params = ActionParams()
        new_params.params = self.params.copy()
        return new_params
