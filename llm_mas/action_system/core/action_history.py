"""Action history management for the multi-agent system."""

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_result import ActionResult


class ActionHistory:
    """Class to keep track of action history."""

    def __init__(self) -> None:
        """Initialize the action history."""
        self.history: list[tuple[Action, ActionResult]] = []

    def add_action(self, action: Action, result: ActionResult) -> None:
        """Add an action to the history."""
        self.history.append((action, result))

    def get_history(self) -> list[tuple[Action, ActionResult]]:
        """Get the action history."""
        return self.history

    def get_last_action(self) -> tuple[Action, ActionResult] | None:
        """Get the last action performed."""
        if self.history:
            return self.history[-1]
        return None

    def get_index(self, index: int) -> tuple[Action, ActionResult] | None:
        """Get the action at a specific index."""
        if self.history:
            return self.history[index]
        return None

    def has_action(self, action: Action) -> bool:
        """Check if a specific action is in the history."""
        return any(a == action for a, _ in self.history)

    def clear(self) -> None:
        """Clear the action history."""
        self.history.clear()
