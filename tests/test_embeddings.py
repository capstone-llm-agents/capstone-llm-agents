"""Test suite for embedding functions."""

import pytest

from llm_mas.model_providers.api import ModelsAPI


class TestEmbeddings:
    """Test suite for embedding functions."""

    async def _ensure_llm_available(self) -> None:
        try:
            await ModelsAPI.get_embedding("Test embedding.")
        except ConnectionError:
            pytest.skip("Embedding model is not available. Skipping test.")

    @pytest.mark.asyncio
    async def test_embedding_returns_vector(self) -> None:
        """Test that embedding function returns a vector of floats."""
        await self._ensure_llm_available()

        embedding = await ModelsAPI.get_embedding("test")
        assert isinstance(embedding, list), "Embedding should be a list."
        assert all(isinstance(value, float) for value in embedding), "All elements in embedding should be floats."
        assert len(embedding) > 0, "Embedding should not be empty."
