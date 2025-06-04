from typing import cast
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
from core.capabiliity_manager import AgentCapabilities, CapabilityMap
from core.capability import Capability

from spoof.spoofed_capabilities import SpoofedCapabilities


class CapabilityProxy:
    """A proxy class that let's you choose which spoofed capabilities to use."""

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

    # spoofed capabilities
    spoofed_capabilities: SpoofedCapabilities

    # capabilities map
    capabilities: dict[str, Capability]

    def __init__(self, spoofed_capabilities: SpoofedCapabilities):
        # capabilities
        self.capabilities = {}

        # spoofed capabilities
        self.spoofed_capabilities = spoofed_capabilities

    def add_capability(self, capability: Capability) -> "CapabilityProxy":
        """Add a capability to the proxy."""
        self.capabilities[capability.name] = capability
        return self

    def get_capabilities(self) -> list[Capability]:
        """Get all capabilities."""
        return list(self.capabilities.values())

    def build_capabilities_manager(self) -> "AgentCapabilities":
        """Build the capabilities manager."""

        # get capabilities from proxy
        proxy_capabilities = self.get_capabilities()

        # get capabilities from spoofed capabilities to fill the gaps
        spoofed_capabilities = self.spoofed_capabilities.get_capabilities()

        capabilties_dict = {}

        # add capabilities to the capabilities dict
        for capability in spoofed_capabilities:
            capabilties_dict[capability.name] = capability

        # override with the capabilities from the proxy
        for capability in proxy_capabilities:
            capabilties_dict[capability.name] = capability

        def convert_dict_to_capabilities(
            capabilities_dict: dict[str, Capability],
        ) -> CapabilityMap:
            """Convert a dictionary to a capabilities map."""
            return cast(CapabilityMap, capabilities_dict)

        capabilities_map = convert_dict_to_capabilities(capabilties_dict)

        return AgentCapabilities.from_capabilities(capabilities_map)
