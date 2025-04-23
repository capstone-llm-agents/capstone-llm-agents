"""Module for BaseResource class"""

from pydantic import BaseModel


class BaseResource:
    """Base class for all resources in the system."""

    def __init__(self, model: BaseModel):
        """
        Initialise the BaseResource with a model.

        Args:
            model (BaseModel): The model to be used for the resource.
        """
        self.model = model
        """The model for the resource."""

    # TODO hacky refactor this later
    @staticmethod
    def get_model_type() -> type[BaseModel]:
        """
        Get the type of the model.

        Returns:
            type: The type of the model.
        """
        raise NotImplementedError(
            "This method should be implemented in a subclass of BaseResource."
        )
