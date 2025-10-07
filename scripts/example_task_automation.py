"""Example script demonstrating the new task automation features."""

from datetime import datetime
from unittest.mock import MagicMock

from llm_mas.communication.task.agent_task import Task
from llm_mas.communication.task.task_enums import TaskPriority, TaskStatus


def main():
    """Demonstrate task automation features."""
    print("=" * 70)
    print("Task Automation Features Demo")
    print("=" * 70)
    print()

    # Create mock context
    mock_context = MagicMock()

    # 1. Create tasks with different priorities
    print("1. Creating tasks with different priorities...")
    print("-" * 70)
    
    task1 = Task(
        description="Update documentation",
        action_context=mock_context,
        priority=TaskPriority.LOW,
    )
    
    task2 = Task(
        description="Fix critical bug",
        action_context=mock_context,
        priority=TaskPriority.CRITICAL,
    )
    
    task3 = Task(
        description="Add new feature",
        action_context=mock_context,
        priority=TaskPriority.NORMAL,
    )
    
    task4 = Task(
        description="Review pull request",
        action_context=mock_context,
        priority=TaskPriority.HIGH,
    )
    
    tasks = [task1, task2, task3, task4]
    
    for task in tasks:
        print(f"  • {task.description:<30} Priority: {task.priority.name:<10} Status: {task.status.value}")
    print()

    # 2. Demonstrate status transitions
    print("2. Demonstrating task status transitions...")
    print("-" * 70)
    
    demo_task = Task(
        description="Example task",
        action_context=mock_context,
        priority=TaskPriority.NORMAL,
    )
    
    print(f"  Initial status: {demo_task.status.value}")
    print(f"  Is pending? {demo_task.is_pending()}")
    print()
    
    demo_task.mark_in_progress()
    print(f"  After mark_in_progress(): {demo_task.status.value}")
    print(f"  Is in progress? {demo_task.is_in_progress()}")
    print(f"  Started at: {demo_task.started_at.strftime('%Y-%m-%d %H:%M:%S UTC') if demo_task.started_at else 'N/A'}")
    print()
    
    demo_task.mark_completed()
    print(f"  After mark_completed(): {demo_task.status.value}")
    print(f"  Is completed? {demo_task.is_completed()}")
    print(f"  Completed at: {demo_task.completed_at.strftime('%Y-%m-%d %H:%M:%S UTC') if demo_task.completed_at else 'N/A'}")
    print()

    # 3. Demonstrate failure tracking
    print("3. Demonstrating task failure tracking...")
    print("-" * 70)
    
    failed_task = Task(
        description="Task that will fail",
        action_context=mock_context,
        priority=TaskPriority.HIGH,
    )
    
    failed_task.mark_in_progress()
    failed_task.mark_failed("Network connection timeout")
    
    print(f"  Task status: {failed_task.status.value}")
    print(f"  Is failed? {failed_task.is_failed()}")
    print(f"  Error message: {failed_task.error_message}")
    print()

    # 4. Simulate agent task management
    print("4. Simulating agent task management...")
    print("-" * 70)
    
    # Create a mock agent with task stack
    mock_agent = MagicMock()
    mock_agent.task_stack = []
    
    # Add tasks to agent
    for task in tasks:
        task.assigned_to = mock_agent
        mock_agent.task_stack.append(task)
    
    print(f"  Total tasks: {len(mock_agent.task_stack)}")
    print()
    
    # Simulate working on tasks
    task2.mark_in_progress()  # Critical bug (highest priority)
    task4.mark_in_progress()  # Review PR (high priority)
    task1.mark_completed()    # Documentation (low priority)
    
    # Filter tasks by status
    pending_tasks = [t for t in mock_agent.task_stack if t.is_pending()]
    in_progress_tasks = [t for t in mock_agent.task_stack if t.is_in_progress()]
    completed_tasks = [t for t in mock_agent.task_stack if t.is_completed()]
    
    print(f"  Pending tasks: {len(pending_tasks)}")
    for task in pending_tasks:
        print(f"    - {task.description} (Priority: {task.priority.name})")
    print()
    
    print(f"  In progress tasks: {len(in_progress_tasks)}")
    for task in in_progress_tasks:
        print(f"    - {task.description} (Priority: {task.priority.name})")
    print()
    
    print(f"  Completed tasks: {len(completed_tasks)}")
    for task in completed_tasks:
        print(f"    - {task.description} (Priority: {task.priority.name})")
    print()

    # 5. Demonstrate priority-based selection
    print("5. Demonstrating priority-based task selection...")
    print("-" * 70)
    
    pending = [t for t in mock_agent.task_stack if t.is_pending()]
    if pending:
        highest_priority_task = max(pending, key=lambda t: t.priority.value)
        print(f"  Highest priority pending task: {highest_priority_task.description}")
        print(f"  Priority level: {highest_priority_task.priority.name}")
    else:
        print("  No pending tasks available")
    print()

    # 6. Demonstrate time tracking
    print("6. Demonstrating time tracking...")
    print("-" * 70)
    
    if completed_tasks:
        for task in completed_tasks:
            if task.completed_at and task.created_at:
                duration = (task.completed_at - task.created_at).total_seconds()
                print(f"  Task: {task.description}")
                print(f"    Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                print(f"    Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                print(f"    Duration: {duration:.2f} seconds")
    print()

    print("=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
