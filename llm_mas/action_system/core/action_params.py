"""ActionParams module defines the ActionParams class for defining parameters used in actions."""

import logging
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
        return self.params.get(key, None)

    def has_param(self, key: str) -> bool:
        """Check if a parameter exists."""
        return key in self.params

    def copy(self) -> "ActionParams":
        """Create a copy of the action parameters."""
        new_params = ActionParams()
        new_params.params = self.params.copy()
        return new_params

    def to_dict(self) -> dict[str, Any]:
        """Convert the parameters to a dictionary."""
        return self.params

    def matches_schema(self, schema: dict[str, Any]) -> bool:
        """Check if the parameters match the given schema."""
        logging.getLogger("textual_app").debug("Checking parameters against schema: %s", schema)
        logging.getLogger("textual_app").debug("Current parameters: %s", self.params)

        # TODO: Make this more robust, include types etc.  # noqa: TD003

        # check if all required properties are present
        for prop in schema.get("required", []):
            if prop not in self.params:
                logging.getLogger("textual_app").warning("Missing required parameter: %s", prop)
                return False
        return True
