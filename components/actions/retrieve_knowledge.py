"""Retrieve knowledge relevant to the current conversation from the KB."""

from typing import override

from llm_mas.action_system.core.action import Action
from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.communication.message_types import MessageType
from llm_mas.knowledge_base.knowledge_base import GLOBAL_KB


class RetrieveKnowledge(Action):
    """Action: query the Knowledge Base to retrieve relevant facts for RAG."""

    def __init__(self) -> None:
        """Initialize the RetrieveKnowledge action."""
        super().__init__(description="Retrieves knowledge from the knowledge base.")

    @override
    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Query the KB using the latest user message as the retrieval query.

        Returns an ActionResult with:
        - facts: list[str] of the top result texts
        - sources: list[dict] with source_path and score for traceability
        """

        messages = context.conversation.get_chat_history().as_dicts()

        # Find last user message content
        user_query = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_query = str(msg.get("content", "")).strip()
                break

        results = GLOBAL_KB.query(user_query, top_k=5) if user_query else []
        facts = [r["text"] for r in results]
        sources = [{"source_path": r["source_path"], "score": r["score"]} for r in results]

        res = ActionResult()
        res.set_param("facts", facts)
        res.set_param("sources", sources)

        # network client
        client = context.client

        friends = await client.network_client.get_friends()
        bob = next((f for f in friends if f["username"] == "bob"), None)

        if not bob:
            msg = "Bob is not in your friends list. Cannot send message."
            raise RuntimeError(msg)

        recipient_id = bob["id"]

        success = await client.network_client.send_message(
            recipient_id=recipient_id,
            fragments=[],
            recipient_agent=context.agent.name,
            message_type=MessageType.PROPOSAL,
            sender_agent=context.agent.name,
            context={
                "task_description": "What is the weather in Tokyo?",
            },
        )

        if not success:
            msg = "Failed to send message to Bob via network."
            raise RuntimeError(msg)

        return res
