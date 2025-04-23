"""Runs the plan for a given query"""

from mas.base_resource import BaseResource
from mas.clauses.horn_descriptor import HornClauseForDepedendentDescriptor
from mas.clauses.horn_resource_assignment import HornClauseForResourceAssignment
from mas.clauses.horn_task import HornClauseForTask
from mas.query.query_plan import QueryPlan
from mas.resource_manager import ResourceManager


class QueryRunner:
    """Runs the plan for a given query."""

    def __init__(
        self,
        query_plan: QueryPlan,
        resource_manager: ResourceManager,
        input_resources: dict[tuple[type[BaseResource], int], BaseResource],
        output_resource_tuple: tuple[type[BaseResource], int],
    ):
        """
        Initialise the QueryRunner with a query plan and resource manager.

        Args:
            query_plan (QueryPlan): The query plan to be executed
            resource_manager (ResourceManager): The resource manager for the MAS
            input_resources (dict[tuple[type[BaseResource], int], BaseResource]): The input resources for the query
            output_resource_tuple (tuple[type[BaseResource], int]): The output resource tuple for the query
        """
        self.query_plan = query_plan
        self.resource_manager = resource_manager

        # lookup for resource values
        self.resource_values: dict[tuple[type[BaseResource], int], BaseResource] = {}

        # add input resources
        # TODO its not a copy which is a problem, should be fine though I think
        # because each task generates a new resource
        for resource_tuple, resource in input_resources.items():
            self.resource_values[resource_tuple] = resource

        self.output_resource_tuple = output_resource_tuple

    def run(self) -> BaseResource:
        """
        Run the query plan.

        Returns:
            None
        """

        # iter over claues
        for clause in self.query_plan.horn_clauses:

            print("Running clause", clause)

            # handle type
            if isinstance(clause, HornClauseForDepedendentDescriptor):
                # e.g. topic_1 => about_topic(sentence_1)

                # input
                input_resource_tuple = clause.dependent_task.input_resource_tuple

                # output
                output_resource_tuple = clause.dependent_task.output_resource_tuple

                # lookup input resource
                if input_resource_tuple not in self.resource_values:
                    raise ValueError(
                        f"Plan did not have input resource {input_resource_tuple} in resource values."
                    )
                # get input resource
                input_resource = self.resource_values[input_resource_tuple]

                # run task
                print("Running task with input resource", input_resource)
                output_resource = clause.dependent_task.task.do(input_resource)

                # set output resource
                self.resource_values[output_resource_tuple] = output_resource

            elif isinstance(clause, HornClauseForResourceAssignment):
                # e.g. sentence_0 => sentence_2

                # input
                input_resource_tuple = clause.input_tuple

                # output
                output_resource_tuple = clause.output_tuple

                # lookup input resource
                if input_resource_tuple not in self.resource_values:
                    raise ValueError(
                        f"Plan did not have input resource {input_resource_tuple} in resource values."
                    )

                # get input resource
                input_resource = self.resource_values[input_resource_tuple]

                # add new record
                self.resource_values[output_resource_tuple] = input_resource

            elif isinstance(clause, HornClauseForTask):
                # e.g. topic_0 => sentence_0

                # input
                input_resource_tuple = clause.input_tuple

                # output
                output_resource_tuple = clause.output_tuple

                # lookup input resource
                if input_resource_tuple not in self.resource_values:
                    raise ValueError(
                        f"Plan did not have input resource {input_resource_tuple} in resource values."
                    )

                # get input resource
                input_resource = self.resource_values[input_resource_tuple]

                print("Running task with input resource", input_resource)

                # run task
                output_resource = clause.task.do(input_resource)

                # set output resource
                self.resource_values[output_resource_tuple] = output_resource
            else:
                raise ValueError(f"Unknown clause type {type(clause)} in query plan.")

        # lookup output resource
        if self.output_resource_tuple not in self.resource_values:
            raise ValueError(
                f"Plan did not have output resource {self.output_resource_tuple} in resource values."
            )

        return self.resource_values[self.output_resource_tuple]
