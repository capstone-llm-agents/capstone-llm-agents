"""Module for a Plan class"""

from typing import TypeVar, Generic
from mas.base_resource import BaseResource
from mas.task import InputResource, Task

PlanOutputResource = TypeVar("PlanOutputResource", bound=BaseResource)


class Plan(Generic[PlanOutputResource]):
    """A Plan is a sequence of Tasks to be completed."""

    def __init__(self, tasks: list[Task]):
        """
        Initialise the Plan with a list of tasks.

        Args:
            tasks (list[Task]): The list of tasks to be completed in the plan.
        """
        self.tasks = tasks

    def add_task(self, task: Task):
        """Add a task to the plan.

        Args:
            task (Task): The task to be added to the plan.

        """
        self.tasks.append(task)

    def verify_plan(self, initial_input: type[InputResource]) -> bool:
        """
        Verify the plan to ensure that the output and input resources of the tasks are compatible.

        Args:
            initial_input (type[InputResource]): The initial input resource for the plan.
        Returns:
            bool: True if the plan is valid, False otherwise.
        Raises:
            ValueError: If the input resource is not compatible with the task.
        """
        input_res = initial_input

        for task in self.tasks:
            if not isinstance(input_res, task.get_input_resource()):
                raise ValueError(
                    f"Input resource {input_res} is not compatible with task {task}"
                )

            input_res = task.get_output_resource()

        return True

    def execute(self, initial_input: InputResource) -> PlanOutputResource:
        """
        Execute the plan using the initial input resource.

        Args:
            initial_input (InputResource): The initial input resource for the plan.

        Returns:
            PlanOutputResource: The output resource after executing the plan.
        """
        if len(self.tasks) == 0:
            raise ValueError("No tasks in the plan to execute.")

        self.verify_plan(type(initial_input))

        input_res = initial_input

        for task in self.tasks:
            input_res = task.do_work(input_res)

        final_task = self.tasks[-1]

        # assert
        assert isinstance(
            input_res, final_task.get_output_resource()
        ), f"Output resource {input_res} is not compatible with task {final_task}"

        return input_res
