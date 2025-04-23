"""Module for ParmsResource class."""

from typing import Any
from pydantic import BaseModel
from mas.base_resource import BaseResource


class ParamsResource(BaseResource):
    """A resource representing a set of parameters."""

    # params model
    class ParamsModel(BaseModel):
        """A model representing a set of parameters."""

        params: dict[str, Any]
        """The parameters to be represented by the resource."""

    def __init__(self, params: ParamsModel):
        """
        Initialise the ParamsResource with a set of parameters.

        Args:
            params (dict): The parameters to be represented by the resource.
        """
        super().__init__(params)
        self.params = params

    @staticmethod
    def get_model_type() -> type[ParamsModel]:
        """
        Get the type of the model.

        Returns:
            type: The type of the model.
        """
        return ParamsResource.ParamsModel
