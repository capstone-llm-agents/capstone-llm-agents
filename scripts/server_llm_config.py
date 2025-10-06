Model_type = 2 #use 1 for gemma3 or 2 for openai
import os
if Model_type == 1:
    llm_config = {
        "api_type": "ollama",
        "model": "gemma3",
    }
elif Model_type == 2:
    llm_config = {
        "api_type": "openai",
        "model": "gpt-4o-mini",
        "api_key": os.environ.get("OPENAI_API_KEY"),
    }
else:
    print("No model has been selected local LLM will be used instead")
    llm_config = {
        "api_type": "ollama",
        "model": "gemma3",
    }
