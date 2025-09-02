"""An action to list available friends in the agent system."""

from collections.abc import Awaitable, Callable
from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.mas.agent import Agent
from llm_mas.utils.embeddings import VectorSelector
from llm_mas.utils.random_id import generate_random_id


class ListFriends(Action):
    """An action that retrieves the list of available friends."""

    def __init__(
        self,
    ) -> None:
        """Initialize the ListFriends action."""
        super().__init__(description="Retrieves the list of available friends")

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action by retrieving the list of friends."""
        entity = context.agent
        friends = entity.friends

        friend_names = [friend.get_name() for friend in friends]

        res = ActionResult()
        res.set_param("friends", friend_names)
        return res


# ask friend for help
class AskFriendForHelp(Action):
    """An action that asks a friend for help."""

    def __init__(
        self,
        embedding_model: Callable[[str], Awaitable[list[float]]],
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
            query_vector=await self.embedding_model(last_message),
            items_with_vectors=[
                (friend, await self.embedding_model(friend.get_description())) for friend in agent_friends
            ],
        )[0]

        if not friend:
            msg = "No friends available to ask for help."
            raise ValueError(msg)

        friend_name = friend.get_name()

        # create conversation
        conversation = context.conversation_manager.start_conversation(f"HelpFrom{friend_name}-{generate_random_id()}")

        # send message to friend
        conversation.add_message(entity, "Can you help me with something?")
        conversation.add_message(friend, f"Sure, {entity.get_name()}! How can I assist you?")

        # relay the context to the friend
        last_result = context.last_result

        context_json = last_result.as_json_pretty()

        chat_history = context.conversation.get_chat_history()

        messages = chat_history.as_dicts()

        last_message = messages[-1]

        message = ""

        if not context.last_result.is_empty():
            # override content
            message = f"""
            The user asked me {last_message["content"]}

            Here is the context of the request:\n
            {context_json}

            Could you help?
            """
        else:
            message = f"""The user asked me "{last_message["content"]}". But I'm not sure how to answer their request. Could you help?"""  # noqa: E501

        conversation.add_message(entity, message)

        # set new agent in context
        context.agent = friend

        # friend makes a new workspace
        friend.workspace.reset()

        action_result, context = await friend.work(context)

        # get the message before the last one (the last one is the StopAction)
        action_history_tuple = context.agent.workspace.action_history.get_history_at_index(-2)

        action_result = action_history_tuple[1] if action_history_tuple else ActionResult()

        response = action_result.get_param("response")

        wrapped_res = f"I completed the task. Relay this response to the user: {response}"

        conversation.add_message(friend, wrapped_res)

        res = ActionResult()
        res.set_param("response", response)
        return res
