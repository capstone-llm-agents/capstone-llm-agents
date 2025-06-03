from core.query import Query


class Task:
    """A task to be completed by an agent."""

    def __init__(self, description: str):
        self.description = description

    def __str__(self):
        return f"Task(description='{self.description}')"


class AnswerQueryTask(Task):
    """A task to answer a query."""

    def __init__(self, query: Query):
        super().__init__(f"Answer the query: '{query.content}'")
        self.query = query
