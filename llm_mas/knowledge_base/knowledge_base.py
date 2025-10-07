"""Embedding-backed Knowledge Base used for Retrieval-Augmented Generation (RAG).

This module provides a lightweight vector store with:
- Simple text chunking
- Embeddings via Ollama (local) when available, optional OpenAI fallback
- JSON persistence on disk
- Cosine similarity search

Notes:
- Default storage path: ``kb_index.json`` in the current working directory.

"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import re
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import docx
import ollama
import pypdf
from bs4 import BeautifulSoup
from openai import OpenAI

from llm_mas.logging.loggers import APP_LOGGER

if TYPE_CHECKING:
    import logging


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

def _fixed_size_chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
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


def _recursive_chunk_text(
    text: str,
    max_chunk_size: int = 1000,
    chunk_overlap: int = 200,
    separators: list[str] | None = None,
) -> list[str]:
    r"""Recursively split ``text`` into overlapping chunks.

    See helper functions: ``_rc_split_leaves`` and ``_rc_pack`` for the two phases.
    """
    if not text:
        return []
    if max_chunk_size <= 0:
        return [text]
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]
    if chunk_overlap >= max_chunk_size:
        chunk_overlap = max(0, max_chunk_size // 5)
    leaves = _rc_split_leaves(text, max_chunk_size, separators)
    if not leaves:
        return []
    return _rc_pack(leaves, max_chunk_size, chunk_overlap)


def _rc_split_leaves(text: str, max_chunk_size: int, separators: list[str]) -> list[str]:
    """Return list of fragments <= max_chunk_size by hierarchical splitting."""
    result: list[str] = []
    stack: list[tuple[str, int]] = [(text, 0)]
    last_sep_idx = len(separators)
    while stack:
        frag, idx = stack.pop()
        if len(frag) <= max_chunk_size:
            result.append(frag)
            continue
        if idx >= last_sep_idx:
            result.extend(
                frag[i : i + max_chunk_size] for i in range(0, len(frag), max_chunk_size)
            )
            continue
        sep = separators[idx]
        if sep and sep in frag:
            parts = [p for p in frag.split(sep) if p]
            if len(parts) == 1:
                stack.append((frag, idx + 1))
            else:
                # Reverse push to preserve order
                stack.extend((p, idx + 1) for p in reversed(parts))
        else:
            stack.append((frag, idx + 1))
    result.reverse()
    return result


def _rc_pack(fragments: list[str], max_chunk_size: int, chunk_overlap: int) -> list[str]:
    """Greedily pack leaf fragments with overlap and final normalization."""
    if not fragments:
        return []
    chunks: list[str] = []
    current = fragments[0]
    for frag in fragments[1:]:
        tentative = current + "\n" + frag
        if len(tentative) <= max_chunk_size:
            current = tentative
            continue
        chunks.append(current)
        if chunk_overlap > 0 and len(current) > chunk_overlap:
            tail = current[-chunk_overlap:].lstrip("\n")
            prefix = tail + ("\n" if tail and not tail.endswith("\n") else "")
            current = prefix + frag
            if len(current) > max_chunk_size:
                chunks.append(current[:max_chunk_size])
                current = current[max_chunk_size:]
        else:
            current = frag
    if current:
        chunks.append(current)
    normalized: list[str] = []
    for c in chunks:
        if len(c) <= max_chunk_size:
            normalized.append(c)
        else:
            normalized.extend(c[i : i + max_chunk_size] for i in range(0, len(c), max_chunk_size))
    return normalized


# --- Semantic chunking (preferred) ---
def _semantic_chunk_text(
    text: str,
    max_chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[str]:
    """Lightweight semantic-style chunking (paragraph + sentence aware)."""
    text = text.strip()
    if not text:
        return []
    if max_chunk_size <= 0:
        return [text]
    if chunk_overlap >= max_chunk_size:
        chunk_overlap = max_chunk_size // 5

    sent_pattern = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    sentences = [s.strip() for para in paragraphs for s in sent_pattern.split(para) if s.strip()]
    if not sentences:
        return []

    def slice_long(s: str) -> list[str]:
        return [s[i : i + max_chunk_size] for i in range(0, len(s), max_chunk_size)]

    chunks: list[str] = []
    current = ""
    for s in sentences:
        if len(s) > max_chunk_size:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(slice_long(s))
            continue
        if not current:
            current = s
            continue
        if len(current) + 1 + len(s) <= max_chunk_size:
            current += "\n" + s
            continue
        chunks.append(current)
        if chunk_overlap > 0 and len(current) > chunk_overlap:
            tail = current[-chunk_overlap:]
            candidate = tail + "\n" + s
            current = candidate if len(candidate) <= max_chunk_size else s
        else:
            current = s
    if current:
        chunks.append(current)
    return chunks


def _read_plain_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def _read_pdf(path: Path) -> str:
    reader = pypdf.PdfReader(str(path))
    texts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(texts)


def _read_docx(path: Path) -> str:
    document = docx.Document(str(path))
    return "\n".join(p.text for p in document.paragraphs)


def _read_html(path: Path) -> str:
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


class _EmbeddingProvider:
    """Simple embedding provider abstraction."""

    def __init__(self, model: str | None = None) -> None:
        self._use_ollama = None

        if not model:
            model = os.getenv("OLLAMA_EMBED_MODEL", "mxbai-embed-large")
            self._use_ollama = True
        self.model = model

        # Optional OpenAI fallback if API key is available
        self._openai_client = None
        if not self._use_ollama and os.getenv("OPENAI_API_KEY"):
            try:
                self._openai_client = OpenAI()
                # Default embedding model for OpenAI
                if self.model in (None, "mxbai-embed-large"):
                    self.model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
            except (ValueError, RuntimeError):
                self._openai_client = None

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Return embeddings for a list of texts.

        Prefers Ollama local embeddings; falls back to OpenAI if configured; otherwise raises.
        """
        if not texts:
            return []

        if self._use_ollama:
            # Ollama API accepts one prompt at a time; batch sequentially
            embeddings: list[list[float]] = []
            for t in texts:
                resp = ollama.embeddings(model=self.model, prompt=t)
                vec = resp.get("embedding")
                if not isinstance(vec, list):
                    msg = "Invalid embedding response from Ollama."
                    raise TypeError(msg)
                embeddings.append([float(v) for v in vec])
            return embeddings

        if self._openai_client is not None:
            # OpenAI new API: client.embeddings.create
            resp = self._openai_client.embeddings.create(model=str(self.model), input=texts)
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
        # Simple in-memory rolling progress log (mirrors APP_LOGGER messages) - no callbacks
        self._progress_log: deque[str] = deque(maxlen=1000)
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
    async def index_path(self, path: Path) -> int:
        """Asynchronously index a path without blocking the main event loop.

        Strategy:
        - Run file enumeration and each file's indexing in the default thread pool.
        - Yield control to the event loop between files so TUI remains responsive.
        - Save once at the end (in executor) to minimize contention.
        """
        loop = asyncio.get_running_loop()
        logger = APP_LOGGER
        start_msg = "KB indexing started: path=%s"

        logger.info(start_msg, path)
        self._progress_log.append(start_msg % (path,))
        # Enumerate files off-thread
        paths, scan_time = await loop.run_in_executor(
            None, self._gather_files_for_index, path, logger,
        )
        ctx = self._ProcessContext(
            root_path=path,
            enum_duration=scan_time,
            logger=logger,
        )
        total_local = len(paths)
        added_local = 0
        ingest_start_local = time.monotonic()
        for idx, file_path in enumerate(paths, start=1):
            start_file = time.monotonic()

            # Index each file in executor
            file_chunks_added = await loop.run_in_executor(None, self._index_single_file, file_path)
            added_local += file_chunks_added
            duration = time.monotonic() - start_file

            # Progress variables
            info_tpl = "KB file indexed: file=%s chunks=%d duration=%.2fs total_chunks_after=%d"
            debug_tpl = "KB progress: %d/%d files (%.1f%%) cumulative_chunks=%d"

            # Log progress
            pct = (idx / total_local) * 100 if total_local else 0.0
            logger.info(info_tpl, file_path, file_chunks_added, duration, self._next_id - 1)
            logger.debug(debug_tpl, idx, total_local, pct, self._next_id - 1)

            # Append the combined string as a single entry to the progress log
            self._progress_log.append(debug_tpl % (idx, total_local, pct, self._next_id - 1))
            self._progress_log.append(info_tpl % (file_path, file_chunks_added, duration, self._next_id - 1))

            # Let the event loop process UI events
            await asyncio.sleep(0)
        if added_local:
            await loop.run_in_executor(None, self._save)
        ingest_duration_local = time.monotonic() - ingest_start_local
        finish_tpl = (
            "KB async indexing finished: root=%s files_processed=%d chunks_added=%d "
            "scan_time=%.2fs ingest_time=%.2fs"
        )
        logger.info(
            finish_tpl,
            ctx.root_path,
            total_local,
            added_local,
            ctx.enum_duration,
            ingest_duration_local,
        )
        self._progress_log.append(
            finish_tpl % (ctx.root_path, total_local, added_local, ctx.enum_duration, ingest_duration_local),
        )
        if added_local == 0:
            warn_tpl = "KB async indexing produced no new chunks for path=%s"
            logger.warning(warn_tpl, ctx.root_path)
            self._progress_log.append(warn_tpl % (ctx.root_path,))
        return added_local

    # --------------- Progress Access ---------------
    def recent_progress(self, limit: int = 100) -> list[str]:
        """Return up to the latest 'limit' progress log lines."""
        if limit <= 0:
            return []
        return list(self._progress_log)[-limit:]

    # --- helpers extracted to reduce complexity of public API method ---
    def _gather_files_for_index(self, root_path: Path, logger: logging.Logger) -> tuple[list[Path], float]:  # noqa: C901
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
    class _ProcessContext:
        root_path: Path
        enum_duration: float
        logger: logging.Logger

    def _process_files_for_index(self, paths: list[Path], ctx: _ProcessContext) -> int:
        total_local = len(paths)
        added_local = 0
        ingest_start_local = time.monotonic()
        for idx, file_path in enumerate(paths, start=1):
            file_start = time.monotonic()
            file_chunks_added = self._index_single_file(file_path)
            added_local += file_chunks_added
            file_duration = time.monotonic() - file_start
            ctx.logger.info(
                "KB file indexed: file=%s chunks=%d duration=%.2fs total_chunks_after=%d",
                file_path,
                file_chunks_added,
                file_duration,
                self._next_id - 1,
            )
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
    ) -> int:
        """Index a single supported file; returns number of chunks added.

        Skips unreadable or empty files and logs at INFO/WARN levels. Any embedding
        errors for a single file are contained and won't stop the folder ingestion.
        """
        try:
            text = _read_text_file(p)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            APP_LOGGER.warning("Skipping unreadable file %s: %s", p, exc)
            return 0

        if not text or not text.strip():
            APP_LOGGER.info("Skipping empty file: %s", p)
            return 0
        # Semantic chunking (preferred over recursive / fixed-size)
        try:
            max_chunk_size = int(os.getenv("KB_CHUNK_SIZE", "1000"))
        except ValueError:
            max_chunk_size = 1000
        try:
            chunk_overlap = int(os.getenv("KB_CHUNK_OVERLAP", "200"))
        except ValueError:
            chunk_overlap = 200

        chunks = _semantic_chunk_text(text, max_chunk_size=max_chunk_size, chunk_overlap=chunk_overlap)
        if not chunks:
            APP_LOGGER.info("No chunks produced for file: %s", p)
            return 0

        try:
            embeddings = self._embedder.embed_texts(chunks)
        except Exception as exc:  # noqa: BLE001
            APP_LOGGER.warning("Embedding failed for %s: %s", p, exc)
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

    # --------------- Stats ---------------
    def record_count(self) -> int:
        """Return the total number of indexed chunks in the knowledge base."""
        return len(self._records)

    def is_empty(self) -> bool:
        """Return True if the knowledge base has no indexed content."""
        return len(self._records) == 0

# Global singleton to share across UI and actions
GLOBAL_KB = KnowledgeBase()

