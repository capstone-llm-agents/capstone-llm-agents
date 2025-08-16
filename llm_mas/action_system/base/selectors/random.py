"""The random selector module provides a base class for random selection of actions in the action system."""

import random
from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_selector import ActionSelector
from llm_mas.action_system.core.action_space import ActionSpace


# random selection policy
class RandomSelector(ActionSelector):
    """A selection policy that randomly selects an action from the narrowed action space."""

    @override
    def select_action(self, action_space: ActionSpace, context: ActionContext) -> Action:
        """Select a random action from the given action space."""
        if not action_space.actions:
            msg = "Action space is empty. Cannot select an action."
            raise ValueError(msg)
        return random.choice(action_space.actions)  # noqa: S311 (random.choice is safe here)
