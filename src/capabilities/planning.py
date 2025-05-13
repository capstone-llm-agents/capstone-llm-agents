from capabilities.query_executor import QueryExectuor
from core.capability import Capability
from core.model import UnderlyingModel


class PlanStep:
    """A class to represent a step in a plan."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description


class Plan:
    """A class to represent a plan."""

    def __init__(self, steps: list[PlanStep]):
        self.steps = steps

    def add_step(self, step: PlanStep):
        """Add a step to the plan."""
        self.steps.append(step)


class Planning(Capability):
    """A class to represent the planning capabilities of the agent."""

    def __init__(self, underlying_model: UnderlyingModel):
        super().__init__("planning")
        self.underlying_model = underlying_model

    def create_plan(self, query: str) -> Plan:
        """Create a plan based on the query."""
        raise NotImplementedError("create_plan not implemented")

    def build_executor(self, query: str, plan: Plan) -> QueryExectuor:
        """Build an executor for the plan."""
        raise NotImplementedError("build_executor not implemented")

    def query_needs_planning(self, query: str) -> bool:
        """Check if the query needs planning."""
        raise NotImplementedError("query_needs_planning not implemented")

    def plan_is_executable(self, plan: Plan) -> bool:
        """Check if the plan is executable."""
        raise NotImplementedError("plan_is_executable not implemented")
