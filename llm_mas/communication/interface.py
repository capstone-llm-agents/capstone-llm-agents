"""Communication interface that defines how to act for different incoming messages."""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from llm_mas.communication.message_types import MessageType
    from llm_mas.mas.agent import Agent
    from llm_mas.mas.conversation import AssistantMessage


class CommunicationState:
    """State of the communication interface shared across handlers."""

    def __init__(self, agent: Agent, talking_to: Agent) -> None:
        """Initialize the communication state."""
        self.agent = agent
        """The agent using this communication interface."""
        self.talking_to = talking_to
        """The other agent in the conversation."""


TMsg = TypeVar("TMsg", bound="AssistantMessage")


class MessageHandler(Generic[TMsg]):  # noqa: UP046
    """Handler for a specific type of message."""

    def __init__(self, message_type: MessageType, *, use_async: bool = False) -> None:
        """Initialize the message handler with a message type."""
        self.message_type = message_type
        self.use_async = use_async

    def handle_message(self, message: TMsg, state: CommunicationState) -> AssistantMessage:
        """Handle an incoming message."""
        msg = "Should be implemented by subclasses."
        raise NotImplementedError(msg)

    async def handle_message_async(self, message: TMsg, state: CommunicationState) -> AssistantMessage:
        """Handle an incoming message asynchronously."""
        msg = "Should be implemented by subclasses."
        raise NotImplementedError(msg)


class CommunicationInterface:
    """Interface for handling different types of incoming messages."""

    def __init__(self, agent: Agent) -> None:
        """Initialize the communication interface."""
        self.message_handlers: dict[MessageType, MessageHandler[AssistantMessage]] = {}
        self.agent = agent

    def add_message_handler(self, handler: MessageHandler[AssistantMessage]) -> None:
        """Add a message handler for a specific message type."""
        self.message_handlers[handler.message_type] = handler

    async def handle_message(self, message: AssistantMessage, state: CommunicationState) -> AssistantMessage:
        """Handle an incoming message by delegating to the appropriate handler."""
        handler = self.message_handlers.get(message.message_type)
        if handler:
            if handler.use_async:
                return await handler.handle_message_async(message, state)
            return handler.handle_message(message, state)
        msg = f"No handler found for message type {message.message_type}."
        raise ValueError(msg)
