from core.capability import Capability


class Knowledge:
    """A simple knowledge representation to store information."""

    def __init__(self, knowledge: str):
        self.knowledge = knowledge

    def __str__(self) -> str:
        return self.knowledge


class Document:
    """A document to be ingested into the knowledge base that could be a PDF, Word document, etc. provided by the user."""

    def __init__(self, path: str, extension: str):
        self.path = path
        self.extension = extension

    def to_text(self) -> str:
        """Convert the document to text."""
        raise NotImplementedError("This method should be implemented by subclasses.")


class KnowledgeBase(Capability):
    """A simple knowledge base to store and retrieve information that the agent can use."""

    def __init__(self, supported_extensions: list[str]):
        super().__init__("knowledge_base")
        self.supported_extensions = supported_extensions

    def add_knowledge(self, knowledge: Knowledge):
        """Add knowledge to the knowledge base."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def is_supported_extension(self, extension: str) -> bool:
        """Check if the extension is supported."""
        return extension in self.supported_extensions

    def ingest_document(self, document: Document):
        """Ingest a document into the knowledge base."""
        if not self.is_supported_extension(document.extension):
            raise ValueError(f"Unsupported file extension: {document.extension}")

        text = document.to_text()
        knowledge = self.chunk_text_to_knowledge(text)

        for k in knowledge:
            self.add_knowledge(k)

    def chunk_text_to_knowledge(self, text: str) -> list[Knowledge]:
        """Chunk text into knowledge."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def retrieve_related_knowledge(self, query: str) -> list[Knowledge]:
        """Retrieve knowledge related to a query."""
        raise NotImplementedError("This method should be implemented by subclasses.")
