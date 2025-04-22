"""Test file for basic MAS"""

from mas.base_resource import BaseResource
from mas.multi_agent_system import MultiAgentSystem
from app import App
from mas.query.mas_query import MASQuery
from mas.tasks.write_sentence import SentenceResource, TopicResource


def test_basic_mas(app: App):
    """Test basic MAS."""

    mas = MultiAgentSystem()

    yaml_file = "./resource/example/example2.yaml"

    mas_query = MASQuery.from_yaml(yaml_file)

    print(
        mas_query.model_dump_json(indent=4, exclude_unset=True, exclude_defaults=True)
    )

    # TODO create a class that can contains this mapping and allows you add to it
    # TODO includes aliases for mapping also
    # example resources mapping
    example_resource_mapping: dict[str, type[BaseResource]] = {
        "sentence": SentenceResource,
        "topic": TopicResource,
    }

    mas.add_resource_types_from_dict(example_resource_mapping)

    mas.solve_query(mas_query)
