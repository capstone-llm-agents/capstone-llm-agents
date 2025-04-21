"""Module for Task class"""

from mas.base_resource import BaseResource


class Task:
    """A Task is a unit of work that converts some input resource into some output resource."""

    def __init__(
        self, input_resource: type[BaseResource], output_resource: type[BaseResource]
    ):
        """
        Initialise the Task with input and output resources.

        Args:
            input_resource (type[BaseResource]): The input resource type for the task.
            output_resource (type[BaseResource]): The output resource type for the task.
        """
        self.input_resource = input_resource
        """The input resource type for the task."""

        self.output_resource = output_resource
        """The output resource type for the task."""

    def do_work(self, input_resource: BaseResource) -> BaseResource:
        """
        Perform the task using the input resource.

        Args:
            input_resource (BaseResource): The input resource for the task.

        Returns:
            BaseResource: The output resource after performing the task.
        """
        raise NotImplementedError("Subclasses should implement this method.")
