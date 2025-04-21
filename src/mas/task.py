"""Module for Task class"""

from typing import Callable, Type, TypeVar, Generic
from mas.base_resource import BaseResource

# generic type variables for input and output resource types
InputResource = TypeVar("InputResource", bound=BaseResource)
OutputResource = TypeVar("OutputResource", bound=BaseResource)


class Task(Generic[InputResource, OutputResource]):
    """A Task is a unit of work that converts some input resource into some output resource."""

    def __init__(
        self,
        input_resource: Type[InputResource],
        output_resource: Type[OutputResource],
        do_work: Callable[[InputResource], OutputResource],
    ):
        """
        Initialise the Task with input and output resource types.

        Args:
            input_resource (Type[InputResource]): The input resource type for the task.
            output_resource (Type[OutputResource]): The output resource type for the task.
        """
        self.input_resource = input_resource
        """The input resource type for the task."""

        self.output_resource = output_resource
        """The output resource type for the task."""
        self.do_work_callable = do_work

    def do_work(self, input_resource: InputResource) -> OutputResource:
        """
        Perform the task using the input resource.

        Args:
            input_resource (InputResource): The input resource for the task.

        Returns:
            OutputResource: The output resource after performing the task.
        """
        return self.do_work_callable(input_resource)

    def get_input_resource(self) -> Type[InputResource]:
        """
        Get the input resource type for the task.

        Returns:
            Type[InputResource]: The input resource type for the task.
        """
        return self.input_resource

    def get_output_resource(self) -> Type[OutputResource]:
        """
        Get the output resource type for the task.

        Returns:
            Type[OutputResource]: The output resource type for the task.
        """
        return self.output_resource
