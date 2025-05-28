from capabilities.memory import MemoryManager, Memory
from sentence_transformers import SentenceTransformer
from core.chat import ChatHistory, ChatMessage
import os
from mem0 import MemoryClient

class Memory(MemoryManager):
    def __init__(self):
        super().__init__()
        self.client=MemoryClient(os.getenv("MEM0_API_KEY"))
        self.app_id="agent-memory"


    def load_memories_relevant_to_query(self, query: str, user_id="assistant") -> list[Memory]:
        return self.client.search(query, user_id=user_id, version="v2") # limit parameter for top_k 
        
    def update_memory_from_chat_history(self, chat_history: ChatHistory, user_id="assistant") -> None:
        messages = chat_history.get_last_n_messages(2)
        message = messages[0]
        message = message.content
        self.client.add(message, user_id=user_id)
        if len(messages) == 0:
            return
        message = messages[1]
        message = message.content
        self.client.add(message, user_id=user_id)

    def load_all_long_term_memories(self, user_id="assistant") -> list[Memory]:
        return self.client.get_all(user_id=user_id)
