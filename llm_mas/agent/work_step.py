"""The work step module defines the steps an agent takes to perform work in the workspace."""

from llm_mas.action_system.core.action import Action


class Work:
    """Some work that the agent is doing during the step."""

    def __init__(self, name: str) -> None:
        """Initialize the work with a name."""
        self.name = name
        self.content = ""


class WorkStep:
    """A work step represents a single step of progress an agent has made in the workspace."""

    def __init__(self, name: str, work: Work | None = None) -> None:
        """Initialize the work step."""
        self.name = name
        self.complete = False
        self.work = work

    def mark_complete(self) -> None:
        """Mark the work step as complete."""
        self.complete = True


class SelectingActionWorkStep(WorkStep):
    """A work step that represents selecting an action to perform."""

    def __init__(self) -> None:
        """Initialize the selecting action work step."""
        super().__init__(name="Selecting Action")


class PerformingActionWorkStep(WorkStep):
    """A work step that represents performing an action."""

    def __init__(self, action: Action) -> None:
        """Initialize the performing action work step."""
        super().__init__(name=f"Running Action: {action.name}")
        self.action = action
