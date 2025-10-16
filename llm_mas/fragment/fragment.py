"""The fragment is a base primitive data type for the system that can be observed by the system, agent and user."""

import datetime
import uuid

from llm_mas.fragment.agent_view import AgentView
from llm_mas.fragment.kind import FragmentKind
from llm_mas.fragment.source import FragmentSource
from llm_mas.fragment.system_view import SystemView
from llm_mas.fragment.user_view import UserView


class Fragment:
    """A base primitive data type for the system that can be observed by the system, agent and user."""

    def __init__(
        self,
        name: str,
        kind: FragmentKind,
        description: str | None = None,
        source: FragmentSource = FragmentSource.UNKNOWN,
    ) -> None:
        """Initialize a fragment with a name, description, kind, and source."""
        self.name = name
        self.description = description
        self.kind = kind
        self.source = source

        self.id = str(uuid.uuid4())
        self.created_at = datetime.datetime.now(tz=datetime.UTC)

    def agent_view(self) -> AgentView:
        """Return the agent's view of the fragment."""
        return self.kind.agent_view()

    def system_view(self) -> SystemView:
        """Return the system's view of the fragment."""
        return self.kind.system_view()

    def user_view(self) -> UserView:
        """Return the user's view of the fragment."""
        return self.kind.user_view()
