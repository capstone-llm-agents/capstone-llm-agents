"""Test script for task automation enhancements."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

from llm_mas.communication.task.agent_task import Task
from llm_mas.communication.task.task_enums import TaskPriority, TaskStatus


def test_task_status_tracking():
    """Test task status tracking."""
    print("Testing task status tracking...")

    # Create a task with mock context
    mock_context = MagicMock()
    task = Task(description="Test task", action_context=mock_context, priority=TaskPriority.HIGH)

    # Check initial status
    assert task.status == TaskStatus.PENDING, "Task should start as PENDING"
    assert task.is_pending(), "Task should be pending"
    assert not task.is_in_progress(), "Task should not be in progress"
    assert not task.is_completed(), "Task should not be completed"
    assert not task.is_failed(), "Task should not be failed"
    print("✓ Initial status is PENDING")

    # Mark as in progress
    task.mark_in_progress()
    assert task.status == TaskStatus.IN_PROGRESS, "Task should be IN_PROGRESS"
    assert task.is_in_progress(), "Task should be in progress"
    assert task.started_at is not None, "Task should have a start time"
    print("✓ Task marked as IN_PROGRESS")

    # Mark as completed
    task.mark_completed()
    assert task.status == TaskStatus.COMPLETED, "Task should be COMPLETED"
    assert task.is_completed(), "Task should be completed"
    assert task.completed, "Task.completed should be True"
    assert task.completed_at is not None, "Task should have a completion time"
    print("✓ Task marked as COMPLETED")

    print("Task status tracking test passed!\n")


def test_task_failure_tracking():
    """Test task failure tracking."""
    print("Testing task failure tracking...")

    # Create a task with mock context
    mock_context = MagicMock()
    task = Task(description="Failing task", action_context=mock_context, priority=TaskPriority.NORMAL)

    # Mark as in progress
    task.mark_in_progress()
    assert task.is_in_progress(), "Task should be in progress"
    print("✓ Task marked as IN_PROGRESS")

    # Mark as failed
    error_msg = "Test error message"
    task.mark_failed(error_msg)
    assert task.status == TaskStatus.FAILED, "Task should be FAILED"
    assert task.is_failed(), "Task should be failed"
    assert not task.completed, "Task.completed should be False"
    assert task.error_message == error_msg, "Task should have error message"
    assert task.completed_at is not None, "Task should have a completion time"
    print("✓ Task marked as FAILED with error message")

    print("Task failure tracking test passed!\n")


def test_task_priority():
    """Test task priority levels."""
    print("Testing task priority levels...")

    mock_context = MagicMock()

    # Create tasks with different priorities
    low_task = Task(description="Low priority", action_context=mock_context, priority=TaskPriority.LOW)
    normal_task = Task(description="Normal priority", action_context=mock_context, priority=TaskPriority.NORMAL)
    high_task = Task(description="High priority", action_context=mock_context, priority=TaskPriority.HIGH)
    critical_task = Task(description="Critical priority", action_context=mock_context, priority=TaskPriority.CRITICAL)

    assert low_task.priority == TaskPriority.LOW, "Task should have LOW priority"
    assert normal_task.priority == TaskPriority.NORMAL, "Task should have NORMAL priority"
    assert high_task.priority == TaskPriority.HIGH, "Task should have HIGH priority"
    assert critical_task.priority == TaskPriority.CRITICAL, "Task should have CRITICAL priority"

    # Check priority values for sorting
    assert TaskPriority.LOW.value < TaskPriority.NORMAL.value, "LOW should be less than NORMAL"
    assert TaskPriority.NORMAL.value < TaskPriority.HIGH.value, "NORMAL should be less than HIGH"
    assert TaskPriority.HIGH.value < TaskPriority.CRITICAL.value, "HIGH should be less than CRITICAL"

    print("✓ All priority levels working correctly")
    print("Task priority test passed!\n")


def test_task_timestamps():
    """Test task timestamp tracking."""
    print("Testing task timestamps...")

    mock_context = MagicMock()
    task = Task(description="Timestamp test", action_context=mock_context)

    # Check creation time
    assert task.created_at is not None, "Task should have a creation time"
    assert task.started_at is None, "Task should not have a start time initially"
    assert task.completed_at is None, "Task should not have a completion time initially"
    created_time = task.created_at
    print("✓ Creation timestamp recorded")

    # Mark as in progress and check start time
    task.mark_in_progress()
    assert task.started_at is not None, "Task should have a start time"
    assert task.started_at >= created_time, "Start time should be after creation time"
    started_time = task.started_at
    print("✓ Start timestamp recorded")

    # Mark as completed and check completion time
    task.mark_completed()
    assert task.completed_at is not None, "Task should have a completion time"
    assert task.completed_at >= started_time, "Completion time should be after start time"
    print("✓ Completion timestamp recorded")

    print("Task timestamps test passed!\n")


def test_task_default_priority():
    """Test task default priority."""
    print("Testing task default priority...")

    mock_context = MagicMock()
    task = Task(description="Default priority test", action_context=mock_context)

    assert task.priority == TaskPriority.NORMAL, "Task should have NORMAL priority by default"
    print("✓ Default priority is NORMAL")

    print("Task default priority test passed!\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Running Task Automation Tests")
    print("=" * 60 + "\n")

    test_task_status_tracking()
    test_task_failure_tracking()
    test_task_priority()
    test_task_timestamps()
    test_task_default_priority()

    print("=" * 60)
    print("All tests passed successfully! ✓")
    print("=" * 60)
