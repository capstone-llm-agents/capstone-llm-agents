"""Default communication interface."""

from llm_mas.communication.base_handlers import (
    AcceptanceHandler,
    DisappointmentHandler,
    EndHandler,
    ErrorHandler,
    FreeFormHandler,
    InformationHandler,
    ProposalHandler,
    QueryHandler,
    RejectionHandler,
    TaskHandler,
    WaitHandler,
)
from llm_mas.communication.interface import CommunicationInterface, CommunicationState
from llm_mas.mas.agent import Agent
from llm_mas.mas.conversation import AssistantMessage
from llm_mas.model_providers.api import ModelsAPI


class DefaultCommunicationInterface(CommunicationInterface):
    """Default communication interface."""

    def __init__(self, agent: Agent) -> None:
        """Initialize the default communication interface."""
        super().__init__(agent)


# default handlers
class DefaultProposalHandler(ProposalHandler):
    """Handler for proposal messages."""


class DefaultRejectionHandler(RejectionHandler):
    """Handler for rejection messages."""


class DefaultAcceptanceHandler(AcceptanceHandler):
    """Handler for acceptance messages."""


class DefaultWaitHandler(WaitHandler):
    """Handler for wait messages."""


class DefaultQueryHandler(QueryHandler):
    """Handler for query messages."""


class DefaultTaskHandler(TaskHandler):
    """Handler for task messages."""


class DefaultInformationHandler(InformationHandler):
    """Handler for information messages."""


class DefaultDisappointmentHandler(DisappointmentHandler):
    """Handler for disappointment messages."""


class DefaultErrorHandler(ErrorHandler):
    """Handler for error messages."""


class DefaultEndHandler(EndHandler):
    """Handler for end messages."""


class DefaultFreeFormHandler(FreeFormHandler):
    """Handler for free form messages."""

    async def handle_message_async(self, message: AssistantMessage, state: CommunicationState) -> AssistantMessage:
        """Handle an incoming free form message by echoing it back."""
        # just respond using LLM
        prompt = message.content

        response = await ModelsAPI.call_llm(prompt)

        # create a new message to return
        return AssistantMessage(
            sender=state.agent,
            content=response,
            message_type=message.message_type,
        )
