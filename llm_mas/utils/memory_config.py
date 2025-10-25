from llm_mas.logging.loggers import APP_LOGGER
import json
import pathlib
import yaml
from typing import Any, List

class MemoryConfig:
    def __init__(self):
        self.project_dir = pathlib.Path(__file__).parent.parent.parent

    def load_provider_conf(self) -> dict | None:
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

            return {"embedd": embed_choice, "llm":llm_choice, "provider": provider_choice}
        except FileNotFoundError:
            APP_LOGGER.error("Storage File Not Found")
            return None
        except yaml.YAMLError as e:
            APP_LOGGER.error(f"Yaml Error: {e}")
            return None
        except KeyError as e:
            APP_LOGGER.error(f"Key Error: {e}")
            return None
        except TypeError as e:
            APP_LOGGER.error(f"Type Error {e}")
            return None
        except Exception as e:
            APP_LOGGER.error(f"Unknown Error: {e}")
            return None




