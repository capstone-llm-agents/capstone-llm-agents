"""Empty resource"""

from pydantic import BaseModel
from mas.base_resource import BaseResource


class EmptyResource(BaseResource):
    """A resource representing an empty resource."""

    # empty model
    class EmptyModel(BaseModel):
        """A model representing an empty resource."""

        unused_property: str

        def __init__(self):
            """
            Initialise the EmptyModel.
            """
            super().__init__(unused_property="unused")

    def __init__(self, empty: EmptyModel):
        """
        Initialise the EmptyResource with an empty model.

        Args:
            empty (EmptyModel): The empty model to be represented by the resource.
        """
        super().__init__(empty, alias="empty")
        self.empty = empty

    @staticmethod
    def get_model_type() -> type[EmptyModel]:
        """
        Get the type of the model.

        Returns:
            type: The type of the model.
        """
        return EmptyResource.EmptyModel
