from typing import TypedDict
from capabilities.communication import CommunicationInterface
from capabilities.error_handling import ErrorHandler
from capabilities.knowledge_base import KnowledgeBase
from capabilities.learning import Learning
from capabilities.memory import MemoryManager
from capabilities.monitoring import Monitoring
from capabilities.planning import Planning
from capabilities.query_executor import QueryExectuor
from capabilities.response_formatter import ResponseFormatter
from capabilities.tools import ToolsManager
from core.capability import Capability


class CapabilityMap(TypedDict):
    """A map of capabilities."""

    query_executor: QueryExectuor
    knowledge_base: KnowledgeBase
    memory: MemoryManager
    planning: Planning
    tools_manager: ToolsManager
    response_formatter: ResponseFormatter
    communication: CommunicationInterface
    learning: Learning
    error_handler: ErrorHandler
    monitoring: Monitoring


class AgentCapabilities:
    """Manages the capabilities of the agent."""

    # supported by Sprint 2 (in order of priority)
    query_executor: QueryExectuor
    knowledge_base: KnowledgeBase
    memory: MemoryManager
    planning: Planning
    tools_manager: ToolsManager
    response_formatter: ResponseFormatter

    # supported by Sprint 3 (in order of priority)
    communication: CommunicationInterface
    learning: Learning
    error_handler: ErrorHandler
    monitoring: Monitoring

    # capabilities map
    capabilities: CapabilityMap
    known_capabilities: list[Capability]

    def __init__(
        self,
        query_executor: QueryExectuor,
        knowledge_base: KnowledgeBase,
        memory: MemoryManager,
        planning: Planning,
        tools_manager: ToolsManager,
        response_formatter: ResponseFormatter,
        communication: CommunicationInterface,
        learning: Learning,
        error_handler: ErrorHandler,
        monitoring: Monitoring,
    ):
        # supported by Sprint 2 (in order of priority)
        self.query_executor = query_executor
        self.knowledge_base = knowledge_base
        self.memory = memory
        self.planning = planning
        self.tools_manager = tools_manager
        self.response_formatter = response_formatter

        # supported by Sprint 3 (in order of priority)
        self.communication = communication
        self.learning = learning
        self.error_handler = error_handler
        self.monitoring = monitoring

        # known_capabilities
        self.known_capabilities = []

        # add them
        self.add_capabilities(
            [
                self.query_executor,
                self.knowledge_base,
                self.memory,
                self.planning,
                self.tools_manager,
                self.response_formatter,
                self.communication,
                self.learning,
                self.error_handler,
                self.monitoring,
            ]
        )

        # set capabilities map
        self.capabilities = {
            "query_executor": self.query_executor,
            "knowledge_base": self.knowledge_base,
            "memory": self.memory,
            "planning": self.planning,
            "tools_manager": self.tools_manager,
            "response_formatter": self.response_formatter,
            "communication": self.communication,
            "learning": self.learning,
            "error_handler": self.error_handler,
            "monitoring": self.monitoring,
        }

    def add_capability(self, capability: Capability) -> "AgentCapabilities":
        """Add a capability to the agent."""
        if capability not in self.known_capabilities:
            self.known_capabilities.append(capability)
        else:
            raise ValueError(f"Capability {capability} already exists.")

        return self

    def add_capabilities(self, capabilities: list[Capability]):
        """Add multiple capabilities to the agent."""
        for capability in capabilities:
            self.add_capability(capability)

    def get_capabilities(self) -> list[Capability]:
        """Get all capabilities."""
        return self.known_capabilities

    def get_capabilities_dict(self) -> CapabilityMap:
        """Get all capabilities as a dictionary."""
        return self.capabilities

    @classmethod
    def from_capabilities(cls, capabilities: CapabilityMap) -> "AgentCapabilities":
        """Create an AgentCapabilities instance from a list of capabilities."""

        return cls(
            query_executor=capabilities["query_executor"],
            knowledge_base=capabilities["knowledge_base"],
            memory=capabilities["memory"],
            planning=capabilities["planning"],
            tools_manager=capabilities["tools_manager"],
            response_formatter=capabilities["response_formatter"],
            communication=capabilities["communication"],
            learning=capabilities["learning"],
            error_handler=capabilities["error_handler"],
            monitoring=capabilities["monitoring"],
        )
