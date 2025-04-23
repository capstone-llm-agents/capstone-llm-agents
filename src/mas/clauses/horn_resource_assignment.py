"""Horn clause for resource transform"""

from mas.base_resource import BaseResource
from mas.horn_clause import HornClause
from mas.resource_manager import ResourceManager


class HornClauseForResourceAssignment(HornClause):
    """
    Horn Clause class representing a Horn clause in propositional logic for a resource assignment.

    e.g. topic_any => topic_1

    Attributes:
        head (str): The head of the Horn clause.
        body (list): The body of the Horn clause, represented as a list of literals.
        input_tuple (tuple): The input resource tuple.
        output_tuple (tuple): The output resource tuple.
    """

    def __init__(
        self,
        output_resource_tuple: tuple[type[BaseResource], int],
        resource_manager: ResourceManager,
    ) -> None:
        """
        Initialise the HornClause with a head and body.

        Args:
            output_resource_tuple (tuple): A tuple containing the resource and its ID.
            resource_manager (ResourceManager): The resource manager for converting resource tuples to strings.
        """

        # create input resource tuple by getting the type and making it use any id
        input_resource_type = output_resource_tuple[0]

        input_resource_id = 0  # 0 represents any id

        input_resource_tuple = (input_resource_type, input_resource_id)

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
