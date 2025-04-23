"""Module for BaseResource class"""

from pydantic import BaseModel


class BaseResource:
    """Base class for all resources in the system."""

    def __init__(self, model: BaseModel, alias: str):
        """
        Initialise the BaseResource with a model.

        Args:
            model (BaseModel): The model to be used for the resource.
            alias (str): The alias of the resource for YAML.
        """
        self.model = model
        """The model for the resource."""
        self.alias = alias
        """The alias of the resource for YAML."""

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
