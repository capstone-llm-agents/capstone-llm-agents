"""Horn Clause"""


class HornClause:
    """
    Horn Clause class representing a Horn clause in propositional logic.

    Attributes:
        head (str): The head of the Horn clause.
        body (list): The body of the Horn clause, represented as a list of literals.
    """

    def __init__(self, head: str, body: list[str]) -> None:
        """
        Initialise the HornClause with a head and body.

        Args:
            head (str): The head of the Horn clause.
            body (list): The body of the Horn clause, represented as a list of literals.
        """
        self.head = head
        self.body = body

    def __repr__(self) -> str:
        """
        Return a string representation of the HornClause.

        Returns:
            str: The string representation of the HornClause.
        """
        return f"HornClause(head={self.head}, body={self.body})"

    def __str__(self) -> str:
        """
        Return a string representation of the HornClause.

        Returns:
            str: The string representation of the HornClause.
        """
        return f"{', '.join(self.body)} => {self.head}"
