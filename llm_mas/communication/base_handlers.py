"""Base handlers."""

from llm_mas.communication.interface import MessageHandler
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
    WaitMessage,
)
from llm_mas.mas.conversation import AssistantMessage


class ProposalHandler(MessageHandler[ProposalMessage]):
    """Handler for proposal messages."""


class RejectionHandler(MessageHandler[RejectionMessage]):
    """Handler for rejection messages."""


class AcceptanceHandler(MessageHandler[AcceptanceMessage]):
    """Handler for acceptance messages."""


class WaitHandler(MessageHandler[WaitMessage]):
    """Handler for wait messages."""


class QueryHandler(MessageHandler[QueryMessage]):
    """Handler for query messages."""


class TaskHandler(MessageHandler[TaskMessage]):
    """Handler for task messages."""


class InformationHandler(MessageHandler[InformationMessage]):
    """Handler for information messages."""


class DisappointmentHandler(MessageHandler[DisappointmentMessage]):
    """Handler for disappointment messages."""


class ErrorHandler(MessageHandler[ErrorMessage]):
    """Handler for error messages."""


class EndHandler(MessageHandler[EndMessage]):
    """Handler for end messages."""


class FreeFormHandler(MessageHandler[AssistantMessage]):
    """Handler for free form messages."""
