"""Horn clause for query input"""

from mas.base_resource import BaseResource
from mas.horn_clause import HornClause
from mas.resource_manager import ResourceManager


class HornClauseForInput(HornClause):
    """
    Horn Clause class representing a Horn clause in propositional logic for input.

    Attributes:
        head (str): The head of the Horn clause.
        body (list): The body of the Horn clause, represented as a list of literals.
    """

    def __init__(
        self,
        output_tuple: tuple[type[BaseResource], int],
        resource_manager: ResourceManager,
    ) -> None:
        """
        Initialise the HornClause with a head and body.

        Args:
            input_tuple (tuple): A tuple containing the head and body of the Horn clause.
            resource_manager (ResourceManager): The resource manager for converting resource tuples to strings.
        """

        # get output_str
        output_str = resource_manager.convert_resource_tuple_to_str(output_tuple)

        # body
        body: list[str] = []

        head = output_str

        super().__init__(head, body)

        # save output_tuple
        self.output_tuple = output_tuple
