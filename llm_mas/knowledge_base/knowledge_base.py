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

import json
import logging
import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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


class _EmbeddingProvider:
    """Simple embedding provider abstraction."""

    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        self._use_ollama = OLLAMA_AVAILABLE

        # Optional OpenAI fallback if API key is available
        self._openai_client = None
        if not self._use_ollama and OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY") and OpenAI is not None:
            try:
                self._openai_client = OpenAI()
                # Default embedding model for OpenAI
                if self.model in (None, "nomic-embed-text"):
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
        self._load()

    # --------------- Persistence ---------------
    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self._records = [_KBRecord.from_json(d) for d in data.get("records", [])]
            self._next_id = int(data.get("next_id", len(self._records) + 1))
        except (OSError, json.JSONDecodeError):
            # Corrupt or incompatible index; start fresh
            logging.getLogger(__name__).warning("KB index file is corrupt or unreadable. Starting with a fresh index.")
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
        rec = _KBRecord(id=self._next_id, source_path=source_path, chunk_id=chunk_id, text=text, embedding=vec)
        self._records.append(rec)
        self._next_id += 1
        return rec

    def index_path(self, path: Path) -> int:
        """Index a file or directory.

        Returns the number of chunks added.
        """
        paths: list[Path] = []
        if path.is_dir():
            paths.extend([p for p in path.rglob("*") if _is_supported_file(p)])
        elif _is_supported_file(path):
            paths.append(path)

        added = 0
        for p in paths:
            try:
                text = _read_text_file(p)
            except (OSError, UnicodeDecodeError, ValueError) as exc:
                logging.getLogger(__name__).warning("Skipping unreadable file %s: %s", p, exc)
                continue
            chunks = _chunk_text(text)
            embeddings = self._embedder.embed_texts(chunks)
            for i, (chunk, vec) in enumerate(zip(chunks, embeddings, strict=True)):
                rec = _KBRecord(id=self._next_id, source_path=str(p), chunk_id=i, text=chunk, embedding=vec)
                self._records.append(rec)
                self._next_id += 1
                added += 1
        if added:
            self._save()
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

