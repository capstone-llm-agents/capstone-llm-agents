"""Module for a task where the output resource is dependent on a specific instance of the input resource."""

from mas.base_resource import BaseResource
from mas.resource_manager import ResourceManager
from mas.task import Task


class DependentTask:
    """A task where the output resource is dependent on a specific instance of the input resource."""

    def __init__(
        self,
        task: Task,
        input_resource_tuple: tuple[type[BaseResource], int],
        output_resource_tuple: tuple[type[BaseResource], int],
    ):
        """
        Initialise the DependentTask with a task and an input resource tuple.

        Args:
            task (Task): The task to be executed.
            input_resource_tuple (tuple[type[BaseResource], int]): The input resource tuple.
            output_resource_tuple (tuple[type[BaseResource], int]): The output resource tuple.
        """

        self.task = task
        self.input_resource_tuple = input_resource_tuple
        self.output_resource_tuple = output_resource_tuple

    def to_dependent_str(self, resource_manager: ResourceManager) -> str:
        """
        Convert the dependent task to a string representation.

        Args:
            resource_manager (ResourceManager): The resource manager for the MAS.

        Returns:
            str: The string representation of the dependent task.
        """

        input_resource_str = resource_manager.convert_resource_tuple_to_str(
            self.input_resource_tuple
        )

        output_resource_str = resource_manager.convert_resource_tuple_to_str(
            self.output_resource_tuple
        )

        return f"{self.task.name}({input_resource_str}) -> {output_resource_str}"
