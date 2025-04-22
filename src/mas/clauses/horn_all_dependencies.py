"""Horn clause for ensuring a resource has all descriptors/dependencies"""

from mas.base_resource import BaseResource
from mas.horn_clause import HornClause
from mas.query.dependent_task import DependentTask
from mas.resource_manager import ResourceManager


class HornClauseForAllDescriptors(HornClause):
    """
    Horn Clause class representing a Horn clause in propositional logic for ensuring a resource has all descriptors/dependencies.

    e.g. is_capitalised(sentence_1), about_topic(sentence_1) => all_dependencies(sentence_1)

    Attributes:
        head (str): The head of the Horn clause.
        body (list): The body of the Horn clause, represented as a list of literals.
        dependent_tasks (list[DependentTask]): The dependent tasks associated with the Horn clause.
    """

    def __init__(
        self,
        dependent_tasks: list[DependentTask],
        output_tuple: tuple[type[BaseResource], int],
        resource_manager: ResourceManager,
    ) -> None:
        """
        Initialise the HornClause with a head and body.

        Args:
            dependent_tasks (list[DependentTask]): The dependent tasks associated with the Horn clause.
            output_tuple (tuple): A tuple containing the output resource and its ID.
            resource_manager (ResourceManager): The resource manager for converting resource tuples to strings.
        """

        # get main output
        main_output_str = resource_manager.convert_resource_tuple_to_str(output_tuple)

        # wrap in descriptor
        # TODO refactor 'all_dependencies' content to be a constant stored somewhere
        # it appears in multiple places
        main_output_str = f"all_dependencies({main_output_str})"

        # body
        body: list[str] = []

        for dependent_task in dependent_tasks:

            # get output_str
            output_str = resource_manager.convert_resource_tuple_to_str(
                dependent_task.output_resource_tuple
            )

            # wrap in descriptor
            output_str = f"{dependent_task.descriptor}({output_str})"

            body.append(output_str)
        head = main_output_str

        super().__init__(head, body)

        # save dependent_tasks
        self.dependent_tasks = dependent_tasks
