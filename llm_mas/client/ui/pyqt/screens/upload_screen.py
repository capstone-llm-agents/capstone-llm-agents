"""PyQt6 upload screen for knowledge base ingestion."""

from __future__ import annotations

import asyncio
import json
import re
import time
from pathlib import Path

from PyQt6.QtCore import QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from llm_mas.knowledge_base.knowledge_base import GLOBAL_KB
from llm_mas.logging.loggers import APP_LOGGER


class IndexingWorker(QThread):
    """Background worker thread for indexing files without blocking UI."""

    progress = pyqtSignal(str)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, path: Path) -> None:
        """Initialize the worker with a path to index."""
        super().__init__()
        self.path = path

    def run(self) -> None:
        """Run the indexing in a background thread."""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            self.progress.emit(f"Starting indexing of: {self.path}")
            chunks_added = loop.run_until_complete(GLOBAL_KB.index_path(self.path))

            if chunks_added == 0:
                self.progress.emit(
                    "No indexable files found (supported: .txt, .md, .py, .json, .csv, "
                    ".yaml, .yml, .toml, .pdf, .docx, .html, .htm, .rtf)",
                )
            else:
                self.progress.emit(f"✓ Successfully indexed {chunks_added} chunks")

            self.finished.emit(chunks_added)
            loop.close()
        except Exception as exc:
            APP_LOGGER.exception("Indexing failed")
            self.error.emit(f"✗ Indexing failed: {exc!s}")


