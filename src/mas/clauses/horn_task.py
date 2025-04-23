"""Horn clause for a task with no descriptors / dependencies"""

from mas.base_resource import BaseResource
from mas.horn_clause import HornClause
from mas.resource_manager import ResourceManager
from mas.task import Task


class HornClauseForTask(HornClause):
    """
    Horn Clause class representing a Horn clause in propositional logic for a basic task.

    e.g. topic_any => sentence_any

    Attributes:
        head (str): The head of the Horn clause.
        body (list): The body of the Horn clause, represented as a list of literals.
        input_tuple (tuple): The input resource tuple.
        output_tuple (tuple): The output resource tuple.
    """

    def __init__(
        self,
        input_resource_type: type[BaseResource],
        output_resource_type: type[BaseResource],
        resource_manager: ResourceManager,
        task: Task,
    ) -> None:
        """
        Initialise the HornClause with a head and body.

        Args:
            input_tuple (tuple): A tuple containing the input resource and its ID.
            output_tuple (tuple): A tuple containing the output resource and its ID.
            resource_manager (ResourceManager): The resource manager for converting resource tuples to strings.
        """

        # get input_tuple
        input_resource_tuple = (input_resource_type, 0)

        # get output_tuple
        output_resource_tuple = (output_resource_type, 0)

        # get input_str
        input_str = resource_manager.convert_resource_tuple_to_str(input_resource_tuple)

        # get output_str
        output_str = resource_manager.convert_resource_tuple_to_str(
            output_resource_tuple
        )

        # body
        body = [input_str]

        head = output_str

        super().__init__(head, body)

        # save input_tuple
        self.input_tuple = input_resource_tuple

        # save output_tuple
        self.output_tuple = output_resource_tuple

        # save task
        self.task = task
