"""Some basic fragment kinds."""

# kinds: text, image, file, json, table, code, url, location, datetime, number, boolean
from pathlib import Path

from llm_mas.fragment.agent_view import AgentView
from llm_mas.fragment.kind import FragmentKind
from llm_mas.fragment.raws.base import (
    CodeRaw,
    DatetimeRaw,
    FileRaw,
    ImageRaw,
    JSONRaw,
    LocationRaw,
    TextRaw,
)
from llm_mas.fragment.user_view import FileRenderable, TextRenderable, UserView


class TextFragmentKind(FragmentKind):
    """A text fragment kind."""

    def __init__(self, raw: TextRaw) -> None:
        """Initialize a fragment kind with a name, description and raw data."""
        super().__init__("text", "A text fragment", raw)
        self.raw = raw  # hack to get proper typing  # noqa: FIX004

    def agent_view(self) -> AgentView:
        """Return the agent's view of the fragment."""
        chunk = self.raw.content
        view = AgentView()
        view.add_text_chunk(chunk)
        return view

    def user_view(self) -> UserView:
        """Return the user's view of the fragment."""
        view = UserView()
        view.renderables.append(TextRenderable(self.raw.content))
        return view


class FileFragmentKind(FragmentKind):
    """A raw data type for file fragments."""

    def __init__(self, name: str, description: str, raw: FileRaw) -> None:
        """Initialize a file raw data type with a file path."""
        super().__init__(name, description, raw)
        self.raw = raw  # hack to get proper typing  # noqa: FIX004

    def agent_view(self) -> AgentView:
        """Return the agent's view of the fragment."""
        view = AgentView()

        # add the file name as a text chunk
        view.add_text_chunk(f"File: {self.raw.file_path}")

        with Path(self.raw.file_path).open("r") as f:
            content = f.read()
            view.add_text_chunk(content)

        return view

    def user_view(self) -> UserView:
        """Return the user's view of the fragment."""
        view = UserView()

        # add the name of the file as a text renderable
        view.renderables.append(TextRenderable(f"File: {self.raw.file_path}"))

        # add the file
        view.renderables.append(FileRenderable(self.raw.file_path))

        return view


class ImageFragmentKind(FileFragmentKind):
    """A raw data type for image fragments."""

    def __init__(self, raw: ImageRaw) -> None:
        """Initialize an image raw data type with a file path and optional alt text."""
        super().__init__("image", "An image fragment", raw)
        self.raw = raw  # hack to get proper typing  # noqa: FIX004

    def user_view(self) -> UserView:
        """Return the user's view of the fragment."""
        view = super().user_view()

        if self.raw.alt_text:
            view.renderables.append(TextRenderable(f"Alt text: {self.raw.alt_text}"))

        return view

    def agent_view(self) -> AgentView:
        """Return the agent's view of the fragment."""
        view = super().agent_view()

        # add the alt text if it exists
        if self.raw.alt_text:
            view.add_text_chunk(f"Alt text: {self.raw.alt_text}")

        return view


class JSONFragmentKind(FragmentKind):
    """A raw data type for JSON fragments."""

    def __init__(self, name: str, description: str, raw: JSONRaw) -> None:
        """Initialize a JSON raw data type with a dictionary."""
        super().__init__(name or "json", description or "A JSON fragment", raw)
        self.raw = raw  # hack to get proper typing  # noqa: FIX004

    def agent_view(self) -> AgentView:
        """Return the agent's view of the fragment."""
        view = AgentView()
        view.add_text_chunk(f"JSON: {self.raw.data}")
        return view

    def user_view(self) -> UserView:
        """Return the user's view of the fragment."""
        view = UserView()

        content = ""
        for key, value in self.raw.data.items():
            content += f"{key.capitalize()}: {value}\n"

        view.renderables.append(TextRenderable(content.strip()))
        return view


class CodeFragmentKind(FragmentKind):
    """A raw data type for code fragments."""

    def __init__(self, raw: CodeRaw) -> None:
        """Initialize a code raw data type with code and optional language."""
        super().__init__("code", "A code fragment", raw)
        self.raw = raw  # hack to get proper typing  # noqa: FIX004

    def agent_view(self) -> AgentView:
        """Return the agent's view of the fragment."""
        view = AgentView()
        view.add_text_chunk(f"Code ({self.raw.language}):\n{self.raw.code}")
        return view

    def user_view(self) -> UserView:
        """Return the user's view of the fragment."""
        view = UserView()
        view.renderables.append(TextRenderable(f"Code ({self.raw.language}):\n{self.raw.code}"))
        return view


class LocationFragmentKind(JSONFragmentKind):
    """A raw data type for location fragments."""

    def __init__(self, raw: LocationRaw) -> None:
        """Initialize a location raw data type with latitude and longitude."""
        super().__init__("location", "A location fragment", raw)
        self.raw = raw  # hack to get proper typing  # noqa: FIX004


class DatetimeFragmentKind(JSONFragmentKind):
    """A raw data type for datetime fragments."""

    def __init__(self, raw: DatetimeRaw) -> None:
        """Initialize a datetime raw data type with a datetime string."""
        super().__init__("datetime", "A datetime fragment", raw)
        self.raw = raw  # hack to get proper typing  # noqa: FIX004
