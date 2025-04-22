"""Dependency mapping for MAS query."""

from mas.base_resource import BaseResource
from mas.query.mas_query import ResourceParamModel
from mas.resource_manager import ResourceManager

# temp


class Param:
    """Class for a parameter in a descriptor."""

    def __init__(
        self, param_name: str, resource_type: type[BaseResource], resource_id: int
    ):
        """
        Initialise the Params class.

        Args:
            param_name (str): Name of the parameter.
            resource_type (type[BaseResource]): Type of the resource.
            resource_id (int): ID of the resource.
        """
        self.name = param_name
        """Name of the parameter."""

        self.id = resource_id
        """ID of the resource."""

        self.resource_type = resource_type
        """Type of the resource."""


class DescriptorParams:
    """Class for a descriptor in a query."""

    def __init__(self, name: str, params: dict[str, Param]):
        """
        Initialise the DescriptorParams class.

        Args:
            name (str): Name of the descriptor.
            params (dict[str, Param]): Parameters of the descriptor.
        """
        self.name = name
        """Name of the descriptor."""

        self.params = params
        """Parameters of the descriptor."""


class MASQueryDependencies:
    """Class for managing dependencies in MAS query."""

    # a descriptor has a name, params (that have names and resource dependencies)
    # eg. about_topic, params: { "about": tuple[RESOURCE_TYPE, RESOURCE_ID] }
    # a dependency a set of tuple[RESOURCE_TYPE, RESOURCE_ID]

    descriptors: dict[
        # resource type and id
        tuple[type[BaseResource], int],
        # descriptors
        list[DescriptorParams],  # NOTE: Must be a list because order matters
    ]
    """Dictionary of descriptors in the query."""

    dependencies: dict[
        # each resource
        tuple[type[BaseResource], int],
        # has a set of dependencies
        list[tuple[type[BaseResource], int]],
    ]
    """Dictionary of dependencies in the query."""

    def __init__(
        self,
        query_resources: list[dict[str, ResourceParamModel]],
        resource_manager: ResourceManager,
    ):
        """
        Initialise the QueryDependencies class.

        Args:
            query_resources (list[dict[str, ResourceParamModel]]): List of query resources.
            resource_manager (ResourceManager): Resource manager for the MAS.
        """
        self.dependencies = {}

        self.descriptors = {}

        # iter
        for query_resource in query_resources:
            # iter key values
            for resource_name, resource in query_resource.items():

                # resource type and id
                resource_type = resource_manager.get_resource_type(resource_name)

                # check type exists
                if resource_type is None:
                    raise ValueError(
                        f"Resource type {resource_name} not found in resource manager."
                    )

                resource_id = resource.id

                self.descriptors[(resource_type, resource_id)] = []

                # iter over descriptors
                if resource.descriptors is not None:

                    for descriptor_name, descriptor in resource.descriptors.items():

                        params_dict: dict[str, Param] = {}

                        # if has params
                        if descriptor.params is not None:
                            for param_name, param in descriptor.params.items():

                                param_type_name = list(param.keys())[0]

                                param_resource_type = (
                                    resource_manager.get_resource_type(param_type_name)
                                )

                                if param_resource_type is None:
                                    raise ValueError(
                                        f"Resource type {param_type_name} not found in resource manager."
                                    )

                                param_resource_id = param[param_type_name].id

                                param_class = Param(
                                    param_name, param_resource_type, param_resource_id
                                )

                                # add to params dict
                                params_dict[param_name] = param_class

                        params = DescriptorParams(descriptor_name, params_dict)

                        # add to descriptors
                        self.descriptors[(resource_type, resource_id)].append(params)

                # iter over dependencies
                if resource.dependencies is not None:

                    self.dependencies[(resource_type, resource_id)] = []

                    for dependency in resource.dependencies:
                        # get resource type and id
                        dependency_type_name = list(dependency.keys())[0]

                        dependency_resource_type = resource_manager.get_resource_type(
                            dependency_type_name
                        )

                        if dependency_resource_type is None:
                            raise ValueError(
                                f"Resource type {dependency_type_name} not found in resource manager."
                            )

                        dependency_resource_id = dependency[dependency_type_name].id

                        # add to dependencies
                        self.dependencies[(resource_type, resource_id)].append(
                            (dependency_resource_type, dependency_resource_id)
                        )
