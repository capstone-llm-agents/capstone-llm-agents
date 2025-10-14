Model_type = 3 #use 1 for gemma3 or 2 for openai


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
else:#fallback to local llm if any unusable inputs are found
    print("No model has been selected local LLM will be used instead")
    Model_type = 1
    llm_config = {
        "api_type": "ollama",
        "model": "gemma3",
    }

#Note: when changing what models are being used different LLM's have different ways of extracting responses.
#if your chosen model does not work when replacing any configuration you can try and swap it between option 1 or two.
#if this doesn't work than the way the LLM is extracting data will need to be adjusted within each server/function file to match your chosen LLM
#it is recommended to add a new model type if you chose to do this.
