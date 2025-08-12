"""The base class for a knowledge base in a multi-agent system."""


class KnowledgeBase:
    """A base class for a knowledge base in a multi-agent system."""

    def __init__(self) -> None:
        """Initialize the knowledge base."""
        self.facts: list[str] = []

    def add_fact(self, fact: str) -> None:
        """Add a fact to the knowledge base."""
        self.facts.append(fact)

    def query(self, query: str) -> list[str]:
        """Query the knowledge base for facts matching the query."""
        return self.facts
