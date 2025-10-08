"""Default communication interface."""

from typing import TYPE_CHECKING, override

from llm_mas.action_system.core.action_context import ActionContext
from llm_mas.action_system.core.action_result import ActionResult
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
    ThanksHandler,
)
from llm_mas.communication.comm_extras import CommError, Reason
from llm_mas.communication.interface import CommunicationInterface, CommunicationState
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

if TYPE_CHECKING:
    from llm_mas.mas.agent import Agent


from llm_mas.logging.loggers import APP_LOGGER
from llm_mas.mas.conversation import AssistantMessage
from llm_mas.model_providers.api import ModelsAPI


class DefaultCommunicationInterface(CommunicationInterface):
    """Default communication interface."""

    def __init__(self, agent: "Agent") -> None:
        """Initialize the default communication interface."""
        super().__init__(agent)

        # add all the default handlers
        # NOTE: The invariance issue is not relevant here since we choose the types based on message_type
        self.add_message_handler(DefaultProposalHandler())  # pyright: ignore[reportArgumentType]
        self.add_message_handler(DefaultRejectionHandler())  # pyright: ignore[reportArgumentType]
        self.add_message_handler(DefaultAcceptanceHandler())  # pyright: ignore[reportArgumentType]
        self.add_message_handler(DefaultQueryHandler())  # pyright: ignore[reportArgumentType]
        self.add_message_handler(DefaultTaskHandler())  # pyright: ignore[reportArgumentType]
        self.add_message_handler(DefaultInformationHandler())  # pyright: ignore[reportArgumentType]
        self.add_message_handler(DefaultDisappointmentHandler())  # pyright: ignore[reportArgumentType]
        self.add_message_handler(DefaultErrorHandler())  # pyright: ignore[reportArgumentType]
        self.add_message_handler(DefaultEndHandler())  # pyright: ignore[reportArgumentType]
        self.add_message_handler(DefaultFreeFormHandler())


# default handlers
class DefaultProposalHandler(ProposalHandler):
    """Handler for proposal messages."""

    @override
    def handle_message(
        self,
        message: ProposalMessage,
        state: CommunicationState,
    ) -> AcceptanceMessage | RejectionMessage:
        """Handle an incoming proposal message."""
        # for simplicity just accept all proposals
        # in a real system you might want to check the proposal against some criteria
        return AcceptanceMessage(sender=state.talking_to)


class DefaultRejectionHandler(RejectionHandler):
    """Handler for rejection messages."""

    @override
    def handle_message(self, message: RejectionMessage, state: CommunicationState) -> DisappointmentMessage:
        """Handle an incoming rejection message."""
        return DisappointmentMessage(
            sender=state.talking_to,
            reason=Reason("The proposal was rejected."),
            content="That's disappointing.",
            send_to_self=True,
        )


class DefaultAcceptanceHandler(AcceptanceHandler):
    """Handler for acceptance messages."""

    @override
    def handle_message(
        self,
        message: AcceptanceMessage,
        state: CommunicationState,
    ) -> TaskMessage:
        """Handle an incoming acceptance message."""
        if state.current_task is None:
            msg = "No current task to accept."
            raise ValueError(msg)

        return TaskMessage(
            sender=state.talking_to,
            task=state.current_task,
            content="Please start working on the task.",
        )


class DefaultQueryHandler(QueryHandler):
    """Handler for query messages."""

    @override
    async def handle_message_async(
        self,
        message: QueryMessage,
        state: CommunicationState,
    ) -> InformationMessage | ErrorMessage:
        """Handle an incoming query message."""
        prompt = message.content

        result = ActionResult()
        result.set_param("query", prompt)

        action_context = ActionContext.from_action_result(result, message.action_context)

        try:
            action_result, _ = await state.talking_to.work(action_context)
            return InformationMessage(
                sender=state.talking_to,
                content=f"Here is the information you requested about '{prompt}'.",
                action_result=action_result,
            )
        except Exception as e:  # noqa: BLE001
            return ErrorMessage(sender=state.talking_to, error=CommError(str(e)), content=str(e))


class DefaultTaskHandler(TaskHandler):
    """Handler for task messages."""

    @override
    async def handle_message_async(
        self,
        message: TaskMessage,
        state: CommunicationState,
    ) -> InformationMessage | ErrorMessage:
        """Handle an incoming task message."""
        # execute the task using the agent's action system
        APP_LOGGER.debug(f"Executing task: {message.task.description}")

        # Mark task as in progress
        message.task.mark_in_progress()

        try:
            action_result, _ = await state.talking_to.work(message.task.action_context)

            # Mark task as completed
            message.task.mark_completed()

            return InformationMessage(
                sender=state.talking_to,
                content=f"Task '{message.task.description}' completed successfully.",
                action_result=action_result,
            )
        except Exception as e:  # noqa: BLE001
            # Mark task as failed
            message.task.mark_failed(str(e))

            return ErrorMessage(sender=state.talking_to, error=CommError(str(e)), content=str(e))


class DefaultInformationHandler(InformationHandler):
    """Handler for information messages."""

    @override
    def handle_message(
        self,
        message: InformationMessage,
        state: CommunicationState,
    ) -> ThanksMessage | EndMessage:
        """Handle an incoming information message."""
        # for simplicity just thank and end the conversation
        return EndMessage(sender=state.talking_to, content="Thank you for the information. Goodbye!")


class DefaultThanksHandler(ThanksHandler):
    """Handler for thanks messages."""

    @override
    def handle_message(self, message: ThanksMessage, state: CommunicationState) -> EndMessage:
        """Handle an incoming thanks message."""
        # for simplicity just end the conversation
        return EndMessage(sender=state.talking_to, content="You're welcome! Goodbye!")


class DefaultDisappointmentHandler(DisappointmentHandler):
    """Handler for disappointment messages."""

    @override
    def handle_message(self, message: DisappointmentMessage, state: CommunicationState) -> ProposalMessage | EndMessage:
        """Handle an incoming disappointment message."""
        # for simplicity just end the conversation
        return EndMessage(sender=state.talking_to, content="Goodbye!")


class DefaultErrorHandler(ErrorHandler):
    """Handler for error messages."""

    @override
    def handle_message(self, message: ErrorMessage, state: CommunicationState) -> DisappointmentMessage:
        """Handle an incoming error message."""
        # for simplicity just express disappointment
        return DisappointmentMessage(
            sender=state.talking_to,
            reason=Reason(f"There was an error: {message.error.text}"),
            content="That's not what I wanted.",
            send_to_self=True,
        )


class DefaultEndHandler(EndHandler):
    """Handler for end messages."""

    @override
    def handle_message(self, message: AssistantMessage, state: CommunicationState) -> EndMessage:
        """Handle an incoming end message by acknowledging it."""
        # just acknowledge the end message
        return EndMessage(sender=state.talking_to, content="Goodbye!")


class DefaultFreeFormHandler(FreeFormHandler):
    """Handler for free form messages."""

    async def handle_message_async(self, message: AssistantMessage, state: CommunicationState) -> AssistantMessage:
        """Handle an incoming free form message by echoing it back."""
        # just respond using LLM
        prompt = message.content

        response = await ModelsAPI.call_llm(prompt)

        # create a new message to return
        return AssistantMessage(
            sender=state.talking_to,
            content=response,
            message_type=message.message_type,
        )
