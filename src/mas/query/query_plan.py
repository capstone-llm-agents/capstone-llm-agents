"""Module for query plan class"""

from mas.clauses.horn_descriptor import HornClauseForDepedendentDescriptor
from mas.clauses.horn_resource_assignment import HornClauseForResourceAssignment
from mas.clauses.horn_task import HornClauseForTask


class QueryPlan:
    """Holds the horn clauses for the query plan"""

    def __init__(
        self,
        horn_clauses: list[
            HornClauseForDepedendentDescriptor
            | HornClauseForResourceAssignment
            | HornClauseForTask
        ],
    ):
        """
        Initialise the QueryPlan with a list of horn clauses.

        Args:
            horn_clauses (list[HornClause]): A list of horn clauses representing the query plan.
        """
        self.horn_clauses = horn_clauses
