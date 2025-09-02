"""Utility functions for vector embeddings and selection."""

import logging
from enum import Enum, auto
from typing import TypeVar

import numpy as np

T = TypeVar("T")


class SelectionStrategy(Enum):
    """Selection strategies for vector-based selection."""

    ARGMAX = auto()
    """Select the item with the highest score."""
    RANDOM = auto()
    """Select an item randomly from the filtered items (top-k and/or top-p)."""


class VectorSelector:
    """Generic class for selecting items based on vector similarity."""

    def __init__(
        self,
        *,
        top_k: int | None = None,
        top_p: float | None = None,
        selection_strategy: SelectionStrategy = SelectionStrategy.ARGMAX,
    ) -> None:
        """Initialize the VectorSelector."""
        self.top_k = top_k
        self.top_p = top_p
        self.selection_strategy = selection_strategy

        if self.top_k is not None and self.top_p is not None:
            logging.getLogger("textual_app").warning(
                "Both top_k and top_p are set. This can lead to unexpected behavior.",
            )

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def _convert(self, vector: np.ndarray | list[float]) -> np.ndarray:
        if isinstance(vector, list):
            return np.array(vector)
        return vector

    def select(
        self,
        query_vector: np.ndarray | list[float],
        items_with_vectors: list[tuple[T, np.ndarray]] | list[tuple[T, list[float]]],
    ) -> tuple[T, float]:
        """Select an item given a query vector and a list of (item, vector) pairs."""
        # convert lists to np arrays
        query_vector = self._convert(query_vector)
        vector_items = [(item, self._convert(vec)) for item, vec in items_with_vectors]

        # compute similarities
        similarities = [(item, self._cosine_similarity(query_vector, vec)) for item, vec in vector_items]

        # TODO: move this out of here  # noqa: TD003
        logger = logging.getLogger("textual_app")
        logger.info("Vector similarities:")
        for item, sim in similarities:
            logger.info("Item: %s, Similarity: %.4f", getattr(item, "name", str(item)), sim)

        similarities.sort(key=lambda x: x[1], reverse=True)

        # apply top-k filtering
        if self.top_k is not None and self.top_k < len(similarities):
            similarities = similarities[: self.top_k]

        # apply top-p filtering
        if self.top_p is not None and 0.0 < self.top_p < 1.0:
            total_score = sum(sim for _, sim in similarities)
            cumulative, filtered = 0.0, []
            for item, sim in similarities:
                cumulative += sim / total_score if total_score > 0 else 0
                filtered.append((item, sim))
                if cumulative >= self.top_p:
                    break
            similarities = filtered

        if self.selection_strategy == SelectionStrategy.ARGMAX:
            return similarities[0]
        if self.selection_strategy == SelectionStrategy.RANDOM:
            return similarities[np.random.randint(len(similarities))]  # noqa: NPY002

        msg = f"Unknown selection strategy: {self.selection_strategy}"
        raise ValueError(msg)
