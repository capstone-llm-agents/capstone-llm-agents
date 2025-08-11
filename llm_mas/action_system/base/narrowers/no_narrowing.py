"""The no narrowing policy that does not narrow the action space."""

from typing import override

from llm_mas.action_system.core.action_narrower import ActionNarrower
from llm_mas.action_system.core.action_space import ActionSpace
from llm_mas.agent.workspace import Workspace


class NoNarrowingNarrower(ActionNarrower):
    """A policy that does not narrow the action space at all."""

    @override
    def narrow(self, workspace: Workspace, action_space: ActionSpace) -> ActionSpace:
        """Return the original action space without any narrowing."""
        return action_space.copy()
