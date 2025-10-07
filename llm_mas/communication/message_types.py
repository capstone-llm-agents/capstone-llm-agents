"""Message types for inter-agent communication."""

from enum import Enum, auto


class MessageType(Enum):
    """Enum for different types of messages over the network."""

    # proposal based dialogue (initiating a conversation)
    PROPOSAL = auto()  # "Can you help me with something?" -> yields other ACCEPTANCE or REJECTION
    # has ActionContext
    REJECTION = auto()  # "I cannot help with that." -> yields other DISAPPOINTMENT
    # has Reason
    ACCEPTANCE = auto()  # "Sure, I can help with that." -> yields other TASK

    # task based dialogue (handling the task)
    QUERY = auto()  # "What is on Anton's calendar today?" -> yields other INFORMATION or ERROR
    # has ActionContext
    TASK = auto()  # "Book a flight to New York for next Monday." -> yields other INFORMATION or ERROR
    # NOTE: A QUERY or TASK are both REQUESTS. REQUESTS can be follow ups which can include extra INFORMATION.

    # results based dialogue (providing results)
    INFORMATION = auto()  # "The weather in New York is sunny." -> yields other THANKS or DISAPPOINTMENT
    # has ActionResult

    # closing based dialogue (ending the conversation)
    THANKS = auto()  # "Thanks for your help!" -> yields END
    DISAPPOINTMENT = auto()  # "That's not what I wanted." -> yields self PROPOSAL or END
    # has Reason
    # NOTE: DISAPPOINTMENT can yield PROPOSAL if the other side wants to try again.
    # It is also the only message type that yields a response from itself.
    ERROR = auto()  # "There was an error processing your request." -> yields other DISAPPOINTMENT
    # has Error
    END = auto()  # "Thank you for your help. Goodbye." -> yields nothing

    # no form
    FREE_FORM = auto()  # "Hello!" -> yields other FREE_FORM or END
