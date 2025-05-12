from core.capability import Capability
from core.chat import ChatHistory, ChatMessage


class Memory:
    """A piece of memory for LLM-based agents."""

    def __init__(self, content: str):
        self.content = content


class MemoryManager(Capability):
    """Memory for LLM-based agents."""

    def __init__(self):
        super().__init__("memory")

    def load_memories_relevant_to_query(self, query: str) -> list[Memory]:
        """Load memories relevant to the query."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def is_suitable_for_long_term(self, memory: Memory) -> bool:
        """Decide if memory is suited for long term or short term storage.
        Returns True if memory is suited for long term storage, False for short term.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    def store_memory_long_term(self, memory: Memory) -> None:
        """Store memory long term."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def store_memory_short_term(self, memory: Memory) -> None:
        """Store memory short term."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def load_all_long_term_memories(self) -> list[Memory]:
        """Load all long term memories."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def load_all_short_term_memories(self) -> list[Memory]:
        """Load all short term memories."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def clear_short_term_memory(self) -> None:
        """Clear short term memory."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def update_memory_from_chat_history(self, chat_history: ChatHistory) -> None:
        """Update memory from chat history."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def update_memory_from_last_message(self, last_message: ChatMessage) -> None:
        """Update memory from the last message. Decides if it is suited for long term or short term storage."""

        # NOTE: It should decide which memory to use based on the content of the last message.

        raise NotImplementedError("This method should be implemented by subclasses.")
