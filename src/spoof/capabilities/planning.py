from capabilities.planning import Plan, PlanStep, Planning
from capabilities.query_executor import QueryExectuor
from spoof.capabilities.query_executor import QueryExectuorSpoof


class PlanningSpoof(Planning):
    """A spoof for the Planning capability."""

    def create_plan(self, query: str) -> Plan:
        """Create a plan based on the query."""

        # create a simple plan with a single step
        step = PlanStep(
            name="answer_query", description="This step just runs the query."
        )

        # create a plan with the step
        plan = Plan(steps=[step])
        return plan

    def build_executor(self, query: str, plan: Plan) -> QueryExectuor:
        """Build an executor for the plan."""
        # create a simple executor that just runs the query
        executor = QueryExectuorSpoof(self.underlying_model)
        return executor

    def query_needs_planning(self, query: str) -> bool:
        """Check if the query needs planning."""
        return True

    def plan_is_executable(self, plan: Plan) -> bool:
        """Check if the plan is executable."""
        # check if the plan has at least one step
        return len(plan.steps) > 0
