"""Module for MAS query input"""

from mas.base_resource import BaseResource
from mas.query.mas_query import ResourceArgModel
from mas.resource_manager import ResourceManager
from mas.resources.empty import EmptyResource


class MASQueryInput:
    """Class for MAS query input."""

    def __init__(
        self,
        input_query_models: list[dict[str, ResourceArgModel]],
        resource_manager: ResourceManager,
    ):
        """
        Initialise the MAS query input.

        Args:
            input_query_models (list[dict[str, ResourceArgModel]]): The input query models.
        """

        # resource id mapping
        self.resource_id_mapping: dict[tuple[type[BaseResource], int], BaseResource] = (
            {}
        )

        # iter over models
        for model in input_query_models:
            for key, value in model.items():

                # load type
                resource_type = resource_manager.get_resource_type(key)
                if resource_type is None:
                    raise ValueError(
                        f"Resource type {key} not found in resource manager."
                    )

                # if value is None
                if value.args is None:
                    raise ValueError(f"Resource model {key} has no arguments.")

                resource = resource_type(**value.args)

                # add resource to mapping
                self.resource_id_mapping[(resource_type, value.id)] = resource

        # add empty resource
        empty_resource = EmptyResource(EmptyResource.EmptyModel())
        self.resource_id_mapping[(EmptyResource, 1)] = empty_resource
