"""An action to list available friends in the agent system."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.communication.interface import CommunicationState
from llm_mas.communication.messages import EndMessage, ProposalMessage
from llm_mas.communication.task.agent_task import Task
from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.mas.agent import Agent
from llm_mas.mas.conversation import UserMessage
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
        similarity_threshold: float = 0.6,
    ) -> None:
        """Initialize the Communicate action."""
        super().__init__(description="Asks a friend for help")
        self.embedding_model = embedding_model
        self.vector_selector = vector_selector or VectorSelector()
        self.similarity_threshold = similarity_threshold

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

        should_delegate = await self.should_delegate_to_friend(last_message, context)
        
        if not should_delegate:
            res = ActionResult()
            res.set_param("response", await self.generate_simple_response(last_message))
            return res

        agent_friends = [friend for friend in friends if isinstance(friend, Agent)]

        friend_with_similarity = self.vector_selector.select(
            query_vector=await self.embedding_model(last_message, ModelType.EMBEDDING),
            items_with_vectors=[
                (friend, await self.embedding_model(friend.get_description(), ModelType.EMBEDDING))
                for friend in agent_friends
            ],
        )
        
        friend, similarity = friend_with_similarity[0], friend_with_similarity[1]

        if not friend or similarity < self.similarity_threshold:
            res = ActionResult()
            res.set_param("response", await self.generate_simple_response(last_message))
            return res

        friend_name = friend.get_name()

        context_str = self.get_context_from_last_result(context)

        chat_history = context.conversation.get_chat_history()

        messages = chat_history.as_dicts()

        last_message = messages[-1]

        # friend makes a new workspace
        friend.workspace.reset()

        # create new comm state
        comm_state = CommunicationState(context.agent, friend)

        task_description = await self.get_task_description(context_str, messages)

        # Create a fresh ActionContext for the delegated agent
        # This prevents confusion from reusing AssistantAgent's context
        fresh_result = ActionResult()
        fresh_result.set_param("query", task_description)
        fresh_result.set_param("user_request", last_message["content"])
        
        # Create new conversation for the friend agent with the task description
        conversation_name = self.convert_description_to_conversation_name(task_description)
        fresh_conversation = context.conversation_manager.start_conversation(
            f"{conversation_name}-task-{generate_random_id()}",
        )
        
        # Add the task description as a user message to give context
        fresh_conversation.add_message(context.user, task_description)
        
        fresh_context = ActionContext(
            conversation=fresh_conversation,
            last_result=fresh_result,
            mcp_client=context.mcp_client,
            agent=friend,
            user=context.user,
            conversation_manager=context.conversation_manager,
            client=context.client,
        )
        
        APP_LOGGER.debug(f"Created fresh context for {friend_name} with task: {task_description}")
        
        task = Task(description=task_description, action_context=fresh_context)

        # create conversation
        conversation_name = self.convert_description_to_conversation_name(task_description)
        conversation = context.conversation_manager.start_conversation(
            f"{conversation_name}-{generate_random_id()}",
        )

        comm_state.current_task = task

        # create conversation for the inter-agent communication (separate from task conversation)
        comm_conversation_name = self.convert_description_to_conversation_name(f"comm-{task_description}")
        conversation = context.conversation_manager.start_conversation(
            f"{comm_conversation_name}-{generate_random_id()}",
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

    async def get_task_description(self, context_str: str, messages: list[dict]) -> str:
        """Generate a task description based on the context and recent messages."""
        # Include last 3-5 messages for context (to handle references like "then", "there", etc.)
        recent_messages = messages[-5:] if len(messages) >= 5 else messages
        
        # Format recent messages as a conversation
        conversation_context = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in recent_messages
        ])
        
        prompt = f"""
        You are an AI assistant that helps generate task descriptions for specialized agents.
        Given the conversation context below, generate a concise task description that captures:
        1. What the user is asking for
        2. Any temporal references (dates, times, "today", "then", etc.)
        3. Any location references (places mentioned in recent messages)
        4. Any other relevant context from the conversation
        
        Recent conversation:
        {conversation_context}
        
        Additional context from previous actions:
        {context_str}
        
        Generate a clear, standalone task description that the specialized agent can understand without needing the full conversation.
        ONLY RESPOND WITH THE TASK DESCRIPTION. DO NOT RESPOND WITH ANYTHING ELSE. NO PREAMBLE OR EXPLANATION. KEEP IT CONCISE (1-2 sentences).
        
        Task Description:
        """
        task_desc = await ModelsAPI.call_llm(prompt)
        APP_LOGGER.debug(f"Generated task description: {task_desc}")
        return task_desc

    def convert_description_to_conversation_name(self, description: str) -> str:
        """Convert a task description to a valid conversation name."""
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

    async def should_delegate_to_friend(self, message: str, context: ActionContext) -> bool:
        """Determine if the message requires delegation to a specialized agent."""
        prompt = f"""
        You are analyzing whether a user message requires specialized agent assistance (like weather, calendar, or web search).
        
        User message: {message}
        
        Does this message require specialized tools or agent capabilities? Consider:
        - Does it ask for specific information (weather, calendar events, web searches)?
        - Does it require actions (creating calendar events, booking, searching)?
        - Or is it just general conversation/greeting/simple question?
        
        Respond with ONLY "yes" or "no".
        """
        response = await ModelsAPI.call_llm(prompt, ModelType.DEFAULT)
        return response.strip().lower() == "yes"

    async def generate_simple_response(self, message: str) -> str:
        """Generate a simple conversational response."""
        prompt = f"""
        You are a helpful assistant. Respond naturally to this message:
        
        User: {message}
        
        Assistant:
        """
        return await ModelsAPI.call_llm(prompt, ModelType.DEFAULT)
