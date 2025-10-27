"""Test suite for environment and configurations."""

from functools import lru_cache

import pytest

from llm_mas.model_providers.api import ModelsAPI
from llm_mas.utils.config.models_config import ModelType


class TestConfig:
    """Test suite for environment and configurations."""

    @lru_cache  # noqa: B019
    async def _ensure_llm_available(self) -> None:
        try:
            await ModelsAPI.call_llm("RESPOND WITH THE LETTER A AND NOTHING ELSE.")
        except ConnectionError:
            pytest.skip("LLM model is not available. Skipping test.")

    @lru_cache  # noqa: B019
    async def _ensure_embedding_available(self) -> None:
        try:
            await ModelsAPI.get_embedding("Test embedding.")
        except ConnectionError:
            pytest.skip("Embedding model is not available. Skipping test.")

    @lru_cache  # noqa: B019
    async def _ensure_ollama_available(self) -> None:
        try:
            await ModelsAPI.call_llm("RESPOND WITH THE LETTER A AND NOTHING ELSE.", ModelType.LOCAL)
        except ConnectionError:
            pytest.skip("Ollama model is not available. Skipping test.")

    # LLM model tests
    # ==================

    # try LLM model that doesn't exist
    @pytest.mark.asyncio
    async def test_invalid_llm_model(self) -> None:
        """Test handling of invalid LLM model configuration."""
        await self._ensure_llm_available()

        try:
            await ModelsAPI.call_llm("RESPOND WITH THE LETTER A AND NOTHING ELSE.", "invalid-model-name")
        except ValueError as e:
            assert "Model configuration for 'invalid-model-name' not found." in str(e)  # noqa: PT017

    # try local LLM model that isn't installed
    @pytest.mark.asyncio
    async def test_local_llm_model_not_installed(self) -> None:
        """Test handling of local LLM model that isn't installed."""
        await self._ensure_ollama_available()

        # NOTE: Assumes that the user did not install "command-r7b-arabic:latest"
        # not sure how to test for this because this is what the test itself is trying to do

        try:
            await ModelsAPI.call_llm(
                "RESPOND WITH THE LETTER A AND NOTHING ELSE.",
                "command-r7b-arabic:latest",
            )
        except ConnectionError as e:
            assert "Failed to connect to Ollama server" in str(e)  # noqa: PT017

    # try invalid model type (enum)
    @pytest.mark.asyncio
    async def test_invalid_llm_model_type_enum(self) -> None:
        """Test handling of invalid LLM model type (enum)."""
        await self._ensure_llm_available()

        try:
            await ModelsAPI.call_llm("RESPOND WITH THE LETTER A AND NOTHING ELSE.", ModelType(999))
        except ValueError as e:
            assert "Model configuration for '999' not found." in str(e)  # noqa: PT017
