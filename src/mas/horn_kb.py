"""Horn Knowledge Base"""

from collections import deque
from mas.horn_clause import HornClause


class HornKB:
    """
    Horn Knowledge Base (HornKB) class for managing Horn clauses.

    Attributes:
        horn_clauses (list): List of Horn clauses in the knowledge base.
    """

    def __init__(self):
        """
        Initialise the HornKB with an empty list of Horn clauses.
        """
        self.horn_clauses: list[HornClause] = []

    def add_clause(self, clause: HornClause) -> None:
        """
        Add a Horn clause to the knowledge base.

        Args:
            clause (HornClause): The Horn clause to be added.
        """
        self.horn_clauses.append(clause)

    def forward_chain(self, query: str) -> tuple[bool, list[str]]:
        """
        Perform forward chaining to determine if the query can be derived.

        Args:
            query (str): The proposition to prove.

        Returns:
            tuple: A tuple (True/False, path) indicating whether the query was proven,
                   and the list of inferred literals in order.
        """
        inferred = set()
        agenda = deque()
        count = {}
        clause_map = {}

        # Preprocess clauses
        for clause in self.horn_clauses:
            if not clause.body or len(clause.body) == 0:
                agenda.append(clause.head)
            else:
                count[clause] = len(clause.body)
                for literal in clause.body:
                    clause_map.setdefault(literal, []).append(clause)

        path = []

        while agenda:
            p = agenda.popleft()
            if p in inferred:
                continue

            inferred.add(p)
            path.append(p)

            if p == query:
                return True, path

            for clause in clause_map.get(p, []):
                count[clause] -= 1
                if count[clause] == 0:
                    agenda.append(clause.head)

        return False, path
