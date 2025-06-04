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
      
    def update_memory_from_chat_history(self, chat_history: ChatHistory) -> None:
      
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def load_all_long_term_memories(self) -> list[Memory]:
    
        raise NotImplementedError("This method should be implemented by subclasses.")
