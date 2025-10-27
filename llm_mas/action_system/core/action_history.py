"""Action history management for the multi-agent system."""

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_result import ActionResult


class ActionHistory:
    """Class to keep track of action history."""

    def __init__(self) -> None:
        """Initialize the action history."""
        self.history: list[tuple[Action, ActionResult, ActionContext]] = []

    def add_action(self, action: Action, result: ActionResult, context: ActionContext) -> None:
        """Add an action to the history."""
        self.history.append((action, result, context))

    def get_history(self) -> list[tuple[Action, ActionResult, ActionContext]]:
        """Get the action history."""
        return self.history

    def get_last_action(self) -> tuple[Action, ActionResult, ActionContext] | None:
        """Get the last action performed."""
        if self.history:
            return self.history[-1]
        return None

    def get_history_at_index(self, index: int) -> tuple[Action, ActionResult, ActionContext] | None:
        """Get the action tuple at a specific index."""
        if not self.history:
            return None

        # Translate negative index relative to end
        if index < 0:
            index = len(self.history) + index

        # Clamp to valid range
        if index < 0:
            index = 0
        elif index >= len(self.history):
            index = len(self.history) - 1

        return self.history[index]

    def has_action(self, action: Action) -> bool:
        """Check if a specific action is in the history."""
        return any(a == action for a, _, _ in self.history)

    def clear(self) -> None:
        """Clear the action history."""
        for action, _, _ in self.history:
            action.reset()

        self.history.clear()
