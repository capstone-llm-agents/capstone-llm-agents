"""Ollama call LLM model."""

import ollama


def call_llm(prompt: str) -> str:
    """Call the Ollama LLM with the given model and prompt."""
    model = "gemma3"
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    content = response.message.content

    if not content:
        msg = "No content returned from Ollama LLM."
        raise ValueError(msg)
    return content


def call_llm_with_messages(messages: list[dict]) -> str:
    """Call the Ollama LLM with a list of messages."""
    model = "gemma3"
    response = ollama.chat(model=model, messages=messages)
    content = response.message.content

    if not content:
        msg = "No content returned from Ollama LLM."
        raise ValueError(msg)
    return content


# TODO move out from here


class Message:
    """Message class for LLM interactions."""

    def __init__(self, role: str, content: str) -> None:
        """Initialize the message with a role and content."""
        self.role = role
        self.content = content

    def as_dict(self) -> dict:
        """Return the message as a dictionary."""
        return {"role": self.role, "content": self.content}


class UserMessage(Message):
    """User message class for LLM interactions."""

    def __init__(self, content: str) -> None:
        """Initialize the user message with content."""
        super().__init__(role="user", content=content)


class AssistantMessage(Message):
    """Assistant message class for LLM interactions."""

    def __init__(self, content: str) -> None:
        """Initialize the assistant message with content."""
        super().__init__(role="assistant", content=content)


class ChatHistory:
    """Chat history class to store messages."""

    def __init__(self) -> None:
        """Initialize an empty chat history."""
        self.messages: list[Message] = []

    def add_message(self, message: Message) -> None:
        """Add a message to the chat history."""
        self.messages.append(message)

    def as_dicts(self) -> list[dict]:
        """Return the chat history as a list of dictionaries."""
        return [message.as_dict() for message in self.messages]


class Example:
    """Example class for LLM interactions."""

    def __init__(self, user_message: UserMessage, assistant_message: AssistantMessage) -> None:
        """Initialize the example with user and assistant messages."""
        self.user_message = user_message
        self.assistant_message = assistant_message


def call_llm_with_examples(examples: list[Example], user_message: UserMessage) -> str:
    """Call the Ollama LLM with examples and a user message."""
    model = "gemma3"
    messages = [example.user_message.as_dict() for example in examples]
    messages.append(user_message.as_dict())

    response = ollama.chat(model=model, messages=messages)
    content = response.message.content

    if not content:
        msg = "No content returned from Ollama LLM."
        raise ValueError(msg)
    return content
