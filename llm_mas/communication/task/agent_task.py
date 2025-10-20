"""A task for an agent to complete."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.communication.task.task_enums import TaskPriority, TaskStatus

if TYPE_CHECKING:
    from llm_mas.mas.agent import Agent


class Task:
    """A task for an agent to complete."""

    def __init__(
        self,
        description: str,
        action_context: ActionContext,
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> None:
        """Initialize the task with a description."""
        self.description = description
        self.completed = False
        self.action_context = action_context
        self.assigned_to: Agent | None = None
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now(UTC)
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None
        self.error_message: str | None = None

    def mark_in_progress(self) -> None:
        """Mark the task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now(UTC)

    def mark_completed(self) -> None:
        """Mark the task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed = True
        self.completed_at = datetime.now(UTC)

    def mark_failed(self, error_message: str) -> None:
        """Mark the task as failed with an error message."""
        self.status = TaskStatus.FAILED
        self.completed = False
        self.completed_at = datetime.now(UTC)
        self.error_message = error_message

    def is_pending(self) -> bool:
        """Check if the task is pending."""
        return self.status == TaskStatus.PENDING

    def is_in_progress(self) -> bool:
        """Check if the task is in progress."""
        return self.status == TaskStatus.IN_PROGRESS

    def is_completed(self) -> bool:
        """Check if the task is completed."""
        return self.status == TaskStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if the task is failed."""
        return self.status == TaskStatus.FAILED
