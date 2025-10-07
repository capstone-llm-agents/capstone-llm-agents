"""ActionParams module defines the ActionParams class for defining parameters used in actions."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from llm_mas.fragment.fragment import Fragment


class ActionResult:
    """Base class for action results."""

    def __init__(self) -> None:
        """Initialize the action results."""
        self.results: dict[str, Any] = {}

        # fragments
        self.fragments: list[Fragment] = []

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

    def as_json_pretty(self) -> str:
        """Return the action result as a pretty JSON string."""
        return json.dumps(self.results, indent=4)

    def is_empty(self) -> bool:
        """Check if the action result is empty."""
        return not self.results

    def add_fragment(self, fragment: Fragment) -> None:
        """Add a fragment to the action result."""
        self.fragments.append(fragment)
