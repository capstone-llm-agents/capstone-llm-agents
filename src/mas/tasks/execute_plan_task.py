"""A task that executes a plan of tasks"""

from typing import Generic, Type, TypeVar
from mas.base_resource import BaseResource
from mas.task import Task
from mas.plan import Plan

# generic type variables for input and output resource types
InputResource = TypeVar("InputResource", bound=BaseResource)
OutputResource = TypeVar("OutputResource", bound=BaseResource)


class ExecutePlanTask(
    Task[InputResource, OutputResource], Generic[InputResource, OutputResource]
):
    """A task that executes a plan of tasks."""

    def __init__(
        self,
        input_resource: Type[InputResource],
        output_resource: Type[OutputResource],
        plan: Plan,
    ):
        """
        Initialise the ExecutePlanTask with a plan.

        Args:
            plan (Plan): The plan to be executed.
        """
        super().__init__(input_resource, output_resource, self.execute_plan)
        self.plan = plan

    def execute_plan(self, input_resource: InputResource) -> OutputResource:
        """
        Execute the plan using the input resource.

        Args:
            input_resource (InputResource): The input resource for the task.

        Returns:
            OutputResource: The output resource after executing the plan.
        """
        self.plan.verify_plan(type(input_resource))

        return self.plan.execute(input_resource)
