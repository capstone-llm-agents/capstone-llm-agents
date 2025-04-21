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
