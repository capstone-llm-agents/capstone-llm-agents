from capabilities.query_executor import QueryExectuor


class QueryExectuorSpoof(QueryExectuor):
    """A spoof for the QueryExectuor capability."""

    def answer_query(self, query: str) -> str:
        """Answer a query."""
        return self.underlying_model.generate(query)
