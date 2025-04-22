"""Test YAML file to pydantic model"""

import yaml

from app import App
from mas.query.mas_query import MASQuery


def test_yaml_to_pydantic(app: App):
    """Test YAML file to pydantic model."""

    only_descriptors = "./resource/example/example.yaml"
    descriptors_and_dependencies = "./resource/example/example2.yaml"

    def load_mas_query_from_yaml(file_path: str) -> MASQuery:
        """Load MAS query from yaml file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return MASQuery(**data)

    # Pretty print the output
    print(
        load_mas_query_from_yaml(only_descriptors).model_dump_json(
            indent=4, exclude_unset=True, exclude_defaults=True
        )
    )
    print(
        load_mas_query_from_yaml(descriptors_and_dependencies).model_dump_json(
            indent=4, exclude_unset=True, exclude_defaults=True
        )
    )
