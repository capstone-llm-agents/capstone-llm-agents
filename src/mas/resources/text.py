"""Basic text resource class."""

from pydantic import BaseModel


from mas.base_resource import BaseResource


class TextResource(BaseResource):
    """A resource representing a text string."""

    # text model
    class TextModel(BaseModel):
        """A model representing a text string."""

        text: str
        """The text to be represented by the resource."""

        def __init__(self, text: str):
            """
            Initialise the TextModel with a text string.

            Args:
                text (str): The text to be represented by the resource.
            """
            super().__init__(text=text)
            self.text = text

    def __init__(self, text: TextModel):
        """
        Initialise the TextResource with a text string.

        Args:
            text (str): The text to be represented by the resource.
        """
        super().__init__(text, alias="text")
        self.text = text

    @staticmethod
    def get_model_type() -> type[TextModel]:
        """
        Get the type of the model.

        Returns:
            type: The type of the model.
        """
        return TextResource.TextModel
