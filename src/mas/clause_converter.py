"""Module for converting tasks to clauses."""

from mas.base_resource import BaseResource
from mas.horn_clause import HornClause
from mas.query.query_dependencies import DescriptorParams
from mas.task import Task


class ClauseConverter:
    """
    A module for converting tasks to clauses.
    """

    @staticmethod
    def convert_to_clause(
        task: Task,
        descriptors: dict[tuple[type[BaseResource], int], list[DescriptorParams]],
        dependencies: dict[
            tuple[type[BaseResource], int], list[tuple[type[BaseResource], int]]
        ],
        descriptor_mapping: dict[str, Task],
    ) -> list[HornClause]:
        """
        Convert the task to a clause.

        Args:
            task (Task): The task to be converted.
            descriptors (dict): The descriptors for the task.
            dependencies (dict): The dependencies for the task.
            descriptor_mapping (dict): The mapping of descriptors to tasks.

        Returns:
            list[HornClause]: The horn clauses representing the task.
        """
        # TODO Use dependencies to create the clauses

        # Task: WriteSentenceTask
        # Descriptors: [('is_capitalised', 0), ('about_topic', )]
        # Dependencies: None
