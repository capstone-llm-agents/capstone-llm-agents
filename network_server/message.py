"""A message that can be sent over the network."""

from llm_mas.communication.message_types import MessageType
from network_server.network_fragment import NetworkFragment


class NetworkMessage:
    """A message that can be sent over the network."""

    def __init__(  # noqa: PLR0913
        self,
        sender: str,  # name of the agent
        sender_client: str,  # name/id of the client
        recipient: str,  # name of the agent
        recipient_client: str,  # name/id of the client
        fragments: list[NetworkFragment],
        message_type: MessageType,
        context: dict | None = None,  # some messages may need extra context / data
    ) -> None:
        """Initialize the message with sender, recipient, content, and type."""
        self.sender = sender
        self.sender_client = sender_client
        self.recipient = recipient
        self.recipient_client = recipient_client
        self.fragments = fragments
        self.message_type = message_type
        self.context = context if context is not None else {}

    def serialize(self) -> dict:
        """Serialize the message to a dictionary."""
        return {
            "sender": self.sender,
            "sender_client": self.sender_client,
            "recipient": self.recipient,
            "recipient_client": self.recipient_client,
            "fragments": [fragment.serialize() for fragment in self.fragments],
            "message_type": self.message_type.name,
            "context": self.context,
        }
