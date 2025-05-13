from capabilities.memory import Memory, MemoryManager
from core.chat import ChatHistory, ChatMessage


class CustomMemory(MemoryManager):
    """Memory for LLM-based agents."""

    def load_memories_relevant_to_query(self, query: str) -> list[Memory]:
        """Load memories relevant to the query."""

        # TODO: implement this
        raise NotImplementedError("This method should be implemented by subclasses.")

    def is_suitable_for_long_term(self, memory: Memory) -> bool:
        """Decide if memory is suited for long term or short term storage.
        Returns True if memory is suited for long term storage, False for short term.
        """

        # TODO: implement this

        # NOTE: Idk how to do this maybe you can use the content and pass to LLM
        # or just flip a coin for now
        raise NotImplementedError("This method should be implemented by subclasses.")

    def store_memory_long_term(self, memory: Memory) -> None:
        """Store memory long term."""
        # TODO: implement this

        raise NotImplementedError("This method should be implemented by subclasses.")

    def store_memory_short_term(self, memory: Memory) -> None:
        """Store memory short term."""
        # TODO: implement this

        raise NotImplementedError("This method should be implemented by subclasses.")

    def load_all_long_term_memories(self) -> list[Memory]:
        """Load all long term memories."""
        # TODO: implement this

        raise NotImplementedError("This method should be implemented by subclasses.")

    def load_all_short_term_memories(self) -> list[Memory]:
        """Load all short term memories."""
        # TODO: implement this

        raise NotImplementedError("This method should be implemented by subclasses.")

    def clear_short_term_memory(self) -> None:
        """Clear short term memory."""
        # TODO: implement this

        raise NotImplementedError("This method should be implemented by subclasses.")

    def update_memory_from_chat_history(self, chat_history: ChatHistory) -> None:
        """Update memory from chat history."""
        # TODO: implement this

        raise NotImplementedError("This method should be implemented by subclasses.")

    def update_memory_from_last_message(self, last_message: ChatMessage) -> None:
        """Update memory from the last message. Decides if it is suited for long term or short term storage."""

        # NOTE: It should decide which memory to use based on the content of the last message.
        # TODO: implement this

        raise NotImplementedError("This method should be implemented by subclasses.")
