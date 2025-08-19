"""Base class for policies that narrow down the action space based on the current state."""

from abc import abstractmethod

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.agent.workspace import Workspace


class ActionNarrower:
    """Base class for policies that narrow down the action space based on the current state."""

    @abstractmethod
    def narrow(self, workspace: Workspace, action_space: ActionSpace) -> ActionSpace:
        """Narrow the action space based on the policy."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)

    @abstractmethod
    def update_for_new_action(self, action: Action, action_space: ActionSpace) -> None:
        """Update the policy for a new action."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)
