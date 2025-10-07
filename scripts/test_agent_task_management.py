"""Test script for agent task management enhancements."""

from unittest.mock import MagicMock

from llm_mas.communication.task.agent_task import Task
from llm_mas.communication.task.task_enums import TaskPriority, TaskStatus


def test_agent_task_stack_operations():
    """Test basic task stack operations."""
    print("Testing agent task stack operations...")

    # Create a mock agent with task_stack
    mock_agent = MagicMock()
    mock_agent.task_stack = []
    mock_context = MagicMock()

    # Create tasks
    task1 = Task(description="Task 1", action_context=mock_context, priority=TaskPriority.NORMAL)
    task2 = Task(description="Task 2", action_context=mock_context, priority=TaskPriority.HIGH)
    task3 = Task(description="Task 3", action_context=mock_context, priority=TaskPriority.LOW)

    # Add tasks to stack
    mock_agent.task_stack.append(task1)
    mock_agent.task_stack.append(task2)
    mock_agent.task_stack.append(task3)

    assert len(mock_agent.task_stack) == 3, "Should have 3 tasks"
    print("✓ Tasks added to stack")

    # Get current task (last one)
    current_task = mock_agent.task_stack[-1]
    assert current_task == task3, "Current task should be task3"
    print("✓ Current task retrieved")

    # Complete current task
    completed = mock_agent.task_stack.pop()
    assert completed == task3, "Completed task should be task3"
    assert len(mock_agent.task_stack) == 2, "Should have 2 tasks left"
    print("✓ Current task completed and removed from stack")

    print("Agent task stack operations test passed!\n")


def test_task_filtering_by_status():
    """Test filtering tasks by status."""
    print("Testing task filtering by status...")

    mock_context = MagicMock()

    # Create tasks with different statuses
    task1 = Task(description="Pending task", action_context=mock_context, priority=TaskPriority.NORMAL)
    task2 = Task(description="In progress task", action_context=mock_context, priority=TaskPriority.HIGH)
    task3 = Task(description="Completed task", action_context=mock_context, priority=TaskPriority.LOW)
    task4 = Task(description="Failed task", action_context=mock_context, priority=TaskPriority.CRITICAL)

    # Set different statuses
    task1.status = TaskStatus.PENDING
    task2.mark_in_progress()
    task3.mark_completed()
    task4.mark_failed("Test error")

    # Create task stack
    task_stack = [task1, task2, task3, task4]

    # Filter by status
    pending_tasks = [t for t in task_stack if t.is_pending()]
    in_progress_tasks = [t for t in task_stack if t.is_in_progress()]
    completed_tasks = [t for t in task_stack if t.is_completed()]
    failed_tasks = [t for t in task_stack if t.is_failed()]

    assert len(pending_tasks) == 1, "Should have 1 pending task"
    assert len(in_progress_tasks) == 1, "Should have 1 in-progress task"
    assert len(completed_tasks) == 1, "Should have 1 completed task"
    assert len(failed_tasks) == 1, "Should have 1 failed task"

    assert pending_tasks[0] == task1, "Pending task should be task1"
    assert in_progress_tasks[0] == task2, "In-progress task should be task2"
    assert completed_tasks[0] == task3, "Completed task should be task3"
    assert failed_tasks[0] == task4, "Failed task should be task4"

    print("✓ Tasks filtered by status correctly")
    print("Task filtering by status test passed!\n")


def test_task_filtering_by_priority():
    """Test filtering tasks by priority."""
    print("Testing task filtering by priority...")

    mock_context = MagicMock()

    # Create tasks with different priorities
    task1 = Task(description="Low priority", action_context=mock_context, priority=TaskPriority.LOW)
    task2 = Task(description="Normal priority", action_context=mock_context, priority=TaskPriority.NORMAL)
    task3 = Task(description="High priority", action_context=mock_context, priority=TaskPriority.HIGH)
    task4 = Task(description="Critical priority", action_context=mock_context, priority=TaskPriority.CRITICAL)

    # Create task stack
    task_stack = [task1, task2, task3, task4]

    # Filter by priority
    low_tasks = [t for t in task_stack if t.priority == TaskPriority.LOW]
    normal_tasks = [t for t in task_stack if t.priority == TaskPriority.NORMAL]
    high_tasks = [t for t in task_stack if t.priority == TaskPriority.HIGH]
    critical_tasks = [t for t in task_stack if t.priority == TaskPriority.CRITICAL]

    assert len(low_tasks) == 1, "Should have 1 low priority task"
    assert len(normal_tasks) == 1, "Should have 1 normal priority task"
    assert len(high_tasks) == 1, "Should have 1 high priority task"
    assert len(critical_tasks) == 1, "Should have 1 critical priority task"

    print("✓ Tasks filtered by priority correctly")
    print("Task filtering by priority test passed!\n")


def test_highest_priority_selection():
    """Test selecting highest priority pending task."""
    print("Testing highest priority pending task selection...")

    mock_context = MagicMock()

    # Create pending tasks with different priorities
    task1 = Task(description="Low priority", action_context=mock_context, priority=TaskPriority.LOW)
    task2 = Task(description="Normal priority", action_context=mock_context, priority=TaskPriority.NORMAL)
    task3 = Task(description="High priority", action_context=mock_context, priority=TaskPriority.HIGH)
    task4 = Task(description="Critical priority", action_context=mock_context, priority=TaskPriority.CRITICAL)

    # Mark one as completed and one as in progress
    task2.mark_completed()
    task4.mark_in_progress()

    # Create task stack
    task_stack = [task1, task2, task3, task4]

    # Get pending tasks only
    pending_tasks = [t for t in task_stack if t.is_pending()]

    # Find highest priority pending task
    if pending_tasks:
        highest_priority_task = max(pending_tasks, key=lambda t: t.priority.value)
        assert highest_priority_task == task3, "Highest priority pending task should be task3 (HIGH)"
        print("✓ Highest priority pending task selected correctly")
    else:
        raise AssertionError("Should have pending tasks")

    print("Highest priority task selection test passed!\n")


def test_task_assignment():
    """Test task assignment to agent."""
    print("Testing task assignment to agent...")

    mock_context = MagicMock()
    mock_agent = MagicMock()
    mock_agent.name = "Test Agent"

    # Create task
    task = Task(description="Test task", action_context=mock_context, priority=TaskPriority.NORMAL)

    # Initially unassigned
    assert task.assigned_to is None, "Task should be unassigned initially"
    print("✓ Task initially unassigned")

    # Assign to agent
    task.assigned_to = mock_agent
    assert task.assigned_to == mock_agent, "Task should be assigned to agent"
    print("✓ Task assigned to agent")

    print("Task assignment test passed!\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Running Agent Task Management Tests")
    print("=" * 60 + "\n")

    test_agent_task_stack_operations()
    test_task_filtering_by_status()
    test_task_filtering_by_priority()
    test_highest_priority_selection()
    test_task_assignment()

    print("=" * 60)
    print("All agent task management tests passed successfully! ✓")
    print("=" * 60)
