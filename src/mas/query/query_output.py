"""Module for MAS query output"""

from mas.base_resource import BaseResource
from mas.query.mas_query import ResourceModel
from mas.resource_manager import ResourceManager


class MASQueryOutput:
    """Class for MAS query output."""

    def __init__(
        self,
        output_query_models: list[dict[str, ResourceModel]],
        resource_manager: ResourceManager,
    ):
        """
        Initialise the MAS query output.

        Args:
            output_query_models (list[dict[str, ResourceModel]]): The output query models.
            resource_manager (ResourceManager): The resource manager.
        """

        # output resources
        self.output_resources: set[tuple[type[BaseResource], int]] = set()

        # iter over models
        for model in output_query_models:
            for key, value in model.items():

                # load type
                resource_type = resource_manager.get_resource_type(key)
                if resource_type is None:
                    raise ValueError(
                        f"Resource type {key} not found in resource manager."
                    )

                # add output resource
                self.output_resources.add((resource_type, value.id))
