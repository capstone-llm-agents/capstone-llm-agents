"""Module for the resource manager"""

from mas.base_resource import BaseResource


class ResourceManager:
    """
    A class representing a resource manager in a multi-agent system (MAS).

    It provides methods to add, remove, and get resources.
    """

    def __init__(self):
        """
        Initialise the resource manager.
        """
        self.resources: dict[int, BaseResource] = {}
        """Dictionary of resources in the system."""

        self.resource_types: dict[str, type[BaseResource]] = {}
        """Dictionary of resource types in the system."""

        self.resource_counter = 0
        """Counter for resource IDs."""

    def add_resource(self, resource: BaseResource):
        """
        Add a resource to the resource manager.

        Args:
            resource (BaseResource): The resource to be added.
        """
        self.resource_counter += 1
        self.resources[self.resource_counter] = resource

    def remove_resource(self, resource_id: int):
        """
        Remove a resource from the resource manager.

        Args:
            resource_id (int): The ID of the resource to be removed.
        """
        if resource_id in self.resources:
            del self.resources[resource_id]
        else:
            raise ValueError(f"Resource with ID {resource_id} does not exist.")

    def get_resource(self, resource_id: int) -> BaseResource:
        """
        Get a resource from the resource manager.

        Args:
            resource_id (int): The ID of the resource to be retrieved.

        Returns:
            BaseResource: The requested resource.
        """
        return self.resources.get(resource_id)
