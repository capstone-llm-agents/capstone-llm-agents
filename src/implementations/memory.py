from capabilities.memory import MemoryManager, Memory
from core.chat import ChatHistory
import os
from mem0 import MemoryClient


class Memory(MemoryManager):
    def __init__(self):
        super().__init__()
        self.client = MemoryClient(os.getenv("MEM0_API_KEY"))
        self.app_id = "agent-memory"

    def load_memories_relevant_to_query(
        self, query: str, user_id="assistant"
    ) -> list[Memory]:
        print("Using mem0 to load memories relevant to query:", query)

        return self.client.search(
            query, user_id=user_id, version="v2"
        )  # limit parameter for top_k

    def update_memory_from_chat_history(
        self, chat_history: ChatHistory, user_id="assistant"
    ) -> None:
        messages = chat_history.get_last_n_messages(2)

        # TODO figure out how to handle if agent talks to agent
        # like should it remember the other agent's messages? i mean ig so
        # filter for user messages
        messages = [msg for msg in messages if msg.who.role == "user"]

        if len(messages) == 0:
            return

        message = messages[0]
        message = message.content
        self.client.add(message, user_id=user_id)

        if len(messages) == 1:
            return

        message = messages[1]
        message = message.content
        self.client.add(message, user_id=user_id)

    def load_all_long_term_memories(self, user_id="assistant") -> list[Memory]:
        return self.client.get_all(user_id=user_id)
