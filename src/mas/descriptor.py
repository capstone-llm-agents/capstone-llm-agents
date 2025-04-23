"""Module for descriptor class"""

from typing import Callable, Generic, Type, TypeVar
from mas.base_resource import BaseResource
from mas.task import Task

InputResource = TypeVar("InputResource", bound=BaseResource)
OutputResource = TypeVar("OutputResource", bound=BaseResource)


class Descriptor(
    Task[InputResource, OutputResource], Generic[InputResource, OutputResource]
):
    """A descriptor is a task that describes a resource."""

    def __init__(
        self,
        name: str,
        alias: str,
        description: str,
        input_resource: Type[InputResource],
        output_resource: Type[OutputResource],
        do_work: Callable[[InputResource], OutputResource],
    ):
        """
        Initialise the Descriptor with input and output resource types.

        Args:
            name (str): The name of the descriptor.
            alias (str): The alias of the descriptor for YAML.
            description (str): The description of the descriptor.
            input_resource (Type[InputResource]): The input resource type for the descriptor.
            output_resource (Type[OutputResource]): The output resource type for the descriptor.
        """
        super().__init__(name, description, input_resource, output_resource, do_work)
        self.alias = alias
