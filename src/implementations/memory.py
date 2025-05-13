from capabilities.memory import MemoryManager, Memory
from sentence_transformers import SentenceTransformer
from core.chat import ChatHistory, ChatMessage

import numpy as np
import chromadb as DB

class Memory(MemoryManager):
    def __init__(self, embedding_model_name: str = 'all-MiniLM-L6-v2'):
        super().__init__()
        self.model = SentenceTransformer(embedding_model_name)
        self.client = DB.PersistentClient(path='Assistant')
        self.agent = 'Assistant'
        self.memory = self.client.get_or_create_collection(name=self.agent)

    def load_memories_relevant_to_query(self, query: str, top_k: int = 3) -> list[Memory]:
        
        query_embedding = self.model.encode(query)
        results = self.memory.query(
           query_embeddings=[query_embedding],
           n_results=top_k,
           include=['documents', 'metadatas', 'distances']
        )
        print(results)
        return results['documents']
        

    def is_suitable_for_long_term(self, memory: Memory) -> bool:
        """Decide if memory is suited for long term or short term storage.
        Returns True if memory is suited for long term storage, False for short term.
        """
        raise True

    def store_memory_long_term(self, memory: Memory) -> None:
       
        print(text)
        embedding = self.model.encode(text)
        memory = self.client.get_collection(name=self.agent)
        memory.add(
           embeddings=[embedding],
           documents=[text],
           ids=[str(self.get_id())],
           metadatas=[metadata]
       )
        
    def get_id(self):
       return len(self.memory.get()['ids']) + 1

    def update_memory_from_chat_history(self, chat_history: ChatHistory, metadata: dict = {'time':'00:00'}) -> None:
        memory = self.client.get_collection(name=self.agent)
        messages = chat_history.get_last_n_messages(2)
        message = messages[0]
        message = message.content
       
        if len(messages) == 0:
            return
        embedding = self.model.encode(message)
        memory.add(
            embeddings=[embedding],
            documents=[message],
            ids=[str(self.get_id())],
            metadatas=[metadata]
        )
        message = messages[1]
        message = message.content
        embedding = self.model.encode(message)
        memory.add(
            embeddings=[embedding],
            documents=[message],
            ids=[str(self.get_id())],
            metadatas=[metadata]
        )

    def update_memory_from_last_message(self, last_message: ChatMessage) -> None:
        print('This is text')
        print(text)
        embedding = self.model.encode(text)
        memory = self.client.get_collection(name=self.agent)
        memory.add(
            embeddings=[embedding],
            documents=[text],
            ids=[str(self.get_id())],
            metadatas=[metadata]
        )
        # NOTE: It should decide which memory to use based on the content of the last message.

 

"""
    def store_memory_short_term(self, memory: Memory) -> None:
     
        raise NotImplementedError("This method should be implemented by subclasses.")

    def load_all_long_term_memories(self) -> list[Memory]:
     
        raise NotImplementedError("This method should be implemented by subclasses.")

    def load_all_short_term_memories(self) -> list[Memory]:
       
        raise NotImplementedError("This method should be implemented by subclasses.")

    def clear_short_term_memory(self) -> None:
       
        raise NotImplementedError("This method should be implemented by subclasses.")
"""