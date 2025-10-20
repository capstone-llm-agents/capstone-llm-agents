# Task Automation Enhancements

This document describes the task automation enhancements added to the Capstone LLM Agents repository.

## Overview

The task automation system has been enhanced with comprehensive status tracking, priority management, and timestamp recording to improve task management and automation capabilities for agents.

## New Features

### 1. Task Status Tracking

Tasks now have explicit status tracking through the `TaskStatus` enum:
- `PENDING` - Task is waiting to be started
- `IN_PROGRESS` - Task is currently being worked on
- `COMPLETED` - Task has been successfully completed
- `FAILED` - Task has failed with an error

**Usage:**
```python
from llm_mas.communication.task.agent_task import Task
from llm_mas.communication.task.task_enums import TaskStatus

task = Task(description="Example task", action_context=context)
task.mark_in_progress()  # Start working on task
task.mark_completed()    # Mark as completed
# or
task.mark_failed("Error message")  # Mark as failed
```

### 2. Task Priority System

Tasks can be prioritized using the `TaskPriority` enum:
- `LOW` (value: 1)
- `NORMAL` (value: 2) - Default priority
- `HIGH` (value: 3)
- `CRITICAL` (value: 4)

**Usage:**
```python
from llm_mas.communication.task.task_enums import TaskPriority

high_priority_task = Task(
    description="Urgent task",
    action_context=context,
    priority=TaskPriority.HIGH
)
```

### 3. Timestamp Tracking

Tasks automatically track important timestamps:
- `created_at` - When the task was created
- `started_at` - When the task was started (set when marked as IN_PROGRESS)
- `completed_at` - When the task was completed or failed

All timestamps use UTC timezone for consistency.

### 4. Enhanced Agent Task Management

The `Agent` class now includes helper methods for better task management:

```python
# Get tasks by status
pending_tasks = agent.get_pending_tasks()
in_progress_tasks = agent.get_in_progress_tasks()
completed_tasks = agent.get_completed_tasks()
failed_tasks = agent.get_failed_tasks()

# Get tasks by priority
high_priority_tasks = agent.get_tasks_by_priority(TaskPriority.HIGH)

# Get the highest priority pending task
next_task = agent.get_highest_priority_pending_task()
```

### 5. Automatic Status Updates

The system automatically updates task status at key points:
- When a task is added to an agent, it's automatically assigned to that agent
- When an agent starts working (`agent.work()`), the current task is marked as IN_PROGRESS
- When the `DefaultTaskHandler` executes a task, it marks it as IN_PROGRESS, then COMPLETED or FAILED
- When `complete_current_task()` is called, it marks the task as COMPLETED if not already marked

## API Changes

### Task Class

**New Constructor Parameter:**
```python
def __init__(
    self,
    description: str,
    action_context: ActionContext,
    priority: TaskPriority = TaskPriority.NORMAL,  # NEW
) -> None:
```

**New Methods:**
- `mark_in_progress()` - Mark task as in progress
- `mark_completed()` - Mark task as completed
- `mark_failed(error_message: str)` - Mark task as failed
- `is_pending()` - Check if task is pending
- `is_in_progress()` - Check if task is in progress
- `is_completed()` - Check if task is completed
- `is_failed()` - Check if task is failed

**New Attributes:**
- `priority: TaskPriority` - Task priority level
- `status: TaskStatus` - Current task status
- `created_at: datetime` - When task was created
- `started_at: datetime | None` - When task was started
- `completed_at: datetime | None` - When task was completed/failed
- `error_message: str | None` - Error message if task failed

### Agent Class

**Enhanced Methods:**
- `add_task(task: Task)` - Now automatically assigns task to agent
- `complete_current_task()` - Now marks task as completed if not already marked
- `work(context: ActionContext)` - Now marks current task as IN_PROGRESS

**New Methods:**
- `get_pending_tasks()` - Get all pending tasks
- `get_in_progress_tasks()` - Get all in-progress tasks
- `get_completed_tasks()` - Get all completed tasks
- `get_failed_tasks()` - Get all failed tasks
- `get_tasks_by_priority(priority: TaskPriority)` - Get tasks by priority
- `get_highest_priority_pending_task()` - Get highest priority pending task

## Testing

Two comprehensive test suites have been added:

1. **`scripts/test_task_automation.py`** - Tests task status, priority, and timestamp features
2. **`scripts/test_agent_task_management.py`** - Tests agent task management helper methods

Run tests with:
```bash
python -m scripts.test_task_automation
python -m scripts.test_agent_task_management
```

## Migration Guide

### For Existing Code

The changes are backward compatible. Existing code will continue to work because:
- The `priority` parameter has a default value (`TaskPriority.NORMAL`)
- Existing task operations still function as before
- The `completed` boolean flag is maintained for backward compatibility

### Recommended Updates

To take advantage of the new features:

1. **Add priority to task creation:**
```python
# Before
task = Task(description="My task", action_context=context)

# After (recommended)
task = Task(
    description="My task",
    action_context=context,
    priority=TaskPriority.HIGH  # Add priority
)
```

2. **Check task status instead of just `completed` flag:**
```python
# Before
if task.completed:
    # ...

# After (recommended)
if task.is_completed():
    # ...
```

3. **Use new agent helper methods:**
```python
# Before
pending = [t for t in agent.task_stack if not t.completed]

# After (recommended)
pending = agent.get_pending_tasks()
```

## Benefits

1. **Better Task Tracking** - Know exactly what state each task is in
2. **Priority Management** - Focus on high-priority tasks first
3. **Error Handling** - Track which tasks failed and why
4. **Time Analysis** - Analyze how long tasks take with timestamps
5. **Improved Automation** - Agents can intelligently select which task to work on next
6. **Debugging** - Easier to debug task execution with detailed status information

## Files Modified

- `llm_mas/communication/task/task_enums.py` - NEW: Task status and priority enums
- `llm_mas/communication/task/agent_task.py` - Enhanced with status, priority, timestamps
- `llm_mas/communication/default_interface.py` - Updated DefaultTaskHandler to track status
- `llm_mas/mas/agent.py` - Added task management helper methods
- `scripts/test_task_automation.py` - NEW: Task automation tests
- `scripts/test_agent_task_management.py` - NEW: Agent task management tests
