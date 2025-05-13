from capabilities.knowledge_base import Document, Knowledge, KnowledgeBase


class DocumentSpoof(Document):
    """A spoof for the Document class."""

    def __init__(self, path: str, extension: str):
        super().__init__(path, extension)
        self.text = "Hello World! This is a test document."

    def to_text(self) -> str:
        """Convert the document to text."""
        return self.text


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
        print(f"Knowledge added: {knowledge.knowledge}")
        for k in self.knowledge_base:
            print(f" - {k.knowledge}")

    def is_supported_extension(self, extension: str) -> bool:
        """Check if the extension is supported."""
        return extension in self.supported_extensions

    def ingest_document(self, document: Document):
        """Ingest a document into the knowledge base."""
        if not self.is_supported_extension(document.extension):
            raise ValueError(f"Unsupported file extension: {document.extension}")

        # override with a spoofed document
        spoofed_document = DocumentSpoof(document.path, document.extension)

        text = spoofed_document.to_text()
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
