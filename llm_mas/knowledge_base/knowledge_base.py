"""Embedding-backed Knowledge Base used for Retrieval-Augmented Generation (RAG).

This module provides a lightweight vector store with:
- Simple text chunking
- Embeddings via Ollama (local) when available, optional OpenAI fallback
- JSON persistence on disk
- Cosine similarity search

Notes:
- We avoid external heavy deps (faiss, chroma, etc.).
- Default storage path: ``kb_index.json`` in the current working directory.

"""

from __future__ import annotations

import contextlib
import json
import logging
import math
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from llm_mas.logging.loggers import APP_LOGGER

if TYPE_CHECKING:
    from collections.abc import Callable

# Optional dependencies
try:  # pragma: no cover - optional import
    import ollama  # type: ignore[import-not-found]

    OLLAMA_AVAILABLE = True
except ImportError:  # pragma: no cover - optional import
    OLLAMA_AVAILABLE = False

try:  # pragma: no cover - optional import
    from openai import OpenAI  # type: ignore[import-not-found]

    OPENAI_AVAILABLE = True
except ImportError:  # pragma: no cover - optional import
    OpenAI = None  # type: ignore[assignment]
    OPENAI_AVAILABLE = False

# Optional parsers for document formats
try:  # pragma: no cover - optional import
    import pypdf  # type: ignore[import-not-found]

    PDF_AVAILABLE = True
except ImportError:  # pragma: no cover - optional import
    pypdf = None  # type: ignore[assignment]
    PDF_AVAILABLE = False

try:  # pragma: no cover - optional import
    import docx  # type: ignore[import-not-found]

    DOCX_AVAILABLE = True
except ImportError:  # pragma: no cover - optional import
    docx = None  # type: ignore[assignment]
    DOCX_AVAILABLE = False

try:  # pragma: no cover - optional import
    from bs4 import BeautifulSoup  # type: ignore[import-not-found]

    BS4_AVAILABLE = True
except ImportError:  # pragma: no cover - optional import
    BeautifulSoup = None  # type: ignore[assignment]
    BS4_AVAILABLE = False


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors.

    Returns 0.0 if either vector has zero magnitude or dimensions mismatch.
    """
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Chunk text into overlapping windows of characters.

    This is a simple heuristic that works fine for many text files.
    """
    if chunk_size <= 0:
        return [text]
    chunks: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        chunk = text[i : i + chunk_size]
        if chunk:
            chunks.append(chunk)
        i += max(1, chunk_size - overlap)
    return chunks


def _read_plain_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def _read_pdf(path: Path) -> str:
    if not PDF_AVAILABLE or pypdf is None:
        msg = "pypdf is not installed; cannot index PDF files."
        raise ValueError(msg)
    reader = pypdf.PdfReader(str(path))
    texts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(texts)


def _read_docx(path: Path) -> str:
    if not DOCX_AVAILABLE or docx is None:
        msg = "python-docx is not installed; cannot index DOCX files."
        raise ValueError(msg)
    document = docx.Document(str(path))
    return "\n".join(p.text for p in document.paragraphs)


def _read_html(path: Path) -> str:
    if not BS4_AVAILABLE or BeautifulSoup is None:
        msg = "beautifulsoup4 is not installed; cannot index HTML files."
        raise ValueError(msg)
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n")


def _read_rtf(path: Path) -> str:
    content = path.read_text(encoding="latin-1", errors="ignore")
    content = re.sub(r"\\[a-zA-Z]+-?\d* ?", "", content)
    return content.replace("{", "").replace("}", "")


def _read_text_file(path: Path) -> str:
    """Extract text content from a supported file (plain, PDF, DOCX, HTML, RTF)."""
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".py", ".json", ".csv", ".yaml", ".yml", ".toml"}:
        return _read_plain_text(path)
    if suffix == ".pdf":
        return _read_pdf(path)
    if suffix == ".docx":
        return _read_docx(path)
    if suffix in {".html", ".htm"}:
        return _read_html(path)
    if suffix == ".rtf":
        return _read_rtf(path)
    msg = f"Unsupported file type: {suffix}"
    raise ValueError(msg)


def _is_supported_file(path: Path) -> bool:
    """Return True if the file suffix is supported for indexing."""
    allowed = {
        ".txt",
        ".md",
        ".py",
        ".json",
        ".csv",
        ".yaml",
        ".yml",
        ".toml",
        ".pdf",
        ".docx",
        ".html",
        ".htm",
        ".rtf",
    }
    return path.is_file() and path.suffix.lower() in allowed


