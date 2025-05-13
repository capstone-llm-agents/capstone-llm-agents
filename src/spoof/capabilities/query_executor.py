from capabilities.query_executor import QueryExectuor
from core.query import Query


class QueryExectuorSpoof(QueryExectuor):
    """A spoof for the QueryExectuor capability."""

    def answer_query(self, query: Query) -> str:
        """Answer a query."""
        return self.underlying_model.generate(query)
