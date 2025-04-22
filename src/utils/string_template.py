"""Module for string template generation using a template and parameters."""

from typing import Callable
from mas.base_resource import BaseResource
from mas.resources.param_template import ParamTemplateResource
from mas.resources.params import ParamsResource
from mas.resources.text import TextResource
from mas.tasks.param_string_task import ParamStringTask


def generate_str_using_template(
    templated_str: str,
) -> Callable[[BaseResource], str]:
    """Generate the string callable from string template."""

    def param_temp_task(input_resource: BaseResource) -> str:
        """Generate the string template for the task."""
        # use param str task

        param_task = ParamStringTask()

        param_template = param_task.do(
            ParamTemplateResource(
                ParamTemplateResource.ParamTemplateModel(
                    template_str=TextResource.TextModel(text=templated_str),
                    params=ParamsResource.ParamsModel(
                        params=input_resource.model.model_dump()
                    ),
                )
            )
        )

        return param_template.text.text

    return param_temp_task
