"""Module for task that parameterises a string"""

from mas.task import Task

from mas.resources.text import TextResource
from mas.resources.param_template import ParamTemplateResource


class ParamStringTask(Task[ParamTemplateResource, TextResource]):
    """A task that parameterises a string using a template and parameters."""

    def __init__(self):
        """
        Initialise the ParamStringTask with input and output resource types.
        """
        super().__init__(
            "ParamStringTask",
            "A task that parameterises a string using a template and parameters.",
            ParamTemplateResource,
            TextResource,
            self.parameterise_string,
        )

    def parameterise_string(
        self, input_resource: ParamTemplateResource
    ) -> TextResource:
        """
        Perform the task of parameterising a string using a template and parameters.

        Args:
            input_resource (ParamTemplateResource): The input resource containing the template and parameters.

        Returns:
            TextResource: The output resource containing the parameterised string.
        """
        template = input_resource.template.template_str.text
        params = input_resource.template.params.params
        result = template.format(**params)
        return TextResource(TextResource.TextModel(result))
