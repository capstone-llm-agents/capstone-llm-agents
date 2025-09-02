"""The JSON parser utility provides functions to extract and parse JSON from strings."""

import re


def extract_json_from_response(response: str) -> str:
    """Extract and parse JSON from a string, removing markdown formatting if needed."""
    # Remove ```json ... ``` or ``` ... ``` blocks
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
    json_str = match.group(1) if match else response.strip()
    return json_str.strip()
