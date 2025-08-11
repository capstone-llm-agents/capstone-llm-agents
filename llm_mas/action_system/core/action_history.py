"""Action history management for the multi-agent system."""

from llm_mas.action_system.core.action import Action


class ActionHistory:
    """Class to keep track of action history."""

    def __init__(self) -> None:
        """Initialize the action history."""
        self.history: list[Action] = []

    def add_action(self, action: Action) -> None:
        """Add an action to the history."""
        self.history.append(action)

    def get_history(self) -> list[Action]:
        """Get the action history."""
        return self.history

    def get_last_action(self) -> Action | None:
        """Get the last action from the history."""
        if self.history:
            return self.history[-1]
        return None

    def has_action(self, action: Action) -> bool:
        """Check if a specific action is in the history."""
        return action in self.history
