"""A message that can be sent over the network."""

from enum import Enum, auto

from network_server.network_fragment import NetworkFragment


class MessageType(Enum):
    """Enum for different types of messages over the network."""

    # proposal based dialogue (initiating a conversation)
    PROPOSAL = auto()  # "Can you help me with something?" -> yields other ACCEPTANCE or REJECTION
    REJECTION = auto()  # "I cannot help with that." -> yields other DISAPPOINTMENT
    ACCEPTANCE = auto()  # "Sure, I can help with that." -> yields other WAIT

    # task based dialogue (handling the task)
    QUERY = auto()  # "What is on Anton's calendar today?" -> yields other INFORMATION or ERROR
    TASK = auto()  # "Book a flight to New York for next Monday." -> yields other CONFIRMATION or ERROR
    # NOTE: A QUERY or TASK are both REQUESTS. REQUESTS can be follow ups

    WAIT = auto()  # "Ok, thanks let me know when you're done." -> yields other INFORMATION or ERROR or QUERY or TASK
    # WAIT can also yield QUERY or TASK from the other side if they need more information perhaps counter-intuitively

    # results based dialogue (providing results)
    INFORMATION = auto()  # "The weather in New York is sunny." -> yields other THANKS or DISAPPOINTMENT
    CONFIRMATION = auto()  # "Your flight has been booked." -> yields other THANKS or DISAPPOINTMENT

    # closing based dialogue (ending the conversation)
    THANKS = auto()  # "Thanks for your help!" -> yields END
    DISAPPOINTMENT = auto()  # "That's not what I wanted." -> yields self PROPOSAL or END
    # NOTE: DISAPPOINTMENT can yield PROPOSAL if the other side wants to try again.
    # It is also the only message type that yields a response from itself.
    ERROR = auto()  # "There was an error processing your request." -> yields other DISAPPOINTMENT
    END = auto()  # "Thank you for your help. Goodbye." -> yields nothing


class NetworkMessage:
    """A message that can be sent over the network."""

    def __init__(
        self,
        sender: str,
        recipient: str,
        fragments: list[NetworkFragment],
        message_type: MessageType,
    ) -> None:
        """Initialize the message with sender, recipient, content, and type."""
        self.sender = sender
        self.recipient = recipient
        self.fragments = fragments
        self.message_type = message_type
