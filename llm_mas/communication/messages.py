"""Defines some of the message types used in inter-agent communication."""

from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_result import ActionResult
from llm_mas.communication.comm_extras import CommError, Reason
from llm_mas.communication.message_types import MessageType
from llm_mas.communication.task.agent_task import Task
from llm_mas.mas.agent import Agent
from llm_mas.mas.conversation import AssistantMessage


class ProposalMessage(AssistantMessage):
    """Proposal message class for LLM interactions."""

    def __init__(
        self,
        content: str,
        sender: Agent,
        action_context: ActionContext,
    ) -> None:
        """Initialize the proposal message with content and action context."""
        super().__init__(content=content, sender=sender, message_type=MessageType.PROPOSAL)
        self.action_context = action_context


class RejectionMessage(AssistantMessage):
    """Rejection message class for LLM interactions."""

    def __init__(self, sender: Agent, reason: Reason, content: str = "I cannot help with that.") -> None:
        """Initialize the rejection message with content and reason."""
        super().__init__(content=content, sender=sender, message_type=MessageType.REJECTION)
        self.reason = reason


class AcceptanceMessage(AssistantMessage):
    """Acceptance message class for LLM interactions."""

    def __init__(
        self,
        sender: Agent,
        content: str = "Sure, I can help with that.",
    ) -> None:
        """Initialize the acceptance message with content and action context."""
        super().__init__(content=content, sender=sender, message_type=MessageType.ACCEPTANCE)


class QueryMessage(AssistantMessage):
    """Query message class for LLM interactions."""

    def __init__(
        self,
        content: str,
        sender: Agent,
        action_context: ActionContext,
    ) -> None:
        """Initialize the query message with content and action context."""
        super().__init__(content=content, sender=sender, message_type=MessageType.QUERY)
        self.action_context = action_context


class TaskMessage(AssistantMessage):
    """Task message class for LLM interactions."""

    def __init__(
        self,
        content: str,
        sender: Agent,
        task: Task,
    ) -> None:
        """Initialize the task message with content and task."""
        super().__init__(content=content, sender=sender, message_type=MessageType.TASK)
        self.task = task


class InformationMessage(AssistantMessage):
    """Information message class for LLM interactions."""

    def __init__(self, content: str, sender: Agent, action_result: ActionResult) -> None:
        """Initialize the information message with content and action result."""
        super().__init__(content=content, sender=sender, message_type=MessageType.INFORMATION)
        self.action_result = action_result


class ThanksMessage(AssistantMessage):
    """Thanks message class for LLM interactions."""

    def __init__(self, sender: Agent, content: str = "Thanks for your help!") -> None:
        """Initialize the thanks message with content."""
        super().__init__(content=content, sender=sender, message_type=MessageType.THANKS)


class DisappointmentMessage(AssistantMessage):
    """Disappointment message class for LLM interactions."""

    def __init__(
        self,
        sender: Agent,
        reason: Reason,
        content: str = "That's not what I wanted.",
        *,
        send_to_self: bool = False,
    ) -> None:
        """Initialize the disappointment message with content and reason."""
        super().__init__(
            content=content,
            sender=sender,
            message_type=MessageType.DISAPPOINTMENT,
            send_to_self=send_to_self,
        )
        self.reason = reason


class ErrorMessage(AssistantMessage):
    """Error message class for LLM interactions."""

    def __init__(
        self,
        sender: Agent,
        error: CommError,
        content: str = "There was an error processing your request.",
    ) -> None:
        """Initialize the error message with content and error."""
        super().__init__(content=content, sender=sender, message_type=MessageType.ERROR)
        self.error = error


class EndMessage(AssistantMessage):
    """End message class for LLM interactions."""

    def __init__(self, sender: Agent, content: str = "Thank you for your help. Goodbye.") -> None:
        """Initialize the end message with content."""
        super().__init__(content=content, sender=sender, message_type=MessageType.END)
