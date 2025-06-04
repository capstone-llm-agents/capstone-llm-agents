"""Application configuration module."""

import autogen
import requests

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """Configuration for the LLM (Large Language Model)."""

    api_type: str = Field(default="ollama")
    model: str = Field()


class ModelConfig(BaseModel):
    """Configuration for the model."""

    models: list[LLMConfig] = Field()
    default_model_index: int = Field()
    default_model_with_tools_index: int = Field()


class AppConfig(BaseModel):
    """Application configuration."""

    llm_config: ModelConfig
    db_path: str = Field("./database.db")
    interface: str = Field(default="cli")  # "cli" or "gui"


class LoadedConfig:
    """Class to hold the loaded application configuration."""

    def __init__(self, app_config: AppConfig):
        self.app_config = app_config

    def get_llm_config(
        self, uses_tools: bool = False, index: int | None = None
    ) -> autogen.LLMConfig:
        """Get the model configuration based on whether tools are used."""
        if uses_tools:
            index = (
                self.app_config.llm_config.default_model_with_tools_index
                if index is None
                else index
            )
        else:
            index = (
                self.app_config.llm_config.default_model_index
                if index is None
                else index
            )

        if not (0 <= index < len(self.app_config.llm_config.models)):
            raise IndexError("Model index out of range.")

        llm_config_model = self.app_config.llm_config.models[index]

        return autogen.LLMConfig(
            api_type=str(llm_config_model.api_type), model=str(llm_config_model.model)
        )

    def get_db_path(self) -> str:
        """Get the database path."""
        return self.app_config.db_path


class Config:
    """Class to hold the application configuration."""

    def __init__(self, config: AppConfig):
        self.config = config

    @staticmethod
    def get_ollama_models() -> list[str]:
        """Get the list of available models from the Ollama CLI."""
        response = requests.get("http://localhost:11434/api/tags", timeout=5)

        if response.status_code != 200:
            raise ConnectionError(
                "Failed to connect to the Ollama server. Please ensure it is running."
            )

        json = response.json()

        if "models" not in json:
            raise ValueError(
                "Invalid response from Ollama server. 'models' key not found."
            )

        return [model["name"] for model in json["models"]]

    @classmethod
    def create_config_file(
        cls,
        config_path: str = "./config.yaml",
    ):
        """Create a default configuration file."""

        # get models
        models = Config.get_ollama_models()

        # if there aren't any models, raise error
        if not models:
            raise ValueError(
                "No models found. Please download models using Ollama CLI."
            )

        default_model_index = 0
        default_model_with_tools_index = 0

        # ask user to select a default model
        while True:
            print("Available models:")
            for i, model in enumerate(models):
                print(f"{i + 1}. {model}")

            try:
                default_model_index = (
                    int(input(f"Select a default model (1-{len(models)}): ")) - 1
                )
                if 0 <= default_model_index < len(models):
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        # ask user to select a default model with tools
        while True:
            print("Available models with tools (it can be the same model):")
            for i, model in enumerate(models):
                print(f"{i + 1}. {model}")

            try:
                default_model_with_tools_index = (
                    int(input(f"Select a default model with tools (1-{len(models)}): "))
                    - 1
                )
                if 0 <= default_model_with_tools_index < len(models):
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        model_config = ModelConfig(
            models=[LLMConfig(api_type="ollama", model=model) for model in models],
            default_model_index=default_model_index,
            default_model_with_tools_index=default_model_with_tools_index,
        )

        app_config = AppConfig(
            llm_config=model_config,
            db_path="./database.db",
            interface="cli",
        )

        # create the file
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(app_config.model_dump_json(indent=4))

        return cls(config=app_config)
