from core.agent import Agent
from core.capabiliity_manager import AgentCapabilities
from core.chat import ChatHistory
from core.mas import MAS

from capabilities.knowledge_base import Document


class MASAPI:
    """API layer between the user interface and the MAS."""

    documents: list[Document]
    agent_documents: dict[str, list[Document]]

    def __init__(self, mas: MAS):
        self.mas = mas
        self.documents = []

        # a dictionary of agent names to documents
        self.agent_documents = {}

    def add_document(self, document: Document, agent: Agent):
        """Add a document to the MAS."""
        self.documents.append(document)
        self.agent_documents.setdefault(agent.name, []).append(document)
        agent.capabilties.knowledge_base.ingest_document(document)

    def query_mas(self, query: str) -> str:
        """Query the MAS with a prompt."""
        return self.mas.handle_prompt_from_user(query)

    def get_agents(self) -> list[Agent]:
        """Get a list of agents in the MAS."""
        return self.mas.get_agents()

    def get_agent_capabilities(self, agent: Agent) -> AgentCapabilities:
        """Get the capabilities of an agent."""
        return agent.get_capabilities()

    def get_agent(self, name: str) -> Agent:
        """Get an agent by name."""
        return self.mas.get_agent(name)

    def get_documents(self) -> list[Document]:
        """Get a list of documents in the MAS."""
        return self.documents

    def get_agent_documents(self, agent: Agent) -> list[Document]:
        """Get a list of documents for an agent."""
        return self.agent_documents.get(agent.name, [])

    def get_chat_history(self) -> ChatHistory:
        """Get the chat history."""
        return self.mas.chat_history
