from datetime import datetime
from typing import override
from mem0 import AsyncMemory
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.utils.memory_config import InternalMemoryConfig as MemoryConfig
import sys




#tried moving both helper functions back and it broke
async def Save(context: ActionContext, config):
    """helper function from previous threading tried to move it back since its async, and it broke
    Save the memory to the memory store."""
    try:
        APP_LOGGER.info(f"Before saving memory")
        memory = AsyncMemory(config=config)
        chat_history = context.conversation.get_chat_history()
        messages = chat_history.as_dicts()
        last_message = messages[-1]
        memory_to_save_user = f"User said {last_message['content']}"

        action_res_tuple = context.agent.workspace.action_history.get_history_at_index(-2)

        if action_res_tuple is None:
            memory_to_save_agent = f""
        else:
            _, result, _ = action_res_tuple
            memory_to_save_agent = result.get_param("response")

        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d %H:%M:%S")
        APP_LOGGER.info(f"Just before Adding:\n")
        await memory.add(
            messages=memory_to_save_user,
            agent_id=context.agent.name,
            metadata={"Speaker": "User", "timestamp": date_string},
        )

        await memory.add(
            messages=memory_to_save_agent,
            agent_id=context.agent.name,
            metadata={"speaker": "Agent", "timestamp": date_string},
        )
        APP_LOGGER.info(f"Memory Saved\n")
        return
    except Exception as e:
        APP_LOGGER.error(f"Exception occured  in stop{e}")
        return


async def Search(context: ActionContext, config):
    """helper function from previous threading tried to move it back since its async, and it broke
        Save the memory to the memory store."""
    APP_LOGGER.info("Searching memory")
    if sys.platform == "win32":
        memories_str = "No memories found"
        return memories_str
    else:
        memory = AsyncMemory(config=config)
        chat_history = context.conversation.get_chat_history()

        messages = chat_history.as_dicts()

        last_message = messages[-1]

        relevant_memories = await memory.search(query=last_message["content"], agent_id=context.agent.name, limit=10)
        # relevant_memories = m.search(query=last_message["content"], limit=10)
        memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
        return memories_str


class MemorySaveLong(Action):
    """An action that let's the agent save its long term memory."""

    def __init__(self) -> None:
        """Initialize the memory save action."""
        super().__init__(description="Access memory")
        config = MemoryConfig()
        self.config = config.load_provider_conf()


    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        APP_LOGGER.info(f"Saving memory and config {self.config}")
        await Save(context, self.config)

        res = ActionResult()
        res.set_param("response", "memories saved")
        return res


class MemorySearchLong(Action):
    """An action that lets the agent search its long term memory"""

    def __init__(self) -> None:
        """Initialize the memory search action."""
        super().__init__(description="Access memory")
        config = MemoryConfig()
        self.config = config.load_provider_conf()


    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        memories_str = await Search(context, self.config)
        res = ActionResult()
        if memories_str:
            response = f" These are the relating memories {memories_str}"
            res.set_param("response", response)
        else:
            response = "No memories found"
            res.set_param("response", response)
        return res

