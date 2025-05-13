# NOTE: For now just do what you need to make it work but I will fix it later
import argparse

from capabilities.knowledge_base import Document
from implementations.faiss_kb import FAISSKnowledgeBase


class AG2Agent:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base

    def ask(self, query):
        # Retrieve relevant text snippets from the KB
        docs = self.kb.retrieve_related_knowledge(query, top_k=3)
        if not docs:
            return "No knowledge available."
        # In a real RAG system, here we'd call an LLM with these docs.
        # For now, just join the snippets to simulate an answer.

        for doc in docs:
            print(doc.knowledge + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG Knowledge Base Agent")
    parser.add_argument("doc_path", help="Path to a .txt or .pdf file to ingest")
    args = parser.parse_args()

    # Instantiate knowledge base and agent
    kb = FAISSKnowledgeBase(["txt", "pdf"])
    document = Document(args.doc_path, args.doc_path.split(".")[-1])
    agent = AG2Agent(kb)

    # Ingest the document
    print(f"Ingesting document '{document.path}'...")
    kb.ingest_document(document)

    # Loop to accept queries
    print("Ready for questions. Type your query and press Enter.")
    while True:
        query = input("\nYour question: ")
        if not query.strip():
            print("Exiting.")
            break
        answer = agent.ask(query)
        print(f"Agent response:\n{answer}")
