"""The agent view is a concise representation for the agent."""

from llm_mas.fragment.view import FragmentView


class AgentView(FragmentView):
    """The agent view is a concise representation for the agent."""

    MAX_TEXT_CHUNK_LENGTH = 1000
    MAX_TEXT_CHUNKS = 5

    def __init__(self) -> None:
        """Initialize an agent view."""
        self.text_chunks: list[str] = []

    def add_text_chunk(self, chunk: str) -> None:
        """Add a text chunk to the agent view."""
        if len(self.text_chunks) < self.MAX_TEXT_CHUNKS:
            if len(chunk) > self.MAX_TEXT_CHUNK_LENGTH:
                chunk = chunk[: self.MAX_TEXT_CHUNK_LENGTH] + "..."
            self.text_chunks.append(chunk)
