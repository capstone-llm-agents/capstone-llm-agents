import random

from capabilities.memory import Memory, MemoryManager
from core.chat import ChatHistory, ChatMessage


class MemoryManagerSpoof(MemoryManager):
    """A spoof for the MemoryManager capability."""

    long_term_memories: list[Memory]
    short_term_memories: list[Memory]

    def __init__(self):
        super().__init__()
        self.long_term_memories = []
        self.short_term_memories = []

    def load_memories_relevant_to_query(self, query: str) -> list[Memory]:
        """Load memories relevant to the query."""
        # for now assume that first 3 memories are relevant
        return self.long_term_memories[:3] + self.short_term_memories[:3]

    def is_suitable_for_long_term(self, memory: Memory) -> bool:
        """Decide if memory is suited for long term or short term storage.
        Returns True if memory is suited for long term storage, False for short term.
        """
        # coin flip if suitable for long term or short term
        chance = 0.5
        return random.random() < chance

    def store_memory_long_term(self, memory: Memory) -> None:
        """Store memory long term."""
        self.long_term_memories.append(memory)

    def store_memory_short_term(self, memory: Memory) -> None:
        """Store memory short term."""
        self.short_term_memories.append(memory)

    def load_all_long_term_memories(self) -> list[Memory]:
        """Load all long term memories."""
        return self.long_term_memories

    def load_all_short_term_memories(self) -> list[Memory]:
        """Load all short term memories."""
        return self.short_term_memories

    def clear_short_term_memory(self) -> None:
        """Clear short term memory."""
        self.short_term_memories = []

    def update_memory_from_chat_history(self, chat_history: ChatHistory) -> None:
        """Update memory from chat history."""

        # get last two messages if possible
        messages = chat_history.get_last_n_messages(2)

        if len(messages) == 0:
            return

        for message in messages:
            self.update_memory_from_last_message(message)

    def update_memory_from_last_message(self, last_message: ChatMessage) -> None:
        """Update memory from the last message. Decides if it is suited for long term or short term storage."""
        # decide if it is suited for long term or short term storage
        memory = Memory(last_message.content)

        if self.is_suitable_for_long_term(memory):
            self.store_memory_long_term(memory)
        else:
            self.store_memory_short_term(memory)
