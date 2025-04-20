"""Models for application and models configurations."""

from typing import Optional
from pydantic import BaseModel


class AppConfig(BaseModel):
    """Application configuration model."""

    env: str
    """Path to the .env file."""

    models: str
    """Path to the models JSON config."""


class ModelConfig(BaseModel):
    """Model configuration model."""

    api_type: str
    """API type for the model."""

    model: str
    """Model name."""


class ModelsConfig(BaseModel):
    """Models configuration model."""

    models: list[ModelConfig]
    """List of model configurations."""

    default_model: int
    """Index of the default model in the list of models."""

    default_model_with_tools: Optional[int] = None
    """Index of the default model with tools in the list of models. If None, presumes that the default model supports tools."""
