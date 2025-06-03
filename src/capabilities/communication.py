from __future__ import annotations
from typing import TYPE_CHECKING


from core.capability import Capability
from core.task import Task


# we use TYPE_CHECKING to avoid circular imports, this isn't actually an issue
# because this file is an interface and doesn't need to know about the Agent class
# on a code execution level there is no circular import because the implementations
# of these interfaces do not have this circular dependency
if TYPE_CHECKING:
    from core.agent import Agent


class CommunicationInterface(Capability):
    """An interface for the agent to communicate with other agents or the user."""

    # TODO: supported by Sprint 3
    def __init__(self):
        super().__init__("communication")

    def task_is_suitable(self, task: Task, agent: Agent) -> float:
        """Returns a value betwene 0 and 1 indicating how well the agent can perform the task."""
        raise NotImplementedError("bid_on_task not implemented")
