"""Horn clause for resource descriptor"""

from mas.horn_clause import HornClause
from mas.query.dependent_task import DependentTask
from mas.resource_manager import ResourceManager


class HornClauseForDepedendentDescriptor(HornClause):
    """
    Horn Clause class representing a Horn clause in propositional logic for a resource descriptor.

    e.g. topic_1 => about_topic(sentence_1)

    Attributes:
        head (str): The head of the Horn clause.
        body (list): The body of the Horn clause, represented as a list of literals.
        dependent_task (DependentTask): The dependent task associated with the Horn clause.
    """

    def __init__(
        self,
        dependent_task: DependentTask,
        resource_manager: ResourceManager,
    ) -> None:
        """
        Initialise the HornClause with a head and body.

        Args:
            dependent_task (DependentTask): The dependent task associated with the Horn clause.
            resource_manager (ResourceManager): The resource manager for converting resource tuples to strings.
        """

        # get input_str
        input_str = resource_manager.convert_resource_tuple_to_str(
            dependent_task.input_resource_tuple
        )

        # get output_str
        output_str = resource_manager.convert_resource_tuple_to_str(
            dependent_task.output_resource_tuple
        )

        # wrap in descriptor
        output_str = f"{dependent_task.descriptor}({output_str})"

        # body
        body: list[str] = [input_str]

        head = output_str

        super().__init__(head, body)

        # save dependent_task
        self.dependent_task = dependent_task
