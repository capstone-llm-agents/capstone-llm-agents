from llm_mas.logging.loggers import APP_LOGGER
from mem0.configs.base import MemoryConfig, EmbedderConfig, LlmConfig, VectorStoreConfig
import json
import pathlib
import yaml
from typing import Any, List

class InternalMemoryConfig:
    def __init__(self):
        self.project_dir = pathlib.Path(__file__).parent.parent.parent

    def load_provider_conf(self) -> MemoryConfig:
        vector_store_config = VectorStoreConfig(
            provider="chroma",
            config={
                    "collection_name": "test",
                    "path": "db",
            }
        )
        embed_config = EmbedderConfig(
            provider="ollama",
            config={
                "model": "mxbai - embed - large",
                "ollama_base_url": "http://localhost:11434",
            },

        )
        llm_config = LlmConfig(
            provider="ollama",
            config={
                "model": "llama3.1:latest",
                "temperature": 0,
                "max_tokens": 2000,
                "ollama_base_url": "http://localhost:11434",  # Ensure this URL is correct
                },
        )
        default_config = MemoryConfig(
            vector_store=vector_store_config,
            llm=llm_config,
            embedder=embed_config,
        )
        try:
            config_dir = self.project_dir.joinpath("config").joinpath("storage.yaml")
            APP_LOGGER.debug(f"project_dir: {config_dir}")
            config = yaml.safe_load(open(config_dir))
            choice_index = config["provider_choice"]

            all_providers = config["providers"]

            provider_choice = all_providers[choice_index]
            embed_choice = config["embedding_model_choice"]
            llm_choice = config["model_choice"]

            embed_choice = config["embedding_models"][embed_choice]
            llm_choice = config["models"][llm_choice]

            vector_store_config = VectorStoreConfig(
                provider=provider_choice.get("provider"),
                config=provider_choice.get("config"),
            )
            embed_config= EmbedderConfig(
                provider=embed_choice.get("provider"),
                config=embed_choice.get("config"),
            )
            llm_config = LlmConfig(
                provider=llm_choice.get("provider"),
                config=llm_choice.get("config"),
            )

            config = MemoryConfig(
                vector_store=vector_store_config,
                llm=llm_config,
                embedder=embed_config,
            )
            return config

        except FileNotFoundError:
            APP_LOGGER.error("Storage File Not Found using default config")
            return default_config
        except yaml.YAMLError as e:
            APP_LOGGER.error(f"Yaml Error: {e}, \nusing default config")
            return default_config
        except KeyError as e:
            APP_LOGGER.error(f"Key Error: {e} \nusing default config")
            return default_config
        except TypeError as e:
            APP_LOGGER.error(f"Type Error {e} \n using default config")
            return default_config
        except Exception as e:
            APP_LOGGER.error(f"Unknown Error: {e} \nusing default config")
            return default_config




