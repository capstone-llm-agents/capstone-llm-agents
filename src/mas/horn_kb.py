"""Horn Knowledge Base"""

from collections import deque
from mas.horn_clause import HornClause


class HornKB:
    """
    Horn Knowledge Base (HornKB) class for managing Horn clauses.

    Attributes:
        horn_clauses (list): List of Horn clauses in the knowledge base.
    """

    horn_clauses: list[HornClause]
    """List of Horn clauses in the knowledge base."""

    def __init__(self):
        """
        Initialise the HornKB with an empty list of Horn clauses.
        """
        self.horn_clauses = []

    def add_clause(self, clause: HornClause) -> None:
        """
        Add a Horn clause to the knowledge base.

        Args:
            clause (HornClause): The Horn clause to be added.
        """
        self.horn_clauses.append(clause)

    def forward_chain(self, query: str) -> tuple[bool, list[HornClause]]:
        """
        Perform goal-aware forward chaining to determine if the query can be derived.
        Stops once the query is entailed and prunes unnecessary steps.

        Args:
            query (str): The proposition to prove.

        Returns:
            tuple: A tuple (True/False, path) indicating whether the query was proven,
                and the minimal list of HornClauses used to infer the query.
        """
        inferred = set()
        agenda: deque[str] = deque()
        count: dict[HornClause, int] = {}
        clause_map: dict[str, list[HornClause]] = {}
        provenance: dict[str, HornClause] = {}

        # preprocess clauses
        for clause in self.horn_clauses:
            if not clause.body:
                agenda.append(clause.head)
                provenance[clause.head] = clause
            else:
                count[clause] = len(clause.body)
                for literal in clause.body:
                    clause_map.setdefault(literal, []).append(clause)

        while agenda:
            p = agenda.popleft()
            if p in inferred:
                continue

            inferred.add(p)

            if p == query:
                # reconstruct the path that led to the query
                path = []
                to_trace = deque([query])
                traced = set()

                while to_trace:
                    fact = to_trace.popleft()
                    if fact in traced or fact not in provenance:
                        continue
                    clause = provenance[fact]
                    path.append(clause)
                    traced.add(fact)
                    for b in clause.body:
                        to_trace.append(b)

                return True, list(reversed(path))

            for clause in clause_map.get(p, []):
                count[clause] -= 1
                if count[clause] == 0:
                    head = clause.head
                    if head not in provenance:
                        provenance[head] = clause
                    agenda.append(head)

        return False, []
