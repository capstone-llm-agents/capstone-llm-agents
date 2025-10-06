"""Action class for the multi-agent system."""

from typing import Any

from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class Action:
    """Base class for all actions in the system."""

    def __init__(self, description: str, name: str | None = None, params_schema: dict[str, Any] | None = None) -> None:
        """Initialize the action with a name."""
        self.name = name if name is not None else self.__class__.__name__
        self.description = description
        self.params_schema = params_schema if params_schema is not None else {}

        self.use_fragments = False

    async def do(self, params: ActionParams, context: ActionContext) -> ActionResult:
        """Perform the action with the given agent."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)

    def __eq__(self, other: object) -> bool:
        """Check equality based on the class name."""
        if not isinstance(other, Action):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        """Return the hash based on the class name."""
        return hash(self.name)

    def as_json(self) -> dict[str, Any]:
        """Return a JSON representation of the action."""
        return {"name": self.name, "description": self.description, "params": self.params_schema}

    def use_fragments_for_context(self) -> None:
        """Set the action to use fragments for context."""
        self.use_fragments = True

    def reset(self) -> None:
        """Reset any internal state of the action."""

    def is_using_fragments(self) -> bool:
        """Return whether the action is using fragments for context."""
        return self.use_fragments

    # TODO: temp
    def get_context_from_last_result(self, context: ActionContext) -> str:
        """Get context string from the last action result's fragments."""
        # not using fragments, use last result as json context dict
        if not self.use_fragments or context.last_result.is_empty():
            return context.last_result.as_json_pretty()

        # using fragments, compile context from fragments
        context_strings: list[str] = []

        for fragment in context.last_result.fragments:
            agent_view = fragment.agent_view()

            chunks = agent_view.text_chunks

            # TODO: optimise later
            context_strings.append(f"--- Fragment: {fragment.name} ---")
            if fragment.description:
                context_strings.append(f"Description: {fragment.description}")
            context_strings.append(f"Source: {fragment.source.name}")
            context_strings.append(f"Kind: {fragment.kind.name}")
            context_strings.append("Content:")
            context_strings.extend(chunks)

        return "\n".join(context_strings)

    def get_last_message_content(self, context: ActionContext) -> str:
        """Get the content of the last message in the conversation."""
        chat_history = context.conversation.get_chat_history()
        messages = chat_history.as_dicts()
        last_message = messages[-1] if messages else None

        if not last_message:
            msg = "No chat history available to respond to."
            raise ValueError(msg)

        return last_message["content"]
