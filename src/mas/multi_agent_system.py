"""Module for Multi-Agent System (MAS)"""

from mas.agent import MASAgent
from mas.base_resource import BaseResource
from mas.clauses.horn_all_dependencies import HornClauseForAllDescriptors
from mas.clauses.horn_descriptor import HornClauseForDepedendentDescriptor
from mas.clauses.horn_input import HornClauseForInput
from mas.clauses.horn_resource import HornClauseForResourceTransform
from mas.clauses.horn_task import HornClauseForTask
from mas.horn_clause import HornClause
from mas.horn_kb import HornKB
from mas.query.dependent_task import DependentTask
from mas.query.mas_query import MASQuery, ResourceModel, ResourceParamModel
from mas.query.query_dependencies import MASQueryDependencies, Param
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

    def solve_query(
        self, query: MASQuery, descriptor_mapping: dict[str, Task]
    ) -> BaseResource:
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

        # compute dependent tasks
        dependent_tasks: list[DependentTask] = []

        # tasks per resource
        dependent_tasks_per_resource: dict[
            tuple[type[BaseResource], int], list[DependentTask]
        ] = {}

        # go over descriptors
        for (
            resource_with_descriptors,
            descriptor_params,
        ) in query_dependencies.descriptors.items():
            # get the task
            output_res_tuple = resource_with_descriptors

            for descriptor_param in descriptor_params:
                # get the task
                task = descriptor_mapping.get(descriptor_param.name)
                if task is None:
                    raise ValueError(
                        f"Task {descriptor_param.name} not found in descriptor mapping."
                    )

                print(descriptor_param.params)

                # TODO add support for multiple params, we assume only one param
                params = list(descriptor_param.params.values())

                if len(params) == 0:
                    # use the input resource
                    param = Param(
                        "input_resource",
                        output_res_tuple[0],
                        output_res_tuple[1],
                    )
                else:
                    # get the param
                    param = params[0]

                param_id = param.id
                param_type = param.resource_type

                input_res_tuple = (
                    param_type,
                    param_id,
                )

                # create dependent task
                dependent_task = DependentTask(
                    task, input_res_tuple, output_res_tuple, descriptor_param.name
                )

                # add to dependent tasks
                dependent_tasks.append(dependent_task)

                # add to dependent tasks per resource
                if output_res_tuple not in dependent_tasks_per_resource:
                    dependent_tasks_per_resource[output_res_tuple] = []

                dependent_tasks_per_resource[output_res_tuple].append(dependent_task)

        print("Dependent tasks:")
        for dependent_task in dependent_tasks:
            print(
                f"\t{dependent_task.task.name}: {dependent_task.input_resource_tuple} -> {dependent_task.output_resource_tuple}"
            )
        # TODO figure out how to implement non-dependent tasks into the horn kb

        print("Dependent tasks per resource:")
        for input_res_tuple, dependent_tasks in dependent_tasks_per_resource.items():
            # get len
            num_dependent_tasks = len(dependent_tasks)
            print(f"\t{input_res_tuple}: {num_dependent_tasks} dependent tasks")

        horn_clauses: list[HornClause] = []

        horn_clause: HornClause

        # add the known clauses from input
        for input_resource_tuple in query_input.resource_id_mapping:
            horn_clause = HornClauseForInput(
                input_resource_tuple, self.resource_manager
            )

            # add to horn clauses
            horn_clauses.append(horn_clause)

            # iterate over tasks
        for task in self.task_manager.tasks.values():
            horn_clause = HornClauseForTask(
                task.input_resource, task.output_resource, self.resource_manager
            )
            # add to horn clauses
            horn_clauses.append(horn_clause)

        # add the dependent tasks
        for dependent_task in dependent_tasks:
            horn_clause = HornClauseForDepedendentDescriptor(
                dependent_task, self.resource_manager
            )
            # add to horn clauses
            horn_clauses.append(horn_clause)

            # also add just for resource transform
            horn_clause = HornClauseForResourceTransform(
                dependent_task.input_resource_tuple,
                dependent_task.output_resource_tuple,
                self.resource_manager,
            )

            # add to horn clauses
            horn_clauses.append(horn_clause)

        # add dependent task per resource horn clauses
        for input_res_tuple, dependent_tasks in dependent_tasks_per_resource.items():
            horn_clause = HornClauseForAllDescriptors(
                dependent_tasks, input_res_tuple, self.resource_manager
            )
            # add to horn clauses
            horn_clauses.append(horn_clause)

        # create the kb
        horn_kb = HornKB()
        for clause in horn_clauses:
            horn_kb.add_clause(clause)

        print("Horn clauses:")
        for clause in horn_clauses:
            print(f"\t{clause}")

        forward_chain_plans: list[list[HornClause]] = []

        # forward chain over each output resource
        # TODO optimise, bit expensive (reiterating for each resource)
        for output_resource in query_output.output_resources:
            resource_str = self.resource_manager.convert_resource_tuple_to_str(
                output_resource
            )

            # if it is in dependent tasks by resource we need to wrap it

            if output_resource in dependent_tasks_per_resource:
                # wrap with all_dependencies()
                resource_str = f"all_dependencies({resource_str})"

            found, forward_chain_plan = horn_kb.forward_chain(resource_str)

            if not found:
                raise ValueError(
                    f"Resource {resource_str} not found in forward chain plan."
                )

            forward_chain_plans.append(forward_chain_plan)

        # TODO convert forward chain plans to task plan
        print("Forward chain plans:")
        for forward_chain_plan in forward_chain_plans:
            print("\tPlan:")
            for clause in forward_chain_plan:
                print(f"\t\t{clause}")

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
