from __future__ import annotations  # noqa: D100

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DirectoryTree, Footer, Header, Static

from llm_mas.knowledge_base.knowledge_base import GLOBAL_KB

if TYPE_CHECKING:
    from textual.app import ComposeResult


class UploadScreen(Screen):
    """Screen for uploading files or folders into the app's uploads directory."""

    CSS_PATH = "../styles/screen.tcss"

    def __init__(self) -> None:
        """Initialize the upload screen."""
        super().__init__()
        # We no longer duplicate files. Keep `uploads` for backward-compat display only.
        self.upload_dir = Path.cwd() / "uploads"
        self.selected_path: Path | None = None
        # Use a non-conflicting name; `tree` is a property on Textual DOM nodes.
        self.fs_tree: DirectoryTree | None = None
        self.selected_label: Static | None = None
        self.status: Static | None = None

    def compose(self) -> ComposeResult:
        """Compose the upload UI."""
        yield Header(name="Upload Files/Folders")

        with Vertical(id="upload-root"):
            with Horizontal():
                yield Static(f"Upload target: {self.upload_dir}", classes="upload-target")

            with Horizontal():
                yield Button("Upload Selected", id="upload_btn")
                yield Button("Back", id="back_btn")

            self.selected_label = Static("Selected: <none>", classes="selected-path")
            yield self.selected_label

            # File browser
            self.fs_tree = DirectoryTree(str(Path.cwd()), id="fs_tree")
            yield self.fs_tree

            self.status = Static("", classes="upload-status")
            yield self.status

        yield Footer()

    def on_mount(self) -> None:
        """Ensure legacy upload directory exists (for display only)."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _set_status(self, message: str) -> None:
        if self.status:
            self.status.update(message)

    def _set_selected(self, path: Path | None) -> None:
        self.selected_path = path
        if self.selected_label:
            self.selected_label.update(f"Selected: {path if path else '<none>'}")

    def _unique_target(self, target: Path) -> Path:
        """Return a unique path if target exists by adding -1, -2, ... suffix."""
        if not target.exists():
            return target
        stem = target.stem
        suffix = target.suffix
        parent = target.parent
        i = 1
        while True:
            candidate = parent / f"{stem}-{i}{suffix}"
            if not candidate.exists():
                return candidate
            i += 1

    def _index_into_kb(self, source: Path) -> int:
        """Index a file or directory into the Knowledge Base. Returns chunks added."""
        return GLOBAL_KB.index_path(source)

    # File selected in DirectoryTree
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection."""
        self._set_selected(Path(event.path))
        self._set_status("")

    # Directory selected in DirectoryTree
    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Handle directory selection."""
        self._set_selected(Path(event.path))
        self._set_status("")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button actions."""
        if event.button.id == "back_btn":
            self.app.pop_screen()
            return

        if event.button.id == "upload_btn":
            if not self.selected_path:
                self._set_status("No selection. Select a file or folder first.")
                return

            try:
                added = await asyncio.to_thread(self._index_into_kb, self.selected_path)
                if added == 0:
                    self._set_status(
                        "No indexable files found (supported: .txt, .md, .py, .json, .csv, .yaml, .yml, .toml).",
                    )
                else:
                    self._set_status(f"Indexed {added} chunks from: {self.selected_path}")
            except Exception as e:  # noqa: BLE001
                self._set_status(f"Indexing failed: {e!s}")
