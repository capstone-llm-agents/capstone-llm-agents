"""A task for an agent to complete."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_mas.action_system.core.action_context import ActionContext
    from llm_mas.mas.agent import Agent


class Task:
    """A task for an agent to complete."""

    def __init__(self, description: str, action_context: "ActionContext") -> None:
        """Initialize the task with a description."""
        self.description = description
        self.completed = False
        self.action_context = action_context
        self.assigned_to: Agent | None = None
