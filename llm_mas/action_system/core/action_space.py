"""The action_space module defines the base class for action spaces in the llm_mas package."""

import json

from llm_mas.action_system.core.action import Action


class ActionSpace:
    """Base class for all action spaces in the system."""

    def __init__(self) -> None:
        """Initialize the action space with a list of actions."""
        self.actions: list[Action] = []

    def get_actions(self) -> list[Action]:
        """Return the list of actions in the action space."""
        return self.actions

    def add_action(self, action: Action) -> None:
        """Add an action to the action space."""
        self.actions.append(action)

    def copy(self) -> "ActionSpace":
        """Create a copy of the action space."""
        new_space = ActionSpace()
        # NOTE: This assumes that actions are copyable.
        new_space.actions = self.actions.copy()
        return new_space

    def has_action(self, action: Action) -> bool:
        """Check if the action space contains a specific action."""
        return action in self.actions

    def as_json_pretty(self) -> str:
        """Return a pretty-printed JSON representation of the action space."""
        # 4 indent
        return json.dumps([action.as_json() for action in self.actions], indent=4, ensure_ascii=False)
