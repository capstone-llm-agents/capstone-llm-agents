"""Enums for task management."""

from enum import Enum


class TaskStatus(Enum):
    """Status of a task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(Enum):
    """Priority level of a task."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
