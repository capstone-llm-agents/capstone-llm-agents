"""Test YAML file to pydantic model"""

import yaml

from mas_query import MASQuery


ONLY_DESCRIPTORS = "./resource/example/example.yaml"
DESCRIPTORS_AND_DEPENDENCIES = "./resource/example/example2.yaml"


def load_mas_query_from_yaml(file_path: str) -> MASQuery:
    """Load MAS query from yaml file."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return MASQuery(**data)


print(load_mas_query_from_yaml(ONLY_DESCRIPTORS))
print("")
print(load_mas_query_from_yaml(DESCRIPTORS_AND_DEPENDENCIES))
