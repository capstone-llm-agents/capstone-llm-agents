"""Action selection strategy base class for the multi-agent system."""

from abc import abstractmethod

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_space import ActionSpace


class ActionSelector:
    """Base class for action selection strategies."""

    @abstractmethod
    def select_action(self, action_space: ActionSpace, context: ActionContext) -> Action:
        """Select an action for the given agent."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)
