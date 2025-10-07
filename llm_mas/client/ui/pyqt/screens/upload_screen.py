from __future__ import annotations  # noqa: D100

import asyncio
import contextlib
import json
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DirectoryTree, Footer, Header, ListItem, ListView, Static

from llm_mas.knowledge_base.knowledge_base import GLOBAL_KB

if TYPE_CHECKING:
    from textual.app import ComposeResult


class UploadScreen(Screen):
    """Screen for uploading files or folders into the app's uploads directory."""

    CSS_PATH = "../styles/screen.tcss"

    def __init__(self) -> None:
        """Initialize the upload screen."""
        super().__init__()
        self.selected_path: Path | None = None
        self.fs_tree: DirectoryTree | None = None
        self.selected_label: Static | None = None
        self.status: Static | None = None
        self._ingest_task: asyncio.Task | None = None
        self._progress_task: asyncio.Task | None = None

    def compose(self) -> ComposeResult:
        """Compose the upload UI."""
        yield Header(name="Upload Files/Folders")

        with Vertical(id="upload-root"):
            # Controls row (compact)
            with Horizontal(id="controls-row"):
                yield Button("Upload Selected", id="upload_btn")
                yield Button("Back", id="back_btn")

            # Current selection label
            self.selected_label = Static("Selected: <none>", classes="selected-path")
            yield self.selected_label

            # Main file browser should dominate space
            # Start at system root so users can navigate anywhere
            start_root = Path(os.sep) if os.sep else Path("/")
            self.fs_tree = DirectoryTree(str(start_root), id="fs_tree")
            yield self.fs_tree

            # Ingested items summary (below the tree so the tree gets priority space)
            yield Static("Ingested items (folders/files):", classes="ingested-header")
            self.ingested_list = ListView(id="ingested_list")
            yield self.ingested_list

            # Status line
            self.status = Static("", classes="upload-status")
            yield self.status

        yield Footer()

    def on_mount(self) -> None:
        """Load ingested items list from a separate file (not the KB records)."""
        self._roots_file = GLOBAL_KB.storage_path.with_name("kb_ingested_roots.json")
        self._ingested_roots: set[str] = set()
        self._load_ingested_roots()
        self._refresh_ingested_list()

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

    # ---- UI helpers ----
    def _get_upload_button(self) -> Button | None:
        try:
            return self.query_one("#upload_btn", Button)
        except Exception:  # noqa: BLE001
            return None

    def _set_button_text(self, button: Button, text: str) -> None:
        try:
            if hasattr(button, "label"):
                button.label = text
            else:
                button.update(text)
        except Exception as exc:  # noqa: BLE001
            logging.getLogger(__name__).debug("Failed to set button text: %s", exc)

    async def _handle_upload(self) -> None:
        """Kick off ingestion as a background task without blocking UI."""
        if self._ingest_task and not self._ingest_task.done():
            self._set_status("Ingestion already running in background…")
            return
        if not self.selected_path:
            self._set_status("No selection. Select a file or folder first.")
            return

        upload_btn = self._get_upload_button()
        old_label: str | None = None
        if upload_btn:
            try:
                old_label = str(getattr(upload_btn, "label", "Upload Selected"))
            except Exception:  # noqa: BLE001
                old_label = "Upload Selected"
            self._set_button_text(upload_btn, "Ingesting…")
            upload_btn.disabled = True

        async def run_ingest(path: Path, previous_label: str | None) -> None:
            try:
                self._set_status("Ingesting in background… You can continue using the app.")
                added = await GLOBAL_KB.index_path(path)
                if added == 0:
                    self._set_status(
                        "No indexable files found (supported: .txt, .md, .py, .json, .csv, .yaml, .yml, .toml, "
                        ".pdf, .docx, .html, .htm, .rtf).",
                    )
                else:
                    self._set_status(f"Indexed {added} chunks from: {path}")
                    self._ingested_roots.add(str(path))
                    self._save_ingested_roots()
                    self._refresh_ingested_list()
            except Exception as exc:  # noqa: BLE001
                self._set_status(f"Indexing failed: {exc!s}")
            finally:
                btn = self._get_upload_button()
                if btn:
                    btn.disabled = False
                    if previous_label is not None:
                        self._set_button_text(btn, previous_label)
                # Stop progress watcher
                if self._progress_task and not self._progress_task.done():
                    self._progress_task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await self._progress_task

        self._ingest_task = asyncio.create_task(run_ingest(self.selected_path, old_label))
        # Launch progress watcher that polls recent_progress for latest line
        if self._progress_task is None or self._progress_task.done():
            self._progress_task = asyncio.create_task(self._watch_progress())

    async def _watch_progress(self) -> None:
        """Periodically pull latest KB progress line and show it while ingesting."""
        try:
            while self._ingest_task and not self._ingest_task.done():
                lines = GLOBAL_KB.recent_progress(1)
                if lines:
                    # Only overwrite if we're still in ingestion phase
                    self._set_status(lines[-1])
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            pass

    async def on_unmount(self) -> None:  # type: ignore[override]
        """Ensure background ingestion is cancelled when leaving the screen."""
        if self._ingest_task and not self._ingest_task.done():
            self._ingest_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._ingest_task
        if self._progress_task and not self._progress_task.done():
            self._progress_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._progress_task

    # ---- Ingested roots persistence ----
    def _load_ingested_roots(self) -> None:
        try:
            if self._roots_file.exists():
                data = json.loads(self._roots_file.read_text(encoding="utf-8"))
                self._ingested_roots = {str(p) for p in data if isinstance(p, str)}
        except Exception:  # noqa: BLE001
            # If corrupt, start fresh
            self._ingested_roots = set()

    def _save_ingested_roots(self) -> None:
        try:
            self._roots_file.write_text(
                json.dumps(sorted(self._ingested_roots), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:  # noqa: BLE001
            # Non-fatal but log for visibility
            logging.getLogger(__name__).warning("Failed to save ingested roots: %s", exc)

    def _refresh_ingested_list(self) -> None:
        if not hasattr(self, "ingested_list") or self.ingested_list is None:
            return
        self.ingested_list.clear()
        for p in sorted(self._ingested_roots):
            self.ingested_list.append(ListItem(Static(p)))

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
        """Handle button actions with minimal branching."""
        if event.button.id == "back_btn":
            self.app.pop_screen()
            return
        if event.button.id == "upload_btn":
            await self._handle_upload()
