from core.capabiliity_manager import AgentCapabilities
from core.model import UnderlyingModel
from spoof.capabilities.communication import CommunicationInterfaceSpoof
from spoof.capabilities.error_handling import ErrorHandlerSpoof
from spoof.capabilities.knowledge_base import KnowledgeBaseSpoof
from spoof.capabilities.learning import LearningSpoof
from spoof.capabilities.memory import MemoryManagerSpoof
from spoof.capabilities.monitoring import MonitoringSpoof
from spoof.capabilities.planning import PlanningSpoof
from spoof.capabilities.query_executor import QueryExectuorSpoof
from spoof.capabilities.response_formatter import ResponseFormatterSpoof
from spoof.capabilities.tools import ToolsManagerSpoof


class SpoofedCapabilities(AgentCapabilities):
    """This class is used to spoof the capabilities of an agent."""

    def __init__(
        self, supported_extensions: list[str], underlying_model: UnderlyingModel
    ):

        query_executor = QueryExectuorSpoof(underlying_model)
        knowledge_base = KnowledgeBaseSpoof(supported_extensions)
        memory = MemoryManagerSpoof()
        planning = PlanningSpoof(underlying_model)
        tools_manager = ToolsManagerSpoof()
        response_formatter = ResponseFormatterSpoof()
        communication = CommunicationInterfaceSpoof()
        learning = LearningSpoof()
        error_handler = ErrorHandlerSpoof()
        monitoring = MonitoringSpoof()
        super().__init__(
            query_executor,
            knowledge_base,
            memory,
            planning,
            tools_manager,
            response_formatter,
            communication,
            learning,
            error_handler,
            monitoring,
        )
