from capabilities.knowledge_base import KnowledgeBase, Knowledge, Document
from sentence_transformers import SentenceTransformer
from transformers import GPT2TokenizerFast  # for token counting
import fitz, faiss, numpy as np


class FAISSKnowledgeBase(KnowledgeBase):
    """A simple knowledge base to store and retrieve information that the agent can use."""

    def __init__(
        self, supported_extensions: list[str], max_tokens: int = 100, top_k: int = 5
    ):
        super().__init__("knowledge_base")
        self.supported_extensions = supported_extensions
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        self.text_chunks = []  # list of all text chunks
        self.embeddings = None  # will hold numpy array of embeddings
        self.index = None  # FAISS index
        self.max_tokens = max_tokens  # max tokens per chunk
        self.top_k = top_k  # number of top k results to retrieve

        # Instead of single index, we use a list of document-specific storages
        self.documents = []  # list of dicts: each with 'chunks', 'embeddings', 'index'

    def is_supported_extension(self, extension: str) -> bool:
        """Check if the extension is supported."""
        return extension in self.supported_extensions

    def ingest_document(self, document: Document):
        """Ingest a document into the knowledge base."""
        if not self.is_supported_extension(document.extension):
            raise ValueError(f"Unsupported file extension: {document.extension}")

        # Read text from document
        texts = []
        if document.extension == "pdf":
            doc = fitz.open(document.path)
            for page in doc:
                texts.append(page.get_text())
        else:
            with open(document.path, "r", encoding="utf-8") as f:
                texts = [f.read()]

        all_chunks = []
        for text in texts:
            token_ids = self.tokenizer.encode(text)
            for i in range(0, len(token_ids), self.max_tokens):
                chunk_ids = token_ids[i : i + self.max_tokens]
                chunk_text = self.tokenizer.decode(chunk_ids)
                all_chunks.append(chunk_text)

        if not all_chunks:
            return

        # Encode and index chunks
        embeddings = self.model.encode(all_chunks)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings))

        self.documents.append(
            {"chunks": all_chunks, "embeddings": embeddings, "index": index}
        )
        print(f"Ingested document with {len(all_chunks)} chunks.")

    def retrieve_related_knowledge(self, query: str) -> list[Knowledge]:
        """
        Retrieves top_k chunks most similar to the query.
        Embeds query and searches FAISS index:contentReference[oaicite:20]{index=20}.
        """
        if not self.documents:
            return []

        query_emb = self.model.encode([query])
        combined_results = []

        # Search each document index separately
        for doc in self.documents:
            D, I = doc["index"].search(np.array(query_emb), self.top_k)
            for dist, idx in zip(D[0], I[0]):
                if idx < len(doc["chunks"]):
                    combined_results.append((dist, doc["chunks"][idx]))

        # Sort all results by distance and return top_k overall
        combined_results.sort(key=lambda x: x[0])
        top_chunks = [Knowledge(text) for _, text in combined_results[: self.top_k]]
        return top_chunks
