"""An action to list available friends in the agent system."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.communication.interface import CommunicationState
from llm_mas.communication.messages import EndMessage, ProposalMessage
from llm_mas.communication.task.agent_task import Task
from llm_mas.mas.agent import Agent
from llm_mas.model_providers.api import ModelsAPI
from llm_mas.utils.config.models_config import ModelType
from llm_mas.utils.embeddings import EmbeddingFunction, VectorSelector
from llm_mas.utils.random_id import generate_random_id


class Communicate(Action):
    """An action that asks a friend for help."""

    def __init__(
        self,
        embedding_model: EmbeddingFunction,
        vector_selector: VectorSelector | None = None,
    ) -> None:
        """Initialize the AskFriendForHelp action."""
        super().__init__(description="Asks a friend for help")
        self.embedding_model = embedding_model
        self.vector_selector = vector_selector or VectorSelector()

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by asking a friend for help."""
        entity = context.agent
        friends = entity.friends

        if not friends:
            res = ActionResult()
            res.set_param("response", "No friends available to ask for help.")
            return res

        last_message = context.conversation.chat_history.messages[-1].content

        agent_friends = [friend for friend in friends if isinstance(friend, Agent)]

        if not agent_friends:
            res = ActionResult()
            res.set_param("response", "No agent friends available to ask for help.")
            return res

        friend = self.vector_selector.select(
            query_vector=await self.embedding_model(last_message, ModelType.EMBEDDING),
            items_with_vectors=[
                (friend, await self.embedding_model(friend.get_description(), ModelType.EMBEDDING))
                for friend in agent_friends
            ],
        )[0]

        if not friend:
            msg = "No friends available to ask for help."
            raise ValueError(msg)

        friend_name = friend.get_name()

        context_str = self.get_context_from_last_result(context)

        chat_history = context.conversation.get_chat_history()

        messages = chat_history.as_dicts()

        last_message = messages[-1]

        # friend makes a new workspace
        friend.workspace.reset()

        # create new comm state
        comm_state = CommunicationState(context.agent, friend)

        task_description = await self.get_task_description(context_str, last_message["content"])

        task = Task(description=task_description, action_context=context)

        # create conversation
        conversation_name = self.convert_description_to_conversation_name(task_description)
        conversation = context.conversation_manager.start_conversation(
            f"{conversation_name}-{generate_random_id()}",
        )

        comm_state.current_task = task

        # start with a proposal to the friend
        proposal = ProposalMessage(
            sender=context.agent,
            task=task,
            content=f"Hi {friend_name}, can you help me with this?\n\n"
            f"Here is some context to help you understand the situation:\n{context_str}\n\n"
            f"Here is the last message I received that I need help with:\n{last_message['content']}\n\n"
            f"Please assist me in any way you can. Thank you!",
        )

        message = proposal

        max_messages = 20
        count = 0

        sender = context.agent
        recipient = friend

        while not isinstance(message, EndMessage) and count < max_messages:
            count += 1
            conversation.add_message(message.sender, message.content)

            # set context agent to the recipient
            context.agent = recipient

            message = await context.agent.communication_interface.handle_message(message, comm_state)

            if message is None:
                break

            # finished message, swap sender and recipient
            sender, recipient = recipient, sender

            # swap communication state
            comm_state.swap()

        conversation.add_message(message.sender, message.content)

        # get the message before the last one (the last one is the StopAction)
        action_history_tuple = friend.workspace.action_history.get_history_at_index(-2)

        if action_history_tuple is None:
            msg = "No action history found for the friend agent."
            raise ValueError(msg)

        action, action_result, action_context = action_history_tuple

        return action_result

    async def get_task_description(self, context_str: str, last_message: str) -> str:
        """Generate a task description based on the context and last message."""
        # use LLM to generate a task description
        prompt = f"""
        You are an AI assistant that helps generate task descriptions for agents based on context and messages.
        Given the following context and last message, generate a concise task description based on the information provided.
        ONLY RESPOND WITH THE TASK DESCRIPTION. DO NOT RESPOND WITH ANYTHING ELSE. NO PREAMBLE OR EXPLANATION. KEEP IT VERY SHORT. AS SHORT AS POSSIBLE.
        Context: {context_str}
        Last Message: {last_message}
        Task Description:
        """
        return await ModelsAPI.call_llm(prompt)

    def convert_description_to_conversation_name(self, description: str) -> str:
        """Convert a task description to a valid conversation name."""
        # identifiers must contain only letters, numbers, underscores, or hyphens, and must not begin with a number.
        max_length = 50
        valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_- "
        conversation_name = "".join(c for c in description if c in valid_chars)
        conversation_name = conversation_name.replace(" ", "_")
        if len(conversation_name) > max_length:
            conversation_name = conversation_name[:max_length]
        if conversation_name and conversation_name[0].isdigit():
            conversation_name = "_" + conversation_name
        if not conversation_name:
            conversation_name = "conversation"
        return conversation_name
