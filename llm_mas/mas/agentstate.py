from typing_extensions import TypedDict


class Message(TypedDict):
    role: str
    content: str


class ConversationState(TypedDict):
    name: str
    messages: list[Message]


class State(TypedDict):
    conversations: list[ConversationState]
