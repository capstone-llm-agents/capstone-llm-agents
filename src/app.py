import yaml
import os


from autogen import ConversableAgent
from core.agent import Agent
from core.app_api import AppAPI
from core.mas_api import MASAPI
from core.capabiliity_manager import AgentCapabilities
from core.capabiliity_proxy import CapabilityProxy
from core.capability import Capability
from core.config import AppConfig, Config, LoadedConfig
from core.entity import HumanUser
from core.mas import MAS
from core.space import MainSpace, UserSpace
from core.space_api import SpaceAPI
from models.ag2_model import AG2Model
from spoof.spoofed_capabilities import SpoofedCapabilities
from storage.api import StorageAPI
from user_interface.user_interface import UserInterface
from user_interface.cli import CLI
from user_interface.gui import GUI
from implementations.communication_protocol import BasicCommunicationProtocol


class App:
    """The main application class."""

    def __init__(
        self,
        config_path: str | None = None,
    ):
        # config
        config_path = config_path or "./config.yaml"
        self.config = LoadedConfig(self.load_config(config_path))

        # mas
        user = HumanUser("User", "The human user of the MAS")
        communication_protocol = BasicCommunicationProtocol(
            user, UserSpace("User Space", None, user), MainSpace("Main Space", None, [])
        )
        mas = MAS(communication_protocol, user)

        # api layer
        mas_api = MASAPI(mas)
        storage_api = StorageAPI(self.config.get_db_path())
        space_api = SpaceAPI([], mas)
        self.api = AppAPI(mas_api, storage_api, space_api)

        # interface dict
        interfaces: dict[str, type[UserInterface]] = {
            "cli": CLI,
            "gui": GUI,
        }

        # get from config
        interface_name = self.config.app_config.interface

        if interface_name not in interfaces:
            print(
                f"[WARN] Interface '{interface_name}' not found. Defaulting to CLI interface."
            )

        # get interface
        interface_type = interfaces.get(interface_name, interfaces["cli"])

        # interface layer
        self.interface = interface_type()

        # set interface API
        self.interface.set_api(self.api)

        # default agent capabilities
        self.capabilities = []

    def load_config(self, config_path: str) -> AppConfig:
        """Load the configuration from a YAML file."""

        # check is yaml
        if not config_path.endswith(".yaml"):
            raise ValueError(
                "Configuration file must be a YAML file with .yaml extension."
            )

        # check if file exists
        if not os.path.exists(config_path):
            # ask config
            print("Config file does not exist. Let's create one!\n")
            Config.create_config_file()

        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return AppConfig(**data)

    def add_capability(self, capability: Capability):
        """Add a capability to the MAS."""
        self.capabilities.append(capability)

    def run(self):
        """Run the application."""
        # start
        self.api.start()

        self.interface.run()

    def add_agent(self, agent: Agent):
        """Add an agent to the MAS."""
        self.api.mas_api.mas.add_agent(agent)
        self.api.storage_api.add_agent(agent)

        # TODO remove this hack

        proto = self.api.mas_api.mas.communication_protocol

        if isinstance(proto, BasicCommunicationProtocol):
            proto.add_agent(agent)

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