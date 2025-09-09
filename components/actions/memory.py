from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from mem0 import Memory as Mem
from datetime import datetime


class MemorySaveLong(Action):
    """An action that let's the agent save its long term memory."""

    def __init__(self) -> None:
        """Initialize the memory save action."""
        super().__init__(description="Access memory")
        self.config = config = {
                "vector_store": {
                    "provider": "chroma",
                    "config": {
                        "collection_name": "test",
                        "path": "db",
                    }
                }
            }
        {
        """
        Qdrant config
            config = {
                        "vector_store":{
                            "provider": "qdrant",
                            "config": {
                                "host": "localhost",
                                "port": 6333,
                            }
                        }
                    }
        """
        }
    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        m = Mem.from_config(self.config)
        chat_history = context.conversation.get_chat_history()
        messages = chat_history.as_dicts()
        last_message = messages[-1]
        memory_to_save_user = f'User said {last_message['content']}'
        second_last_message = messages[-2]
        memory_to_save_agent = f'Agent said {second_last_message['content']}'
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d %H:%M:%S")
        m.add(messages=memory_to_save_user, agent_id = context.agent.name, metadata={'Speaker': 'User', 'timestamp': date_string})
        m.add(messages=memory_to_save_agent, agent_id= context.agent.name, metadata={'speaker': 'Agent', 'timestamp': date_string})
        response = 'Memory Saved'
        res = ActionResult()
        res.set_param("response", response)
        return res


class MemorySearchLong(Action):
    """An action that lets the agent search its long term memory"""

    def __init__(self) -> None:
        """Initialize the memory search action."""
        super().__init__(description="Access memory")
        self.config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "host": "localhost",
                    "port": 6333,
                }
            }
        }

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:

        m = Mem.from_config(self.config)
        chat_history = context.conversation.get_chat_history()

        messages = chat_history.as_dicts()

        last_message = messages[-1]
        relevant_memories = m.search(query=last_message['content'], agent_id = context.agent.name, limit = 10)
        memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
        res = ActionResult()
        if memories_str:
            response = f" These are the relating memories {memories_str}"
            res.set_param("response", response)
        else:
            response = "No memories found"
            res.set_param("response", response)
        return res

