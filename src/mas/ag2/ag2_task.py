"""Module for Autogen2 Task class used to create tasks that are completed using Autogen2."""

from typing import Callable, Generic, Type, TypeVar
from mas.agent import MASAgent
from mas.base_resource import BaseResource
from mas.task import Task

InputResource = TypeVar("InputResource", bound=BaseResource)
OutputResource = TypeVar("OutputResource", bound=BaseResource)


class AG2Task(
    Task[InputResource, OutputResource], Generic[InputResource, OutputResource]
):
    """AG2 task takes some input resource and applies to a string template and prompts the LLM to generate the output resource."""

    def __init__(
        self,
        input_resource: Type[InputResource],
        output_resource: Type[OutputResource],
        generate_str: Callable[[InputResource], str],
        agent: MASAgent,
    ):
        """
        Initialise the AG2Task with input and output resource types and a function to do the work.

        Args:
            input_resource (Type[InputResource]): The type of the input resource.
            output_resource (Type[OutputResource]): The type of the output resource.
            generate_str (Callable[[InputResource], str]): The function to generate the string template.
        """
        self.agent = agent

        do_work = self.get_do_work(generate_str)

        super().__init__(input_resource, output_resource, do_work)

    def get_do_work(
        self, generate_str: Callable[[InputResource], str]
    ) -> Callable[[InputResource], OutputResource]:
        """
        Get the function to do the work for the task.

        Args:
            str_template (str): The string template to be used for the task.

        Returns:
            Callable[[InputResource], OutputResource]: The function to do the work for the task.
        """

        def do_work(input_resource: InputResource) -> OutputResource:
            # format the string template with the parameters
            formatted_str = generate_str(input_resource)

            # call the LLM to generate the output resource model
            output_resource_model = self.agent.ask(formatted_str)

            # create the output resource from the model
            output_resource = self.output_resource(output_resource_model)

            return output_resource

        return do_work
