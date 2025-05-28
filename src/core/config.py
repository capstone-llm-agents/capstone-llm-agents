"""Application configuration module."""

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """Configuration for the LLM (Large Language Model)."""

    model_type: str = Field()
    model: str = Field()


class AppConfig(BaseModel):
    """Application configuration."""

    db_path: str = Field()
    llm: LLMConfig
