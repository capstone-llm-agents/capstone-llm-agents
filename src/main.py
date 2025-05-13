# NOTE: For now just do what you need to make it work but I will fix it later
from autogen import ConversableAgent
from app import App
from core.api import MASAPI
from core.capabiliity_manager import AgentCapabilities
from core.capabiliity_proxy import CapabilityProxy
from core.capability import Capability
from core.entity import HumanUser
from core.mas import MAS
from models.ag2_model import AG2Model
from spoof.spoofed_capabilities import SpoofedCapabilities
from spoof.spoofed_comm_protocol import CommunicationProtocolSpoof
from user_interface.inteface import UserInterface


def generate_capabilities_for_ag2_agent(
    agent: ConversableAgent, agent_capabilities: list[Capability]
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


user = HumanUser("User", "The human user of the MAS")
communication_protocol = CommunicationProtocolSpoof(user)

# NOTE: Here you can add the capabilities that do not need to be spoofed
# (completed capabilities ready to use)
capabilities: list[Capability] = []

mas = MAS(communication_protocol, user)
api = MASAPI(mas)
app = App(api, UserInterface(api))

app.run()
