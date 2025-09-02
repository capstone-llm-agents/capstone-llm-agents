"""The workspace module defines the workspace where agents can perform actions and save data."""

from typing import Any

from llm_mas.action_system.core.action_history import ActionHistory


class WorkspaceState:
    """Base class for the state of the workspace."""

    def __init__(self) -> None:
        """Initialize the workspace state."""
        self.state = {}

    def get_state(self) -> dict:
        """Return the current state of the workspace."""
        return self.state

    def get_value(self, key: str) -> Any:  # noqa: ANN401
        """Get a value from the workspace state."""
        return self.state.get(key, None)

    def set_state(self, key: str, value: Any) -> None:  # noqa: ANN401
        """Set a value in the workspace state."""
        self.state[key] = value


class Workspace:
    """The workspace is where the agent performs its actions and completes tasks."""

    def __init__(self) -> None:
        """Initialize the workspace."""
        self.action_history: ActionHistory = ActionHistory()
        self.state = WorkspaceState()

    def reset(self) -> None:
        """Reset the workspace to its initial state."""
        self.action_history = ActionHistory()
        self.state = WorkspaceState()
