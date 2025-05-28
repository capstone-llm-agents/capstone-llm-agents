from capabilities.memory import MemoryManager, Memory
from sentence_transformers import SentenceTransformer
from core.chat import ChatHistory, ChatMessage
import os
from mem0 import MemoryClient

os.environ['OPENAI_API_KEY'] = "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"
MEM0_API_KEY = "m0-xX74vpX3bEKH0BfJZjBVffA7AWXU7D7EaL00rjOf"


class Memory(MemoryManager):
    def __init__(self):
        super().__init__()
        self.client=MemoryClient(MEM0_API_KEY)
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
