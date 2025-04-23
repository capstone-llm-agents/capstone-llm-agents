"""Horn Knowledge Base"""

from collections import deque, defaultdict
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

    def topological_sort(self, clauses: list[HornClause]) -> list[HornClause]:
        """
        Perform a topological sort on the given list of Horn clauses.
        This function assumes that the clauses form a Directed Acyclic Graph (DAG).
        Args:
            clauses (list[HornClause]): The list of Horn clauses to be sorted.
        Returns:
            list[HornClause]: A topologically sorted list of Horn clauses.
        """

        adj: defaultdict[HornClause, list[HornClause]] = defaultdict(list)
        in_degree: defaultdict[HornClause, int] = defaultdict(int)
        clause_by_head = {clause.head: clause for clause in clauses}

        for clause in clauses:
            for b in clause.body:
                if b in clause_by_head:
                    adj[clause_by_head[b]].append(clause)
                    in_degree[clause] += 1

        queue = deque([c for c in clauses if in_degree[c] == 0])
        sorted_path = []

        while queue:
            c = queue.popleft()
            sorted_path.append(c)
            for neighbor in adj[c]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return sorted_path

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

                sorted_path = self.topological_sort(path)
                return True, sorted_path

            for clause in clause_map.get(p, []):
                count[clause] -= 1
                if count[clause] == 0:
                    head = clause.head
                    if head not in provenance:
                        provenance[head] = clause
                    agenda.append(head)

        return False, []
