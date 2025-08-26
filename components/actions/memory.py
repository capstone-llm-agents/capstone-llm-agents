from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from mem0 import Memory as Mem



class MemorySavelong(Action):
    """An action that let's the agent save its long term memory."""

    def __init__(self) -> None:
        """Initialize the RespondWithChatHistory action."""
        super().__init__(description="Access memory")
        self.config = {
                        "vector_store":{
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
        memory_to_save_user = f'User said {last_message['content']}'
        secondlast_message = messages[-2]
        memory_to_save_agent = f'Agent said {secondlast_message['content']}'
        m.add(messages=memory_to_save_user, agent_id = 'Travel', metadata={'Speaker': 'User'})
        m.add(messages=memory_to_save_agent, agent_id='Travel', metadata={'speaker': 'Agent'})
        response = 'Memory Saved'
        res = ActionResult()
        res.set_param("response", response)
        return res


class MemorySearchlong(Action):
    """An action that lets the agent search its long term memory"""

    def __init__(self) -> None:
        """Initialize the RespondWithChatHistory action."""
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
        relevant_memories = m.search(query=last_message['content'], agent_id = 'Travel', limit = 10)
        memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
        res = ActionResult()
        if memories_str:
            response = f" These are the relating memories {memories_str}"
            res.set_param("response", response)
        else:
            response = "No memories found"
            res.set_param("response", response)
        return res

class MemorySaveShort(Action):
    """An action that lets the save a short term memory"""
    def __init__(self) -> None:
        super().__init__(description="Save short term/chat memory")
        self.config = {}
    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        m = chromaDb

class MemorySearchShort(Action):
    """An action that lets the agent search through its short term memory"""
    def __init__(self) -> None:
        super().__init__(description="Search through short term/chat memory")

    @override
    async  def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        m = chromaDb