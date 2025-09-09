"""A base class for actions that decide what to do next based on the last action."""

from llm_mas.action_system.base.actions.stop import StopAction
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_narrower import NarrowerContext
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.agent.workspace import Workspace


class ActionSwitcher(Action):
    """An action that decides what to do next based on the last action."""

    def __init__(self, description: str, max_retries: int = 1) -> None:
        """Initialize the ActionSwitcher."""
        super().__init__(description=description)
        self.max_retries = max_retries
        self.retry_count = 0

    def hit_max_retries(self) -> bool:
        """Check if the action has hit the maximum number of retries."""
        return self.retry_count >= self.max_retries

    def add_retry(self) -> None:
        """Increment the retry count."""
        self.retry_count += 1

    def reset_retries(self) -> None:
        """Reset the retry count."""
        self.retry_count = 0

    def narrow(
        self,
        workspace: Workspace,
        action_space: ActionSpace,
        context: ActionContext,
        narrower_context: NarrowerContext | None = None,
    ) -> ActionSpace:
        """Narrow the action space based on the last action."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)
