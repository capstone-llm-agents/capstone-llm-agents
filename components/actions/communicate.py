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

        # create conversation
        conversation = context.conversation_manager.start_conversation(
            f"CommunicateWith{friend_name}-{generate_random_id()}",
        )

        context_str = self.get_context_from_last_result(context)

        chat_history = context.conversation.get_chat_history()

        messages = chat_history.as_dicts()

        last_message = messages[-1]

        # friend makes a new workspace
        friend.workspace.reset()

        # create new comm state
        comm_state = CommunicationState(context.agent, friend)

        task = Task(description="Help the other agent with their request.", action_context=context)

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