def _run_with_timeout(fn: Callable[[], Any], seconds: float | None) -> Any:
    """Run a blocking function with a timeout, raising TimeoutError on expiry."""
    if seconds is None or seconds <= 0:
        return fn()
    with ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(fn)
        try:
            return fut.result(timeout=seconds)
        except FuturesTimeoutError as exc:
            # Best-effort cancel (thread may keep running, but we can move on)
            fut.cancel()
            msg = f"Embedding request timed out after {seconds} seconds"
            raise TimeoutError(msg) from exc


class _EmbeddingProvider:
    """Simple embedding provider abstraction."""

    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("OLLAMA_EMBED_MODEL", "mxbai-embed-large")
        self._use_ollama = OLLAMA_AVAILABLE

        # Optional OpenAI fallback if API key is available
        self._openai_client = None
        if not self._use_ollama and OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY") and OpenAI is not None:
            try:
                self._openai_client = OpenAI()
                # Default embedding model for OpenAI
                if self.model in (None, "mxbai-embed-large"):
                    self.model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
            except (ValueError, RuntimeError):
                self._openai_client = None

    def embed_texts(self, texts: list[str], timeout: float | None = None) -> list[list[float]]:
        """Return embeddings for a list of texts.

        Prefers Ollama local embeddings; falls back to OpenAI if configured; otherwise raises.
        """
        if not texts:
            return []

        if self._use_ollama:
            # Ollama API accepts one prompt at a time; batch sequentially
            embeddings: list[list[float]] = []
            for t in texts:
                resp = _run_with_timeout(lambda t=t: ollama.embeddings(model=self.model, prompt=t), timeout)
                vec = resp.get("embedding")
                if not isinstance(vec, list):
                    msg = "Invalid embedding response from Ollama."
                    raise TypeError(msg)
                embeddings.append([float(v) for v in vec])
            return embeddings

        if self._openai_client is not None:
            # OpenAI new API: client.embeddings.create
            resp = _run_with_timeout(
                lambda: self._openai_client.embeddings.create(model=str(self.model), input=texts),
                timeout,
            )
            return [[float(v) for v in item.embedding] for item in resp.data]

        msg = (
            "No embedding backend available. Install/launch Ollama with an embedding model, or set OPENAI_API_KEY."
        )
        raise RuntimeError(msg)


@dataclass
class _KBRecord:
    """A single chunk record in the vector store."""

    id: int
    source_path: str
    chunk_id: int
    text: str
    embedding: list[float]

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_path": self.source_path,
            "chunk_id": self.chunk_id,
            "text": self.text,
            "embedding": self.embedding,
        }

    @staticmethod
    def from_json(d: dict[str, Any]) -> _KBRecord:
        return _KBRecord(
            id=int(d["id"]),
            source_path=str(d["source_path"]),
            chunk_id=int(d["chunk_id"]),
            text=str(d["text"]),
            embedding=[float(x) for x in d["embedding"]],
        )


