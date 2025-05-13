from core.capability import Capability
from core.query import Query
from core.model import UnderlyingModel


class QueryExectuor(Capability):
    """Can execute a query using a model."""

    def __init__(self, underlying_model: UnderlyingModel):
        super().__init__("query_executor")
        self.underlying_model = underlying_model

    def answer_query(self, query: Query) -> str:
        """Answer a query."""
        raise NotImplementedError("This method should be implemented by subclasses.")
