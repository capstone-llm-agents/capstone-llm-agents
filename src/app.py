import yaml

from autogen import ConversableAgent
from core.agent import Agent
from core.app_api import AppAPI
from core.mas_api import MASAPI
from core.capabiliity_manager import AgentCapabilities
from core.capabiliity_proxy import CapabilityProxy
from core.capability import Capability
from core.config import AppConfig
from core.entity import HumanUser
from core.mas import MAS
from models.ag2_model import AG2Model
from spoof.spoofed_capabilities import SpoofedCapabilities
from spoof.spoofed_comm_protocol import CommunicationProtocolSpoof
from storage.api import StorageAPI
from user_interface.inteface import UserInterface


class App:
    """The main application class."""

    def __init__(self, capabilities: list[Capability], config_path: str | None = None):
        # config
        config_path = config_path or "./config.yaml"
        self.config = self.load_config(config_path)

        # mas
        user = HumanUser("User", "The human user of the MAS")
        communication_protocol = CommunicationProtocolSpoof(user)
        mas = MAS(communication_protocol, user)

        # api layer
        mas_api = MASAPI(mas)
        storage_api = StorageAPI(self.config.db_path)
        self.api = AppAPI(mas_api, storage_api)

        # interface layer
        self.interface = UserInterface(self.api)

        # default agent capabilities
        self.capabilities = capabilities

    def load_config(self, config_path: str) -> AppConfig:
        """Load the configuration from a YAML file."""

        # check is yaml
        if not config_path.endswith(".yaml"):
            raise ValueError(
                "Configuration file must be a YAML file with .yaml extension."
            )

        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return AppConfig(**data)

    def run(self):
        """Run the application."""
        # start
        self.api.start()

        self.interface.run()

    def add_agent(self, agent: Agent):
        """Add an agent to the MAS."""
        self.api.mas_api.mas.add_agent(agent)
        self.api.storage_api.add_agent(agent)

    def _generate_capabilities_for_ag2_agent(
        self, agent: ConversableAgent, agent_capabilities: list[Capability]
    ) -> AgentCapabilities:
        """Generate capabilities for the AG2 agent."""
        # agent capabiltiies using proxy
        supported_extensions: list[str] = []

        ag2_model = AG2Model(agent)

        spoofed_capabilities = SpoofedCapabilities(supported_extensions, ag2_model)

        proxy = CapabilityProxy(spoofed_capabilities)

        for capability in agent_capabilities:
            proxy.add_capability(capability)

        return proxy.build_capabilities_manager()

    def _generate_agent_from_ag2_agent(
        self, ag2_agent: ConversableAgent, agent_capabilities: list[Capability]
    ) -> Agent:
        """Generate an agent from the AG2 agent."""

        ag2_model = AG2Model(ag2_agent)

        capabilities_manager = self._generate_capabilities_for_ag2_agent(
            ag2_agent, agent_capabilities
        )

        agent = Agent(
            name=ag2_agent.name,
            description=ag2_agent.description,
            role="agent",
            capabilities=capabilities_manager,
            underlying_model=ag2_model,
        )

        return agent

    def add_ag2_agent(
        self,
        ag2_agent: ConversableAgent,
        agent_capabilities: list[Capability] | None = None,
    ):
        """Add an AG2 agent to the MAS."""
        if agent_capabilities is None:
            agent_capabilities = self.capabilities

        agent = self._generate_agent_from_ag2_agent(ag2_agent, agent_capabilities)
        self.add_agent(agent)
