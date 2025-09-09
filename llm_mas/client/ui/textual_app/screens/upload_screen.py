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
from llm_mas.logging.loggers import APP_LOGGER

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
        """Ensure legacy upload directory exists (for display only)."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        # Load ingested items list from a separate file (not the KB records)
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

    def _index_into_kb(self, source: Path) -> int:
        """Index a file or directory into the Knowledge Base. Returns chunks added."""
        # Progress callback runs in a worker thread; marshal UI updates safely to the main thread
        def progress_cb(file_path: Path, idx: int, total: int) -> None:
            # Light debug log so we can confirm callback execution even if UI doesn't reflect it
            if APP_LOGGER.isEnabledFor(logging.DEBUG):
                APP_LOGGER.debug("KB progress callback: %s (%d/%d)", file_path, idx, total)

            # Update status with current file (or done if idx == total and called post-file)
            label = f"Ingesting ({idx}/{total}): {file_path}" if total else f"Scanning: {file_path}"
            self._set_status(label)
            btn = self._get_upload_button()
            if btn is not None:
                phase_suffix = "✓" if idx == total else "…"
                self._set_button_text(btn, f"Ingesting {idx}/{total}{phase_suffix}")
                with contextlib.suppress(Exception):
                    btn.refresh()
            # Also refresh status widget explicitly (older Textual versions sometimes need it)
            if self.status is not None:
                with contextlib.suppress(Exception):
                    self.status.refresh()

        return GLOBAL_KB.index_path(source, progress=progress_cb, embed_timeout=30)

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
        """Run ingestion with a simple loading indicator and update UI state."""
        if not self.selected_path:
            self._set_status("No selection. Select a file or folder first.")
            return

        self._set_status("Ingesting… Please wait…")

        upload_btn = self._get_upload_button()
        old_label: str | None = None
        if upload_btn is not None:
            try:
                old_label = str(getattr(upload_btn, "label", "Upload Selected"))
            except Exception:  # noqa: BLE001
                old_label = "Upload Selected"
            self._set_button_text(upload_btn, "Ingesting…")
            upload_btn.disabled = True

        try:
            added = await asyncio.to_thread(self._index_into_kb, self.selected_path)
            if added == 0:
                self._set_status(
                    "No indexable files found (supported: .txt, .md, .py, .json, .csv, .yaml, .yml, .toml, "
                    ".pdf, .docx, .html, .htm, .rtf).",
                )
            else:
                self._set_status(f"Indexed {added} chunks from: {self.selected_path}")
                # Track ingested root, whether file or folder
                self._ingested_roots.add(str(self.selected_path))
                self._save_ingested_roots()
                self._refresh_ingested_list()
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Indexing failed: {exc!s}")
        finally:
            if upload_btn is not None:
                upload_btn.disabled = False
                try:
                    if old_label is not None:
                        self._set_button_text(upload_btn, old_label)
                except Exception as e:  # noqa: BLE001
                    logging.getLogger(__name__).warning("Failed to restore upload button label: %s", e)

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
