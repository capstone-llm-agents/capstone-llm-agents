from capabilities.knowledge_base import Document, Knowledge, KnowledgeBase


class KnowledgeBaseSpoof(KnowledgeBase):
    """A spoof for the KnowledgeBase capability."""

    knowledge_base: list[Knowledge]

    def __init__(self, supported_extensions: list[str]):
        super().__init__(supported_extensions)
        self.knowledge_base = []

        self.chunk_size = 128

    def add_knowledge(self, knowledge: Knowledge):
        """Add knowledge to the knowledge base."""
        self.knowledge_base.append(knowledge)

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

        # for simplicity, we will just split the text into chunks of a fixed size.
        # in a real implementation, you might want to use a more sophisticated method.

        if len(text) < self.chunk_size:
            return [Knowledge(text)]

        chunks: list[Knowledge] = []
        for i in range(0, len(text), self.chunk_size):
            start = i
            end = i + self.chunk_size
            chunk = text[start:end]
            chunks.append(Knowledge(chunk))

        return chunks

    def retrieve_related_knowledge(self, query: str) -> list[Knowledge]:
        """Retrieve knowledge related to a query."""

        # for simplicity, we will just return the first 5 knowledge items.
        return self.knowledge_base[:5]
