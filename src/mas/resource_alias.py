"""Manage the resource aliases."""

from mas.base_resource import BaseResource
from mas.resources.empty import EmptyResource
from mas.tasks.write_sentence import SentenceResource, TopicResource


class ResourceAlias:
    """
    Class to manage the resource aliases.

    Attributes:
        resource_aliases (dict[str, str]): Dictionary of resource aliases.
    """

    resource_aliases: dict[str, type[BaseResource]]
    """Dictionary of resource aliases."""

    def __init__(self):
        """
        Initialise the resource alias manager.
        """
        self.resource_aliases = {}

        # add aliases
        self.add_resource_alias("empty", EmptyResource)
        self.add_resource_alias("sentence", SentenceResource)
        self.add_resource_alias("topic", TopicResource)

    def add_resource_alias(self, alias: str, resource_type: type[BaseResource]):
        """
        Add a resource alias to the resource alias manager.

        Args:
            alias (str): The alias of the resource.
            resource_type (type[BaseResource]): The type of the resource.
        """
        if alias in self.resource_aliases:
            raise ValueError(f"Alias {alias} already exists.")

        self.resource_aliases[alias] = resource_type