class UploadScreen(QWidget):
    """PyQt6 screen for uploading files and folders to the knowledge base."""

    def __init__(self, client, nav) -> None:
        """Initialize the upload screen."""
        super().__init__()
        self.client = client
        self.nav = nav
        self.selected_path: Path | None = None
        self._worker: IndexingWorker | None = None
        self._roots_file = GLOBAL_KB.storage_path.with_name("kb_ingested_roots.json")
        self._ingested_roots: set[str] = set()
        self._progress_timer: QTimer | None = None
        self._last_progress_line: str = ""
        self._init_ui()
        self._load_ingested_roots()
        self._refresh_ingested_list()

    def _init_ui(self) -> None:
        """Initialize the PyQt6 UI."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QLabel("📚 Upload Files/Folders to Knowledge Base")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px; color: #2196F3;")
        layout.addWidget(title)

        # Controls row
        controls_layout = QHBoxLayout()

        self.back_btn = QPushButton("← Back to Menu")
        self.back_btn.clicked.connect(self._on_back)
        self.back_btn.setStyleSheet("padding: 8px 15px;")
        controls_layout.addWidget(self.back_btn)

        controls_layout.addStretch()

        self.select_file_btn = QPushButton("📄 Select File")
        self.select_file_btn.clicked.connect(self._on_select_file)
        self.select_file_btn.setStyleSheet("padding: 8px 15px;")
        controls_layout.addWidget(self.select_file_btn)

        self.select_folder_btn = QPushButton("📁 Select Folder")
        self.select_folder_btn.clicked.connect(self._on_select_folder)
        self.select_folder_btn.setStyleSheet("padding: 8px 15px;")
        controls_layout.addWidget(self.select_folder_btn)

        self.upload_btn = QPushButton("⬆ Upload Selected")
        self.upload_btn.clicked.connect(self._on_upload)
        self.upload_btn.setEnabled(False)
        self.upload_btn.setStyleSheet("padding: 8px 15px; background-color: #4CAF50; color: white; font-weight: bold;")
        controls_layout.addWidget(self.upload_btn)

        layout.addLayout(controls_layout)  # Selected path label
        self.selected_label = QLabel("📂 Selected: <none>")
        self.selected_label.setStyleSheet(
            "margin: 10px 5px; padding: 8px; font-weight: bold; color: #2196F3; "
            "background-color: #E3F2FD; border-radius: 4px;",
        )
        layout.addWidget(self.selected_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: 2px solid #2196F3; border-radius: 5px; text-align: center; }"
            "QProgressBar::chunk { background-color: #4CAF50; }",
        )
        layout.addWidget(self.progress_bar)

        # Current progress label (bold and prominent)
        self.current_progress_label = QLabel("")
        self.current_progress_label.setVisible(False)
        self.current_progress_label.setStyleSheet(
            "margin: 5px; padding: 10px; font-weight: bold; font-size: 14px; "
            "color: #1976D2; background-color: #FFF9C4; border-left: 4px solid #FBC02D; "
            "border-radius: 4px;",
        )
        self.current_progress_label.setWordWrap(True)
        layout.addWidget(self.current_progress_label)

        # Status/Progress area
        status_label = QLabel("📊 Status & Progress Log:")
        status_label.setStyleSheet("margin-top: 10px; font-weight: bold;")
        layout.addWidget(status_label)

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        self.status_text.setPlaceholderText("Status messages will appear here...")
        self.status_text.setStyleSheet(
            "QTextEdit { background-color: #FAFAFA; border: 1px solid #E0E0E0; border-radius: 4px; padding: 5px; }",
        )
        layout.addWidget(self.status_text)

        # Ingested items list
        ingested_label = QLabel("✅ Previously Ingested Items:")
        ingested_label.setStyleSheet("margin-top: 10px; font-weight: bold;")
        layout.addWidget(ingested_label)

        self.ingested_list = QListWidget()
        self.ingested_list.setMaximumHeight(150)
        self.ingested_list.setStyleSheet(
            "QListWidget { background-color: #FAFAFA; border: 1px solid #E0E0E0; "
            "border-radius: 4px; } "
            "QListWidget::item { padding: 5px; } "
            "QListWidget::item:hover { background-color: #E8F5E9; }",
        )
        layout.addWidget(self.ingested_list)

        # KB stats
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet(
            "margin: 10px 5px; padding: 8px; font-weight: bold; "
            "color: #1976D2; background-color: #E3F2FD; border-radius: 4px;",
        )
        layout.addWidget(self.stats_label)
        self._update_stats()

    def _update_stats(self) -> None:
        """Update the knowledge base statistics display."""
        count = GLOBAL_KB.record_count()
        self.stats_label.setText(f"📊 Knowledge Base: {count:,} chunks indexed")

    def _add_status(self, message: str, msg_type: str = "info") -> None:
        """Add a color-coded status message to the status text area."""
        # Color code based on message type
        colors = {
            "info": "#2196F3",  # Blue
            "success": "#4CAF50",  # Green
            "error": "#F44336",  # Red
            "warning": "#FF9800",  # Orange
            "progress": "#9C27B0",  # Purple
        }
        color = colors.get(msg_type, "#000000")

        timestamp = time.strftime("%H:%M:%S")
        html_message = f'<span style="color: {color};">[{timestamp}] {message}</span>'
        self.status_text.append(html_message)

    def _set_selected(self, path: Path | None) -> None:
        """Set the selected path and update the UI."""
        self.selected_path = path
        if path:
            icon = "📄" if path.is_file() else "📁"
            self.selected_label.setText(f"{icon} Selected: {path}")
            self.upload_btn.setEnabled(True)
        else:
            self.selected_label.setText("📂 Selected: <none>")
            self.upload_btn.setEnabled(False)

    def _on_select_file(self) -> None:
        """Handle file selection button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File to Index",
            str(Path.home()),
            "All Files (*);;Text Files (*.txt *.md);;Python Files (*.py);;Documents (*.pdf *.docx)",
        )
        if file_path:
            self._set_selected(Path(file_path))
            self._add_status(f"📄 File selected: {file_path}", "info")

    def _on_select_folder(self) -> None:
        """Handle folder selection button click."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Index",
            str(Path.home()),
        )
        if folder_path:
            self._set_selected(Path(folder_path))
            self._add_status(f"📁 Folder selected: {folder_path}", "info")

    def _on_upload(self) -> None:
        """Handle upload button click."""
        if not self.selected_path:
            self._add_status("⚠ No path selected", "warning")
            return

        if self._worker and self._worker.isRunning():
            self._add_status("⚠ Indexing already in progress", "warning")
            return

        # Show progress bar and current progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.current_progress_label.setVisible(True)
        self.current_progress_label.setText("🔄 Initializing indexing...")

        # Disable buttons during indexing
        self.select_file_btn.setEnabled(False)
        self.select_folder_btn.setEnabled(False)
        self.upload_btn.setEnabled(False)
        self.upload_btn.setText("⏳ Indexing...")
        self.upload_btn.setStyleSheet("padding: 8px 15px; background-color: #FFA726; color: white; font-weight: bold;")

        # Create and start worker thread
        self._worker = IndexingWorker(self.selected_path)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

        # Start polling for progress updates
        self._start_progress_polling()

    def _start_progress_polling(self) -> None:
        """Start polling the knowledge base for progress updates."""
        self._progress_timer = QTimer()
        self._progress_timer.timeout.connect(self._poll_progress)
        self._progress_timer.start(500)  # Poll every 500ms

    def _poll_progress(self) -> None:
        """Poll the knowledge base for the latest progress."""
        try:
            recent = GLOBAL_KB.recent_progress(1)
            if recent and recent[0] != self._last_progress_line:
                self._last_progress_line = recent[0]

                # Parse progress line for percentage
                if "KB progress:" in self._last_progress_line:
                    # Extract percentage
                    match = re.search(r"(\d+)/(\d+) files \((\d+\.?\d*)%\)", self._last_progress_line)
                    if match:
                        current = int(match.group(1))
                        total = int(match.group(2))
                        percent = float(match.group(3))

                        # Update progress bar
                        if self.progress_bar.maximum() == 0:  # Was indeterminate
                            self.progress_bar.setRange(0, 100)
                        self.progress_bar.setValue(int(percent))

                        # Update current progress label (bold and prominent)
                        self.current_progress_label.setText(
                            f"🔄 Processing: {current}/{total} files ({percent:.1f}%) - "
                            f"{self._last_progress_line.split('cumulative_chunks=')[1].split()[0]} chunks indexed",
                        )

                        self._add_status(self._last_progress_line, "progress")

                elif "KB file indexed:" in self._last_progress_line:
                    # Extract filename and display it prominently
                    if "file=" in self._last_progress_line:
                        file_part = self._last_progress_line.split("file=")[1].split()[0]
                        file_name = Path(file_part).name
                        self.current_progress_label.setText(f"📝 Indexing: {file_name}")

                    self._add_status(self._last_progress_line, "info")

                else:
                    # Other messages
                    self._add_status(self._last_progress_line, "info")

        except Exception as exc:
            APP_LOGGER.debug(f"Progress polling error: {exc}")

    def _stop_progress_polling(self) -> None:
        """Stop polling for progress updates."""
        if self._progress_timer:
            self._progress_timer.stop()
            self._progress_timer = None

    def _on_progress(self, message: str, msg_type: str = "info") -> None:
        """Handle progress updates from the worker thread."""
        self._add_status(message, msg_type)
        # Also update current progress label for important messages
        if msg_type in ("success", "error"):
            self.current_progress_label.setText(message)

    def _on_finished(self, chunks_added: int) -> None:
        """Handle successful completion of indexing."""
        self._stop_progress_polling()

        # Hide progress bar but keep final message visible briefly
        self.progress_bar.setVisible(False)

        if chunks_added > 0 and self.selected_path:
            self._ingested_roots.add(str(self.selected_path))
            self._save_ingested_roots()
            self._refresh_ingested_list()
            self._add_status(
                f"✅ Indexing complete! Added {chunks_added:,} chunks to knowledge base.",
                "success",
            )
        else:
            self._add_status("⚠ Indexing complete but no chunks were added.", "warning")

        self._update_stats()

        # Hide current progress after a delay
        QTimer.singleShot(3000, lambda: self.current_progress_label.setVisible(False))

        # Re-enable buttons
        self.select_file_btn.setEnabled(True)
        self.select_folder_btn.setEnabled(True)
        self.upload_btn.setEnabled(bool(self.selected_path))
        self.upload_btn.setText("⬆ Upload Selected")
        self.upload_btn.setStyleSheet("padding: 8px 15px; background-color: #4CAF50; color: white; font-weight: bold;")

    def _on_error(self, error_message: str) -> None:
        """Handle indexing errors."""
        self._stop_progress_polling()

        self.progress_bar.setVisible(False)
        self.current_progress_label.setText(error_message)

        self._add_status(error_message, "error")

        # Hide error message after a longer delay
        QTimer.singleShot(5000, lambda: self.current_progress_label.setVisible(False))

        # Re-enable buttons
        self.select_file_btn.setEnabled(True)
        self.select_folder_btn.setEnabled(True)
        self.upload_btn.setEnabled(bool(self.selected_path))
        self.upload_btn.setText("⬆ Upload Selected")
        self.upload_btn.setStyleSheet("padding: 8px 15px; background-color: #4CAF50; color: white; font-weight: bold;")

    def _on_back(self) -> None:
        """Handle back button click."""
        self.nav.navigate.emit("main_menu", None)

    # ---- Ingested roots persistence ----
    def _load_ingested_roots(self) -> None:
        """Load the list of previously ingested paths."""
        try:
            if self._roots_file.exists():
                data = json.loads(self._roots_file.read_text(encoding="utf-8"))
                self._ingested_roots = {str(p) for p in data if isinstance(p, str)}
        except Exception:  # noqa: BLE001
            # If corrupt, start fresh
            self._ingested_roots = set()

    def _save_ingested_roots(self) -> None:
        """Save the list of ingested paths."""
        try:
            self._roots_file.write_text(
                json.dumps(sorted(self._ingested_roots), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:  # noqa: BLE001
            APP_LOGGER.warning("Failed to save ingested roots: %s", exc)

    def _refresh_ingested_list(self) -> None:
        """Refresh the list of previously ingested items with color coding."""
        self.ingested_list.clear()
        for p in sorted(self._ingested_roots):
            path = Path(p)
            # Color code by type
            if path.is_file():
                icon = "📄"
                color = "#1976D2"  # Blue for files
            else:
                icon = "📁"
                color = "#4CAF50"  # Green for folders

            item = QListWidgetItem(f"{icon} {p}")
            color = QColor(color)
            item.setForeground(color)
            self.ingested_list.addItem(item)
