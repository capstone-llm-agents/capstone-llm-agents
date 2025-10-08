"""Base handlers."""

from llm_mas.communication.interface import MessageHandler
from llm_mas.communication.message_types import MessageType
from llm_mas.communication.messages import (
    AcceptanceMessage,
    DisappointmentMessage,
    EndMessage,
    ErrorMessage,
    InformationMessage,
    ProposalMessage,
    QueryMessage,
    RejectionMessage,
    TaskMessage,
    ThanksMessage,
)
from llm_mas.mas.conversation import AssistantMessage


class ProposalHandler(MessageHandler[ProposalMessage]):
    """Handler for proposal messages."""

    def __init__(self, *, use_async: bool = False) -> None:
        """Initialize the proposal handler."""
        super().__init__(MessageType.PROPOSAL, use_async=use_async)


class RejectionHandler(MessageHandler[RejectionMessage]):
    """Handler for rejection messages."""

    def __init__(self, *, use_async: bool = False) -> None:
        """Initialize the rejection handler."""
        super().__init__(MessageType.REJECTION, use_async=use_async)


class AcceptanceHandler(MessageHandler[AcceptanceMessage]):
    """Handler for acceptance messages."""

    def __init__(self, *, use_async: bool = False) -> None:
        """Initialize the acceptance handler."""
        super().__init__(MessageType.ACCEPTANCE, use_async=use_async)


class QueryHandler(MessageHandler[QueryMessage]):
    """Handler for query messages."""

    def __init__(self, *, use_async: bool = True) -> None:
        """Initialize the query handler."""
        super().__init__(MessageType.QUERY, use_async=use_async)


class TaskHandler(MessageHandler[TaskMessage]):
    """Handler for task messages."""

    def __init__(self, *, use_async: bool = True) -> None:
        """Initialize the task handler."""
        super().__init__(MessageType.TASK, use_async=use_async)


class InformationHandler(MessageHandler[InformationMessage]):
    """Handler for information messages."""

    def __init__(self, *, use_async: bool = False) -> None:
        """Initialize the information handler."""
        super().__init__(MessageType.INFORMATION, use_async=use_async)


class ThanksHandler(MessageHandler[ThanksMessage]):
    """Handler for thanks messages."""

    def __init__(self, *, use_async: bool = False) -> None:
        """Initialize the thanks handler."""
        super().__init__(MessageType.THANKS, use_async=use_async)


class DisappointmentHandler(MessageHandler[DisappointmentMessage]):
    """Handler for disappointment messages."""

    def __init__(self, *, use_async: bool = False) -> None:
        """Initialize the disappointment handler."""
        super().__init__(MessageType.DISAPPOINTMENT, use_async=use_async)


class ErrorHandler(MessageHandler[ErrorMessage]):
    """Handler for error messages."""

    def __init__(self, *, use_async: bool = False) -> None:
        """Initialize the error handler."""
        super().__init__(MessageType.ERROR, use_async=use_async)


class EndHandler(MessageHandler[EndMessage]):
    """Handler for end messages."""

    def __init__(self, *, use_async: bool = False) -> None:
        """Initialize the end handler."""
        super().__init__(MessageType.END, use_async=use_async)


class FreeFormHandler(MessageHandler[AssistantMessage]):
    """Handler for free form messages."""

    def __init__(self, *, use_async: bool = False) -> None:
        """Initialize the free form handler."""
        super().__init__(MessageType.FREE_FORM, use_async=use_async)
