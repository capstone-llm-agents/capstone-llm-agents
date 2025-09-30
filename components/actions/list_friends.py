"""An action to list available friends in the agent system."""

from collections.abc import Awaitable, Callable
from typing import override
import json
from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.logging.loggers import APP_LOGGER
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
        super().__init__(description="Ask other agents for help who may be able to answer the users question")
        self.embedding_model = embedding_model
        self.vector_selector = vector_selector or VectorSelector()
        self.friend_to_contact = ''
        self.message_to_friend = ''

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

        friend_lookup = {friend.name: friend for friend in friends if isinstance(friend, Agent)}
        #plan_as_dict = json.loads(context.plan)
        APP_LOGGER.debug(f"Plan within askfriend: {type(context.plan)}")

        for step in context.plan.get('steps', []):
            if not step.get("Completed"):
                step["Completed"] = True
                arguments = step.get("arguments", {})
                agent_name = arguments.get('agent_name')
                if agent_name and agent_name in friend_lookup:
                    self.friend_to_contact = friend_lookup[agent_name]
                    self.message_to_friend = arguments.get('query')
                    APP_LOGGER.debug(f"friend found {self.friend_to_contact.name}")

                    break
            else:
                continue

            """self.vector_selector.select(
            query_vector=await self.embedding_model(last_message),
            items_with_vectors=[
                (friend, await self.embedding_model(friend.get_description())) for friend in agent_friends
            ],
        ))[0]
       
        if not friend:
            msg = "No friends available to ask for help."
            raise ValueError(msg)
        """
        if not self.friend_to_contact and not self.message_to_friend:
            res = ActionResult()
            res.set_param("response", "No friend found to contact or not message to friend found")
            return res
        friend_name = self.friend_to_contact.get_name()

        # create conversation
        conversation = context.conversation_manager.start_conversation(f"HelpFrom{friend_name}-{generate_random_id()}")

        # send message to friend
        conversation.add_message(entity, "Can you help me with something?")
        conversation.add_message(self.friend_to_contact, f"Sure, {entity.get_name()}! How can I assist you?")

        # relay the context to the friend
        last_result = context.last_result

        context_json = last_result.as_json_pretty()

        chat_history = context.conversation.get_chat_history()

        messages = chat_history.as_dicts()



        message = ""

        if not context.last_result.is_empty():
            # override content
            message = f"""
            The user asked me {self.message_to_friend}

            Could you help?
            """
        else:
            message = f"""The user asked me "{self.message_to_friend}". But I'm not sure how to answer their request. Could you help?"""  # noqa: E501
        APP_LOGGER.debug(f"This is the message being passed to friend: {message}")
        conversation.add_message(entity, message)

        # set new agent in context
        context.agent = self.friend_to_contact

        # friend makes a new workspace
        self.friend_to_contact.workspace.reset()

        action_result, context = await self.friend_to_contact.work(context)

        # get the message before the last one (the last one is the StopAction)
        action_history_tuple = context.agent.workspace.action_history.get_history_at_index(-2)

        action_result = action_history_tuple[1] if action_history_tuple else ActionResult()

        response = action_result.get_param("response")

        wrapped_res = f"I completed the task. Relay this response to the user: {response}"

        conversation.add_message(self.friend_to_contact, wrapped_res)

        res = ActionResult()
        res.set_param("response", response)
        return res
