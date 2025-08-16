"""The stateful action module defines actions that can modify the workspace state."""

from typing import Any

from llm_mas.action_system.core.action import Action
from llm_mas.agent.workspace import WorkspaceState


class StatefulAction(Action):
    """A stateful action that can modify the workspace state."""

    def __init__(self, workspace_state: WorkspaceState, description: str) -> None:
        """Initialize the StatefulAction."""
        super().__init__(description=description)

        self.workspace_state = workspace_state

    def save_state(self, key: str, value: Any) -> None:  # noqa: ANN401
        """Save a value to the workspace state."""
        self.workspace_state.set_state(key, value)

    def get_state(self, key: str) -> Any:  # noqa: ANN401
        """Get a value from the workspace state."""
        return self.workspace_state.get_value(key)
