"""A fragment kind defines the type and structure of a fragment."""

from llm_mas.fragment.agent_view import AgentView
from llm_mas.fragment.system_view import SystemView
from llm_mas.fragment.user_view import UserView


class FragmentKind:
    """A fragment kind defines the type and structure of a fragment."""

    def __init__(self, name: str, description: str, raw: SystemView) -> None:
        """Initialize a fragment kind with a name, description and raw data."""
        self.name = name
        self.description = description
        self.raw = raw

    def system_view(self) -> SystemView:
        """Return the system's view of the fragment."""
        return self.raw

    def agent_view(self) -> AgentView:
        """Return the agent's view of the fragment."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)

    def user_view(self) -> UserView:
        """Return the user's view of the fragment."""
        msg = "This method should be overridden by subclasses."
        raise NotImplementedError(msg)

    def get_raw_type(self) -> type[SystemView]:
        """Return the type of the raw data."""
        return type(self.raw)
