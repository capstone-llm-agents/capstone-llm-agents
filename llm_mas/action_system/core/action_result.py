"""ActionParams module defines the ActionParams class for defining parameters used in actions."""

# TODO: update docstrings

from __future__ import annotations

from typing import Any


class ActionResult:
    """Base class for action results."""

    def __init__(self) -> None:
        """Initialize the action results."""
        self.results: dict[str, Any] = {}

    def set_param(self, key: str, value: Any) -> None:  # noqa: ANN401
        """Set a parameter value."""
        self.results[key] = value

    def get_param(self, key: str) -> Any:  # noqa: ANN401
        """Get a parameter value."""
        return self.results.get(key)

    def has_param(self, key: str) -> bool:
        """Check if a parameter exists."""
        return key in self.results

    def copy(self) -> ActionResult:
        """Create a copy of the action parameters."""
        new_params = ActionResult()
        new_params.results = self.results.copy()
        return new_params
