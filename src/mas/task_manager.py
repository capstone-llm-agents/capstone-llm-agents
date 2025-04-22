"""Module for the task manager"""

from mas.task import Task


class TaskManager:
    """
    A class representing a task manager in a multi-agent system (MAS).

    It provides methods to add, remove, and get tasks.
    """

    def __init__(self):
        """
        Initialise the task manager.
        """
        self.tasks: dict[str, Task] = {}
        """Dictionary of tasks in the system."""

    def add_task(self, task: Task):
        """
        Add a task to the task manager.

        Args:
            task (Task): The task to be added.
        """
        self.tasks[task.name] = task

    def remove_task(self, task_name: str):
        """
        Remove a task from the task manager.

        Args:
            task_name (str): The name of the task to be removed.
        """
        if task_name in self.tasks:
            del self.tasks[task_name]
        else:
            raise ValueError(f"Task with name {task_name} does not exist.")

    def get_task(self, task_name: str) -> Task:
        """
        Get a task from the task manager.

        Args:
            task_name (str): The name of the task to be retrieved.

        Returns:
            Task: The requested task.
        """
        return self.tasks.get(task_name)
