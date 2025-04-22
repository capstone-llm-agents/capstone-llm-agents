"""Module for converting tasks to clauses."""

from mas.horn_clause import HornClause
from mas.query.dependent_task import DependentTask
from mas.resource_manager import ResourceManager


class ClauseConverter:
    """
    A module for converting tasks to clauses.
    """

    @staticmethod
    def convert_to_clause(
        dependent_task: DependentTask,
        resource_manager: ResourceManager,
    ) -> HornClause:
        """
        Convert the task to a clause.

        Args:
            dependent_task (DependentTask): The dependent task to be converted.
            resource_manager (ResourceManager): The resource manager for the MAS.
        Returns:
            HornClause: The converted Horn clause.
        """
        input_resource_tuple = dependent_task.input_resource_tuple

        input_resource_str = resource_manager.convert_resource_tuple_to_str(
            input_resource_tuple
        )

        return HornClause(
            head=dependent_task.to_dependent_str(resource_manager),
            body=[input_resource_str],
        )
