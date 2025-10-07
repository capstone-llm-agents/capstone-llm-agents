"""The user view of a fragment is a pretty representation for the user."""

from enum import Enum, auto
from typing import Any

from llm_mas.fragment.view import FragmentView


class FileIcon(Enum):
    """An icon for a file type."""

    GENERIC = auto()
    IMAGE = auto()
    AUDIO = auto()
    VIDEO = auto()
    PDF = auto()
    WORD = auto()
    EXCEL = auto()
    POWERPOINT = auto()
    TEXT = auto()
    CODE = auto()


class UserView(FragmentView):
    """The user view of a fragment is a pretty representation for the user."""

    def __init__(self) -> None:
        """Initialize a user view."""
        self.renderables: list[Renderable] = []


class Renderable:
    """A renderable object."""


class TextRenderable(Renderable):
    """A renderable text object."""

    def __init__(self, content: str) -> None:
        """Initialize a renderable text object with content."""
        self.content = content


class FileRenderable(Renderable):
    """A renderable file object."""

    def __init__(self, file_path: str) -> None:
        """Initialize a renderable file object with a file path."""
        self.file_path = file_path
        self.file_name = file_path.split("/")[-1]
        self.icon = self.determine_icon(file_path)

    @staticmethod
    def determine_icon(file_path: str) -> FileIcon:  # noqa: PLR0911
        """Determine the icon for a file based on its extension."""
        extension = file_path.split(".")[-1].lower()
        if extension in ["jpg", "jpeg", "png", "gif", "bmp", "svg", "tiff"]:
            return FileIcon.IMAGE
        if extension in ["mp3", "wav", "aac", "flac", "ogg"]:
            return FileIcon.AUDIO
        if extension in ["mp4", "avi", "mov", "mkv", "wmv"]:
            return FileIcon.VIDEO
        if extension == "pdf":
            return FileIcon.PDF
        if extension in ["doc", "docx"]:
            return FileIcon.WORD
        if extension in ["xls", "xlsx"]:
            return FileIcon.EXCEL
        if extension in ["ppt", "pptx"]:
            return FileIcon.POWERPOINT
        if extension in ["txt", "md", "rtf"]:
            return FileIcon.TEXT
        if extension in [
            "py",
            "js",
            "java",
            "c",
            "cpp",
            "html",
            "css",
            "json",
            "xml",
            "yaml",
            "yml",
            "sh",
        ]:
            return FileIcon.CODE
        return FileIcon.GENERIC


class ImageRenderable(FileRenderable):
    """A renderable image object."""

    def __init__(self, file_path: str, alt_text: str = "") -> None:
        """Initialize a renderable image object with a file path and optional alt text."""
        super().__init__(file_path)
        self.alt_text = alt_text


class JSONRenderable(Renderable):
    """A renderable JSON object."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize a renderable JSON object with a dictionary."""
        self.data = data


class CodeRenderable(Renderable):
    """A renderable code object."""

    def __init__(self, code: str, language: str) -> None:
        """Initialize a renderable code object with code and optional language."""
        self.code = code
        self.language = language
