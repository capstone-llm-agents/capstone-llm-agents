"""Module for the resource manager"""

from mas.base_resource import BaseResource


class ResourceManager:
    """
    A class representing a resource manager in a multi-agent system (MAS).

    It provides methods to add, remove, and get resources.
    """

    resources: dict[type[BaseResource], set[int]]
    """Dictionary of resources in the system."""

    resource_types: dict[str, type[BaseResource]]
    """Dictionary of name to resource types in the system."""

    # reverse dict
    resource_types_reverse: dict[type[BaseResource], str]
    """Dictionary of resource types to mapped name in the system."""

    def __init__(self):
        """
        Initialise the resource manager.
        """
        self.resources = {}

        self.resource_types = {}

        self.resource_types_reverse = {}

    def add_resource(self, resource: type[BaseResource], resource_id: int):
        """
        Add a resource to the resource manager.

        Args:
            resource (type[BaseResource]): The resource to be added.
            resource_id (int): The ID of the resource to be added.
        """
        if resource not in self.resources:
            self.resources[resource] = set()

        # check if it is already in the resource
        if resource_id in self.resources[resource]:
            raise ValueError(
                f"Resource {resource} with ID {resource_id} already exists in the resource manager."
            )

        self.resources[resource].add(resource_id)

    def remove_resource(self, resource: type[BaseResource], resource_id: int):
        """
        Remove a resource from the resource manager.

        Args:
            resource (type[BaseResource]): The resource to be removed.
            resource_id (int): The ID of the resource to be removed.
        """
        if resource not in self.resources:
            raise ValueError(
                f"Resource {resource} with ID {resource_id} does not exist in the resource manager."
            )

        self.resources[resource].remove(resource_id)

    def get_resources(self) -> dict[type[BaseResource], set[int]]:
        """
        Get all resources in the resource manager.

        Returns:
            resources (dict[type[BaseResource], set[int]]): A dictionary of all resources in the resource manager.
        """
        return self.resources

    def get_resource_type(self, resource_name: str) -> type[BaseResource] | None:
        """
        Get a resource type by its name from the resource manager.

        Args:
            resource_name (str): The name of the resource type to be retrieved.

        Returns:
            resource_type (type[BaseResource]): The requested resource type.
        """
        return self.resource_types.get(resource_name)

    def add_resource_type(
        self, resource_type_name: str, resource_type: type[BaseResource]
    ):
        """
        Add a resource type to the resource manager.

        Args:
            resource_type (type[BaseResource]): The resource type to be added.
        """
        self.resource_types[resource_type_name] = resource_type
        self.resource_types_reverse[resource_type] = resource_type_name

    def convert_resource_tuple_to_str(
        self,
        resource_tuple: tuple[type[BaseResource], int],
    ) -> str:
        """
        Convert a resource tuple to a string.

        Args:
            resource_tuple (tuple[type[BaseResource], int]): The resource tuple to be converted.

        Returns:
            str: The string representation of the resource tuple.
        """
        # get name from reverse dict
        resource_name = self.resource_types_reverse.get(resource_tuple[0], None)

        if resource_name is None:
            raise ValueError(
                f"Resource type {resource_tuple[0]} not found in resource manager."
            )

        return f"{resource_name}_{resource_tuple[1]}"
