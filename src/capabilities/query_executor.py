from core.capability import Capability
from core.model import UnderlyingModel
from core.query import Query


class QueryExectuor(Capability):
    """Can execute a query using a model."""

    def __init__(self, underlying_model: UnderlyingModel):
        super().__init__("query_executor")
        self.underlying_model = underlying_model

    def answer_query(self, query: Query) -> str:
        """Answer a query."""
        raise NotImplementedError("This method should be implemented by subclasses.")
