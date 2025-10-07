"""Communication interface that defines how to act for different incoming messages."""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from llm_mas.communication.message_types import MessageType
    from llm_mas.mas.conversation import AssistantMessage


class CommunicationState:
    """State of the communication interface shared across handlers."""

    def __init__(self) -> None:
        """Initialize the communication state."""


TMsg = TypeVar("TMsg", bound="AssistantMessage")


class MessageHandler(Generic[TMsg]):  # noqa: UP046
    """Handler for a specific type of message."""

    def __init__(self, message: TMsg) -> None:
        """Initialize the message handler with a message type."""
        self.message_type = message.message_type

    def handle_message(self, message: TMsg, state: CommunicationState) -> None:
        """Handle an incoming message."""
        msg = "Should be implemented by subclasses."
        raise NotImplementedError(msg)


class CommunicationInterface:
    """Interface for handling different types of incoming messages."""

    def __init__(self) -> None:
        """Initialize the communication interface."""
        self.message_handlers: dict[MessageType, MessageHandler[AssistantMessage]] = {}

    def add_message_handler(self, handler: MessageHandler[AssistantMessage]) -> None:
        """Add a message handler for a specific message type."""
        self.message_handlers[handler.message_type] = handler

    def handle_message(self, message: AssistantMessage, state: CommunicationState) -> None:
        """Handle an incoming message by delegating to the appropriate handler."""
        handler = self.message_handlers.get(message.message_type)
        if handler:
            handler.handle_message(message, state)
        else:
            msg = f"No handler found for message type {message.message_type}."
            raise ValueError(msg)
