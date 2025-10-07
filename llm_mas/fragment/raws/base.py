"""Some base raw data types for fragment kinds."""

# kinds: text, image, file, json, table, code, url, location, datetime, number, boolean

from typing import Any

from llm_mas.fragment.system_view import SystemView


class TextRaw(SystemView):
    """A raw data type for text fragments."""

    def __init__(self, content: str) -> None:
        """Initialize a text raw data type with content."""
        self.content = content


class FileRaw(SystemView):
    """A raw data type for file fragments."""

    def __init__(self, file_path: str) -> None:
        """Initialize a file raw data type with a file path."""
        self.file_path = file_path


class ImageRaw(FileRaw):
    """A raw data type for image fragments."""

    def __init__(self, file_path: str, alt_text: str = "") -> None:
        """Initialize an image raw data type with a file path and optional alt text."""
        super().__init__(file_path)
        self.alt_text = alt_text


class JSONRaw(SystemView):
    """A raw data type for JSON fragments."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize a JSON raw data type with a dictionary."""
        self.data = data


class CodeRaw(SystemView):
    """A raw data type for code fragments."""

    def __init__(self, code: str, language: str) -> None:
        """Initialize a code raw data type with code and optional language."""
        self.code = code
        self.language = language


class LocationRaw(JSONRaw):
    """A raw data type for location fragments."""

    def __init__(self, latitude: float, longitude: float, description: str = "") -> None:
        """Initialize a location raw data type with latitude, longitude and optional description."""
        self.latitude = latitude
        self.longitude = longitude
        self.description = description
        super().__init__({"latitude": latitude, "longitude": longitude, "description": description})


class DatetimeRaw(JSONRaw):
    """A raw data type for datetime fragments."""

    def __init__(self, datetime_str: str) -> None:
        """Initialize a datetime raw data type with a datetime string."""
        self.datetime_str = datetime_str
        super().__init__({"datetime": datetime_str})
