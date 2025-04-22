"""Pydantic models for MAS query."""

from typing import Any, Optional
from pydantic import BaseModel

import yaml


class ResourceModel(BaseModel):
    """Resource pydantic model for MAS query."""

    id: int


class ResourceArgModel(BaseModel):
    """Resource argument pydantic model for MAS query."""

    id: int
    args: Optional[dict[str, Any]] = None


class ResourceDescriptorModel(BaseModel):
    """Resource descriptor pydantic model for MAS query."""

    params: Optional[dict[str, dict[str, ResourceModel]]] = None


class ResourceParamModel(BaseModel):
    """Resource parameter pydantic model for MAS query."""

    id: int
    descriptors: Optional[dict[str, ResourceDescriptorModel]] = None
    dependencies: Optional[list[dict[str, ResourceModel]]] = None


class MASQuery(BaseModel):
    """MAS query pydantic model."""

    input: list[dict[str, ResourceArgModel]]
    resources: list[dict[str, ResourceParamModel]]
    output: list[dict[str, ResourceModel]]

    @classmethod
    def from_yaml(cls, yaml_file: str) -> "MASQuery":
        """
        Load MAS query from a YAML file.

        Args:
            yaml_file (str): Path to the YAML file.

        Returns:
            MASQuery: MAS query object.
        """

        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return cls(**data)
