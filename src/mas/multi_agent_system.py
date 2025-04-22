"""Module for Multi-Agent System (MAS)"""

from mas.agent import MASAgent
from mas.base_resource import BaseResource
from mas.query.mas_query import MASQuery, ResourceModel, ResourceParamModel
from mas.query.query_dependencies import MASQueryDependencies
from mas.query.query_input import MASQueryInput
from mas.query.query_output import MASQueryOutput
from mas.resource_manager import ResourceManager
from mas.task import Task
from mas.task_manager import TaskManager


class MultiAgentSystem:
    """A class representing a Multi-Agent System (MAS).

    The MAS contains:
        A collection of agents that can interact with each other and perform tasks (possibly nodes).
        A resource manager that knows about all the resources in the system.
        A task manager that knows about all the tasks in the system.
    """

    agents: list[MASAgent]
    """List of agents in the MAS."""

    def __init__(self):
        """
        Initialise the Multi-Agent System (MAS).
        """

        self.agents = []

        self.resource_manager = ResourceManager()
        """The resource manager for the MAS."""

        self.task_manager = TaskManager()
        """The task manager for the MAS."""

    def solve_query(self, query: MASQuery) -> BaseResource:
        """
        Solve a query using the MAS.

        Args:
            query (MASQuery): The query to be solved.

        Returns:
            BaseResource: The resource obtained from solving the query.
        """

        # input
        query_input = MASQueryInput(query.input, self.resource_manager)

        print("Input resources:")
        print(query_input.resource_id_mapping)

        # also add to resource manager
        for resource_id_type_pair in query_input.resource_id_mapping:
            resource_type, resource_id = resource_id_type_pair
            self.resource_manager.add_resource(resource_type, resource_id)

        # resources
        query_resources = query.resources

        # iter over
        for query_resource in query_resources:
            # iter key values
            for key, value in query_resource.items():
                # get resource
                self.add_resource_from_resource_model(key, value)

        # check resources
        print("Resources in resource manager:")
        print(self.resource_manager.get_resources())

        # get resource dependencies
        query_dependencies = MASQueryDependencies(
            query_resources, self.resource_manager
        )

        print("Resource descriptors:")
        print(query_dependencies.descriptors)

        print("=" * 50)

        for (
            resource_with_descriptors,
            descriptors,
        ) in query_dependencies.descriptors.items():

            for descriptor in descriptors:
                print(f"Resource: {resource_with_descriptors}")
                print(f"Descriptor: {descriptor.name}")

                for param_name, param in descriptor.params.items():
                    print(f"\tParam name: {param_name}")
                    print(f"\tParam resource type: {param.resource_type}")

        print("=" * 50)

        print("Resource dependencies:")
        print(query_dependencies.dependencies)

        # output
        query_output = MASQueryOutput(query.output, self.resource_manager)

        print("Output resources:")
        print(query_output.output_resources)

        print("Tasks")
        for task in self.task_manager.tasks:
            print(f"\t{task}")

        # TODO
        return None

    def add_agent(self, agent: MASAgent):
        """
        Add an agent to the MAS.

        Args:
            agent (MASAgent): The agent to be added.
        """
        self.agents.append(agent)

    def add_resource_type(self, resource_name: str, resource_type: type[BaseResource]):
        """
        Add a resource type to the MAS.

        Args:
            resource_name (str): The name of the resource type.
            resource_type (type[BaseResource]): The type of the resource.
        """
        self.resource_manager.add_resource_type(resource_name, resource_type)

    def add_task(self, task: Task):
        """
        Add a task to the MAS.

        Args:
            task (Task): The task to be added.
        """
        self.task_manager.add_task(task)

    def add_resource_types_from_dict(
        self, resource_types: dict[str, type[BaseResource]]
    ):
        """
        Add multiple resource types to the MAS.

        Args:
            resource_types (dict[str, type[BaseResource]]): A dictionary of resource types to be added.
        """
        for resource_name, resource_type in resource_types.items():
            self.add_resource_type(resource_name, resource_type)

    def add_resource_from_resource_model(
        self,
        resource_name: str,
        resource_param_model: ResourceParamModel | ResourceModel,
    ):
        """
        Add a resource from a resource parameter model to the MAS.

        Args:
            resource_name (str): The name of the resource.
            resource_param_model (BaseResource): The resource parameter model to be added.
        """
        resource_id = resource_param_model.id

        resource_type = self.resource_manager.get_resource_type(resource_name)
        if resource_type is None:
            raise ValueError(
                f"Resource type {resource_name} not found in resource manager."
            )

        self.resource_manager.add_resource(resource_type, resource_id)