class KnowledgeBase:
    """A simple, persistent vector-based knowledge base."""

    def __init__(self, storage_path: str | Path | None = None, embed_model: str | None = None) -> None:
        """Initialize the KnowledgeBase.

        Parameters
        ----------
        storage_path:
            Path to the JSON index file. Defaults to ``./kb_index.json`` if not provided.
        embed_model:
            Optional embedding model name. If None, uses a sensible default for the provider.

        """
        self.storage_path = Path(storage_path) if storage_path is not None else Path.cwd() / "kb_index.json"
        self._embedder = _EmbeddingProvider(embed_model)
        self._records: list[_KBRecord] = []
        self._next_id = 1
        self._load()

    # --------------- Persistence ---------------
    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
            # Support both dict-based index { records: [...], next_id: n } and
            # legacy/simple list-based index [ {...record...}, ... ]
            if isinstance(data, list):
                records: list[_KBRecord] = []
                for item in data:
                    if isinstance(item, dict):
                        try:
                            records.append(_KBRecord.from_json(item))
                        except (KeyError, TypeError, ValueError) as exc:
                            APP_LOGGER.warning(
                                "Skipping invalid KB record in list index: %s", exc,
                            )
                    else:
                        APP_LOGGER.warning(
                            "Ignoring non-dict item in KB index list: %r", item,
                        )
                self._records = records
                self._next_id = len(self._records) + 1
            elif isinstance(data, dict):
                self._records = [_KBRecord.from_json(d) for d in data.get("records", [])]
                self._next_id = int(data.get("next_id", len(self._records) + 1))
            else:
                # Unknown format; reset
                self._records = []
                self._next_id = 1
        except (OSError, json.JSONDecodeError):
            # Corrupt or incompatible index; start fresh
            APP_LOGGER.warning("KB index file is corrupt or unreadable. Starting with a fresh index.")
            self._records = []
            self._next_id = 1

    def _save(self) -> None:
        payload = {
            "next_id": self._next_id,
            "records": [r.to_json() for r in self._records],
        }
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # --------------- Indexing ---------------
    def add_text(self, text: str, source_path: str = "unknown", chunk_id: int = 0) -> _KBRecord:
        """Embed and add a single text chunk to the KB.

        Returns the created record.
        """
        vec = self._embedder.embed_texts([text])[0]
        rec = _KBRecord(
            id=self._next_id,
            source_path=source_path,
            chunk_id=chunk_id,
            text=text,
            embedding=vec,
        )
        self._records.append(rec)
        self._next_id += 1
        return rec

    def index_path(
        self,
        path: Path,
        progress: Callable[[Path, int, int]] | None = None,
        on_error: Callable[[Path, str], None] | None = None,
        embed_timeout: float | None = None,
    ) -> int:
        """Index a file or directory.

        Parameters
        ----------
        path : Path
            Path to a file or directory. Directories are scanned recursively.
        progress : Callable[[Path, int, int]] | None
            Optional callback invoked as progress(file_path, index, total) before each file is processed.
        on_error : Callable[[Path, str], None] | None
            Optional callback invoked when a file fails to read or embed. Receives the file path and error message.
        embed_timeout : float | None
            Optional timeout in seconds applied to each embedding request for a file's chunks.

        Returns
        -------
        int
            Number of chunks added to the KB.

        """
        logger = APP_LOGGER

        def _gather_files(root_path: Path) -> list[Path]:
            """Collect supported files respecting caps and skip rules."""
            max_scan_files = int(os.getenv("KB_MAX_SCAN_FILES", "10000"))
            max_file_bytes = int(os.getenv("KB_MAX_FILE_BYTES", "2097152"))
            collected: list[Path] = []
            if root_path.is_dir():
                for r, dirnames, filenames in os.walk(root_path):  # pragma: no branch - linear scan
                    dirnames[:] = list(dirnames)
                    for fname in filenames:
                        fp = Path(r) / fname
                        if not _is_supported_file(fp):
                            continue
                        with contextlib.suppress(OSError):
                            if fp.stat().st_size > max_file_bytes:
                                logger.info("Skipping large file (>%d bytes): %s", max_file_bytes, fp)
                                continue
                        collected.append(fp)
                        if len(collected) >= max_scan_files:
                            logger.warning(
                                "Reached KB_MAX_SCAN_FILES cap (%d). Further supported files will be ignored.",
                                max_scan_files,
                            )
                            return collected
            elif _is_supported_file(root_path):
                try:
                    if root_path.stat().st_size <= int(os.getenv("KB_MAX_FILE_BYTES", "2097152")):
                        collected.append(root_path)
                    else:
                        logger.info(
                            "Skipping large file (>%s bytes): %s",
                            os.getenv("KB_MAX_FILE_BYTES", "2097152"),
                            root_path,
                        )
                except OSError as exc:  # pragma: no cover
                    logger.warning("Unable to stat file %s: %s", root_path, exc)
            return collected

        logger.info("KB indexing started: path=%s embed_timeout=%s", path, embed_timeout)
        if progress is not None:
            with contextlib.suppress(Exception):
                progress(path, 0, 0)
        paths, scan_time = self._gather_files_for_index(path, logger)
        ctx = self._ProcCtx(
            root_path=path,
            enum_duration=scan_time,
            progress=progress,
            on_error=on_error,
            embed_timeout=embed_timeout,
            logger=logger,
        )
        return self._process_files_for_index(paths, ctx)

    # --- helpers extracted to reduce complexity of public API method ---
    def _gather_files_for_index(self, root_path: Path, logger: logging.Logger) -> tuple[list[Path], float]:
        """Gather supported files with size & count limits; returns (paths, scan_seconds)."""
        scan_start = time.monotonic()
        max_scan_files = int(os.getenv("KB_MAX_SCAN_FILES", "10000"))
        max_file_bytes = int(os.getenv("KB_MAX_FILE_BYTES", "2097152"))
        paths: list[Path] = []

        def want(fp: Path) -> bool:
            if not _is_supported_file(fp):
                return False
            try:
                return fp.stat().st_size <= max_file_bytes
            except OSError:  # pragma: no cover
                return False

        if not root_path.is_dir():  # Simple file case
            if want(root_path):  # Only append if supported & under size
                paths.append(root_path)
            duration = time.monotonic() - scan_start
            logger.info("KB scan complete: supported_files=%d (%.2fs) path=%s", len(paths), duration, root_path)
            return paths, duration

        for r, dirnames, filenames in os.walk(root_path):
            dirnames[:] = list(dirnames)
            for fname in filenames:
                fp = Path(r) / fname
                if want(fp):
                    paths.append(fp)
                    if len(paths) >= max_scan_files:
                        logger.warning(
                            "Reached KB_MAX_SCAN_FILES cap (%d). Stopping scan.", max_scan_files,
                        )
                        break
            if len(paths) >= max_scan_files:
                break
        enum_duration = time.monotonic() - scan_start
        logger.info("KB scan complete: supported_files=%d (%.2fs) path=%s", len(paths), enum_duration, root_path)
        return paths, enum_duration

    @dataclass
    class _ProcCtx:
        root_path: Path
        enum_duration: float
        progress: Callable[[Path, int, int]] | None
        on_error: Callable[[Path, str], None] | None
        embed_timeout: float | None
        logger: logging.Logger

    def _process_files_for_index(self, paths: list[Path], ctx: _ProcCtx) -> int:
        total_local = len(paths)
        added_local = 0
        ingest_start_local = time.monotonic()
        for idx, file_path in enumerate(paths, start=1):
            file_start = time.monotonic()
            if ctx.progress is not None:
                with contextlib.suppress(Exception):
                    ctx.progress(file_path, idx, total_local)
            file_chunks_added = self._index_single_file(
                file_path, on_error=ctx.on_error, embed_timeout=ctx.embed_timeout,
            )
            added_local += file_chunks_added
            file_duration = time.monotonic() - file_start
            ctx.logger.info(
                "KB file indexed: file=%s chunks=%d duration=%.2fs total_chunks_after=%d",
                file_path,
                file_chunks_added,
                file_duration,
                self._next_id - 1,
            )
            # Provide an additional progress callback AFTER a file finishes indexing so UIs
            # can reflect completion (some large files may take a while and only had a pre-file update).
            if ctx.progress is not None:
                with contextlib.suppress(Exception):
                    ctx.progress(file_path, idx, total_local)
            if ctx.logger.isEnabledFor(logging.DEBUG):
                ctx.logger.debug(
                    "KB progress: %d/%d files (%.1f%%) cumulative_chunks=%d",
                    idx,
                    total_local,
                    (idx / total_local) * 100 if total_local else 0.0,
                    self._next_id - 1,
                )
        if added_local:
            self._save()
        ingest_duration_local = time.monotonic() - ingest_start_local
        ctx.logger.info(
            "KB indexing finished: root=%s files_processed=%d chunks_added=%d scan_time=%.2fs ingest_time=%.2fs",
            ctx.root_path,
            total_local,
            added_local,
            ctx.enum_duration,
            ingest_duration_local,
        )
        if added_local == 0:
            ctx.logger.warning("KB indexing produced no new chunks for path=%s", ctx.root_path)
        return added_local

    def _index_single_file(
        self,
        p: Path,
        on_error: Callable[[Path, str], None] | None = None,
        embed_timeout: float | None = None,
    ) -> int:
        """Index a single supported file; returns number of chunks added.

        Skips unreadable or empty files and logs at INFO/WARN levels. Any embedding
        errors for a single file are contained and won't stop the folder ingestion.
        """
        try:
            text = _read_text_file(p)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            APP_LOGGER.warning("Skipping unreadable file %s: %s", p, exc)
            if on_error is not None:
                with contextlib.suppress(Exception):
                    on_error(p, f"Read failed: {exc}")
            return 0

        if not text or not text.strip():
            APP_LOGGER.info("Skipping empty file: %s", p)
            return 0

        chunks = _chunk_text(text)
        if not chunks:
            APP_LOGGER.info("No chunks produced for file: %s", p)
            return 0

        try:
            embeddings = self._embedder.embed_texts(chunks, timeout=embed_timeout)
        except Exception as exc:  # noqa: BLE001
            APP_LOGGER.warning("Embedding failed for %s: %s", p, exc)
            if on_error is not None:
                with contextlib.suppress(Exception):
                    on_error(p, f"Embedding failed: {exc}")
            return 0

        added = 0
        for i, (chunk, vec) in enumerate(zip(chunks, embeddings, strict=True)):
            rec = _KBRecord(id=self._next_id, source_path=str(p), chunk_id=i, text=chunk, embedding=vec)
            self._records.append(rec)
            self._next_id += 1
            added += 1
        return added

    # --------------- Query ---------------
    def query(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Return the top_k most similar chunks for the given query string.

        Each result contains: { text, source_path, score }.
        """
        if not query.strip() or not self._records:
            return []
        qvec = self._embedder.embed_texts([query])[0]
        scored = [
            {
                "text": r.text,
                "source_path": r.source_path,
                "score": _cosine_similarity(qvec, r.embedding),
            }
            for r in self._records
        ]
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[: max(1, top_k)]


# Global singleton to share across UI and actions
GLOBAL_KB = KnowledgeBase()

