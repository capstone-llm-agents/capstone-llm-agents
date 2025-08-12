"""Action class for the multi-agent system."""

from llm_mas.action_system.core.action_params import ActionParams
from llm_mas.action_system.core.action_result import ActionResult


class Action:
    """Base class for all actions in the system."""

    def __init__(self, name: str | None = None) -> None:
        """Initialize the action with a name."""
        self.name = name if name is not None else self.__class__.__name__

    def do(self, params: ActionParams) -> ActionResult:
        """Perform the action with the given agent."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)

    def __eq__(self, other: object) -> bool:
        """Check equality based on the class name."""
        if not isinstance(other, Action):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        """Return the hash based on the class name."""
        return hash(self.name)
