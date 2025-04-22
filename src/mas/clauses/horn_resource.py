"""Horn clause for resource transform"""

from mas.base_resource import BaseResource
from mas.horn_clause import HornClause
from mas.resource_manager import ResourceManager


class HornClauseForResourceTransform(HornClause):
    """
    Horn Clause class representing a Horn clause in propositional logic for a resource transform
    generated from a descriptor.

    descriptor topic_1 => about_topic(sentence_1)
    also creates this horn clause:
    e.g. about_topic(sentence_1) => sentence_1

    Attributes:
        head (str): The head of the Horn clause.
        body (list): The body of the Horn clause, represented as a list of literals.
        input_tuple (tuple): The input resource tuple.
        output_tuple (tuple): The output resource tuple.
    """

    def __init__(
        self,
        prev_head: str,
        output_resource_tuple: tuple[type[BaseResource], int],
        resource_manager: ResourceManager,
    ) -> None:
        """
        Initialise the HornClause with a head and body.

        Args:
            prev_head (str): The previous head of the Horn clause.
            output_tuple (tuple): A tuple containing the output resource and its ID.
            resource_manager (ResourceManager): The resource manager for converting resource tuples to strings.
        """

        # get output_str
        output_str = resource_manager.convert_resource_tuple_to_str(
            output_resource_tuple
        )

        # body
        body = [prev_head]

        head = output_str

        super().__init__(head, body)

        # save output_tuple
        self.output_tuple = output_resource_tuple
