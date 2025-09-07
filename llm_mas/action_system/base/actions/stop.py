"""The stop module defines a StopAction class that stops the agent's execution."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from mem0 import Memory as Mem
from datetime import datetime
class StopAction(Action):
    """An action that stops the agent's execution."""

    def __init__(self) -> None:
        """Initialize the StopAction."""
        super().__init__(description="Stops the agent's execution")

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by stopping the agent."""
        config = {
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "test",
                    "path": "db",
                }
            }
        }
        m = Mem.from_config(config)
        chat_history = context.conversation.get_chat_history()
        messages = chat_history.as_dicts()
        last_message = messages[-1]
        memory_to_save_user = f'User said {last_message['content']}'
        second_last_message = messages[-2]
        memory_to_save_agent = f'Agent said {second_last_message['content']}'
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d %H:%M:%S")
        m.add(messages=memory_to_save_user, agent_id=context.agent.name,
              metadata={'Speaker': 'User', 'timestamp': date_string})
        m.add(messages=memory_to_save_agent, agent_id=context.agent.name,
              metadata={'speaker': 'Agent', 'timestamp': date_string})
        return ActionResult()
