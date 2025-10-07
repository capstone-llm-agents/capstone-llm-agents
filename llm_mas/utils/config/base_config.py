"""Base configuration manager using pydantic and YAML."""

from pathlib import Path
from typing import Generic, TypeVar

import pydantic
import yaml
from pydantic import BaseModel


class ConfigBaseModel(BaseModel):
    """Base model for configuration schemas."""

    version: str


T = TypeVar("T", bound=ConfigBaseModel)


class BaseConfigManager(Generic[T]):  # noqa: UP046
    """Generic configuration manager for YAML-based configs."""

    def __init__(self, file_path: str, schema: type[T]) -> None:
        """Initialize the configuration manager."""
        self.file_path = file_path
        self.schema = schema
        self.config = self.load_config()

    def load_config(self) -> T:
        """Load configuration from a YAML file."""
        try:
            with Path(self.file_path).open("r") as file:
                config_data = yaml.safe_load(file)
                if not config_data:
                    msg = f"Configuration file '{self.file_path}' is empty or invalid."
                    raise ValueError(msg)
                return self.schema(**config_data)
        except FileNotFoundError as e:
            msg = f"Configuration file '{self.file_path}' not found."
            raise FileNotFoundError(msg) from e
        except yaml.YAMLError as e:
            msg = f"Error parsing YAML file. {e}"
            raise ValueError(msg) from e
        except pydantic.ValidationError as e:
            msg = f"Invalid configuration structure. {e}"
            raise ValueError(msg) from e

    def save_config(self, config: T) -> None:
        """Save configuration to a YAML file."""
        try:
            with Path(self.file_path).open("w") as file:
                yaml.safe_dump(config.model_dump(), file)
        except Exception as e:
            msg = f"Error saving configuration: {e}"
            raise OSError(msg) from e
