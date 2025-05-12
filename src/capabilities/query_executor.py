from core.capability import Capability


class QueryExectuor(Capability):
    """Can execute a query using a model."""

    def __init__(self):
        super().__init__("query_executor")

    def answer_query(self, query: str) -> str:
        """Answer a query."""
        raise NotImplementedError("This method should be implemented by subclasses.")
