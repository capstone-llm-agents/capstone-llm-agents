"""Module for parameter template class."""

from pydantic import BaseModel
from mas.base_resource import BaseResource
from mas.resources.params import ParamsResource
from mas.resources.text import TextResource


class ParamTemplateResource(BaseResource):
    """A resource representing a parameter template."""

    # param template model
    class ParamTemplateModel(BaseModel):
        """A model representing a parameter template."""

        template_str: TextResource.TextModel
        """The template string to be represented by the resource."""
        params: ParamsResource.ParamsModel
        """The parameters to be replaced in the template."""

    def __init__(self, template: ParamTemplateModel):
        """
        Initialise the ParamTemplateResource with a template string and parameters.

        Args:
            template (ParamTemplateModel): The template string and parameters to be represented by the resource.
        """
        super().__init__(template, alias="param_template")
        self.template = template

    @staticmethod
    def get_model_type() -> type[ParamTemplateModel]:
        """
        Get the type of the model.

        Returns:
            type: The type of the model.
        """
        return ParamTemplateResource.ParamTemplateModel
