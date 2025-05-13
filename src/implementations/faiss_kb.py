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
        # Initialize embedding model and placeholders
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )  # 384-d model:contentReference[oaicite:13]{index=13}
        self.tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        self.text_chunks = []  # list of all text chunks
        self.embeddings = None  # will hold numpy array of embeddings
        self.index = None  # FAISS index
        self.max_tokens = max_tokens  # max tokens per chunk
        self.top_k = top_k  # number of top k results to retrieve

    def is_supported_extension(self, extension: str) -> bool:
        """Check if the extension is supported."""
        return extension in self.supported_extensions

    def ingest_document(self, document: Document):
        """Ingest a document into the knowledge base."""
        if not self.is_supported_extension(document.extension):
            raise ValueError(f"Unsupported file extension: {document.extension}")
        # Read file content

        texts = []
        if document.extension == "pdf":
            doc = fitz.open(
                document.path
            )  # PyMuPDF opens PDF:contentReference[oaicite:17]{index=17}
            for page in doc:
                texts.append(page.get_text())
        else:
            with open(document.path, "r", encoding="utf-8") as f:
                texts = [f.read()]

        # Chunk each text and collect all chunks
        all_chunks = []
        for text in texts:
            chunks = []
            token_ids = self.tokenizer.encode(text)
            for i in range(0, len(token_ids), self.max_tokens):
                chunk_ids = token_ids[i : i + self.max_tokens]
                chunk_text = self.tokenizer.decode(chunk_ids)
                chunks.append(chunk_text)
            all_chunks.extend(chunks)

        if not all_chunks:
            return
        self.text_chunks = all_chunks

        # Encode chunks to embeddings
        self.embeddings = self.model.encode(all_chunks)  # list -> numpy array

        # Build FAISS index (flat L2) and add vectors:contentReference[oaicite:18]{index=18}:contentReference[oaicite:19]{index=19}
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(self.embeddings))
        print(f"Indexed {len(all_chunks)} text chunks.")

    def retrieve_related_knowledge(self, query: str) -> list[Knowledge]:
        """
        Retrieves top_k chunks most similar to the query.
        Embeds query and searches FAISS index:contentReference[oaicite:20]{index=20}.
        """
        if self.index is None:
            return []
        # Embed the query text
        query_emb = self.model.encode([query])
        # Search the index
        D, I = self.index.search(np.array(query_emb), self.top_k)
        results = []
        for idx in I[0]:
            results.append(Knowledge(self.text_chunks[idx]))
        return results
