"""The system view of a fragment is the raw data representation for the system."""

from __future__ import annotations

import json
from typing import Any

from llm_mas.fragment.view import FragmentView


class SystemView(FragmentView):
    """The system view of a fragment is the raw data representation for the system."""


class JSONDictSystemView(SystemView):
    """A JSON representation of the system view."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize a JSON system view with data."""
        self.data: dict[str, Any] = data

    def set_param(self, key: str, value: Any) -> None:  # noqa: ANN401
        """Set a parameter value."""
        self.data[key] = value

    def get_param(self, key: str) -> Any:  # noqa: ANN401
        """Get a parameter value."""
        return self.data.get(key)

    def has_param(self, key: str) -> bool:
        """Check if a parameter exists."""
        return key in self.data

    def copy(self) -> JSONDictSystemView:
        """Create a copy of the action parameters."""
        return JSONDictSystemView(self.data.copy())

    def as_json_pretty(self) -> str:
        """Return the dict data as a pretty JSON string."""
        return json.dumps(self.data, indent=4)

    def is_empty(self) -> bool:
        """Check if the dict data is empty."""
        return not self.data
