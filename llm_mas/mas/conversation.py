"""The conversation module defines messages, chat history and conversation management for the multi-agent system."""

from llm_mas.mas.agent import Agent
from llm_mas.mas.entity import Entity
from llm_mas.mas.user import User


class Message:
    """Message class for LLM interactions."""

    def __init__(self, role: str, content: str, sender: Entity) -> None:
        """Initialize the message with a role and content."""
        self.role = role
        self.content = content
        self.sender = sender

    def as_dict(self) -> dict:
        """Return the message as a dictionary."""
        return {"role": self.role, "content": self.content}


class UserMessage(Message):
    """User message class for LLM interactions."""

    def __init__(self, content: str, sender: User) -> None:
        """Initialize the user message with content."""
        super().__init__(role="user", content=content, sender=sender)


class AssistantMessage(Message):
    """Assistant message class for LLM interactions."""

    def __init__(self, content: str, sender: Agent) -> None:
        """Initialize the assistant message with content."""
        super().__init__(role="assistant", content=content, sender=sender)


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


class UserAssistantExample:
    """Example class for LLM interactions."""

    def __init__(self, user_message: UserMessage, assistant_message: AssistantMessage) -> None:
        """Initialize the example with user and assistant messages."""
        self.user_message = user_message
        self.assistant_message = assistant_message


class Conversation:
    """Conversation class to manage entity interactions."""

    def __init__(self) -> None:
        """Initialize an empty conversation."""
        self.chat_history = ChatHistory()
        self.participants: set[Entity] = set()

    def add_message(self, entity: Entity, content: str) -> None:
        """Add a message to the conversation."""
        message = Message(role=entity.role, content=content, sender=entity)
        self.chat_history.add_message(message)
        self.participants.add(entity)

    def get_chat_history(self) -> ChatHistory:
        """Return the chat history of the conversation."""
        return self.chat_history


class ConversationManager:
    """Manager class for handling multiple conversations."""

    def __init__(self) -> None:
        """Initialize the conversation manager."""
        self.conversations: dict[str, Conversation] = {}

    def start_conversation(self, conversation_name: str) -> Conversation:
        """Start a new conversation."""
        if conversation_name in self.conversations:
            msg = f"Conversation '{conversation_name}' already exists."
            raise ValueError(msg)
        conversation = Conversation()
        self.conversations[conversation_name] = conversation
        return conversation

    def get_conversation(self, conversation_name: str) -> Conversation:
        """Get an existing conversation."""
        if conversation_name not in self.conversations:
            msg = f"Conversation '{conversation_name}' does not exist."
            raise ValueError(msg)
        return self.conversations[conversation_name]

    def end_conversation(self, conversation_name: str) -> None:
        """End a conversation."""
        if conversation_name not in self.conversations:
            msg = f"Conversation '{conversation_name}' does not exist."
            raise ValueError(msg)
        del self.conversations[conversation_name]

    def get_all_conversations(self) -> list[Conversation]:
        """Return all conversations."""
        return list(self.conversations.values())

    def clear_conversations(self) -> None:
        """Clear all conversations."""
        self.conversations.clear()

    def get_conversations_with_participant(self, entity: Entity) -> list[Conversation]:
        """Get all conversations that include a specific participant."""
        return [conversation for conversation in self.conversations.values() if entity in conversation.participants]

    def get_conversation_with_participants(self, entities: list[Entity]) -> Conversation | None:
        """Get a conversation that includes all specified participants."""
        for conversation in self.conversations.values():
            if all(entity in conversation.participants for entity in entities):
                return conversation
        return None

    def get_conversations_with_only_participants(self, entities: list[Entity]) -> list[Conversation]:
        """Get conversations that include only the specified participants."""
        return [
            conversation
            for conversation in self.conversations.values()
            if set(conversation.participants) == set(entities)
        ]
