# NOTE: For now just do what you need to make it work but I will fix it later
from autogen import ConversableAgent
from app import App
from core.agent import Agent
from core.api import MASAPI
from core.capabiliity_manager import AgentCapabilities
from core.capabiliity_proxy import CapabilityProxy
from core.capability import Capability
from core.entity import HumanUser
from core.mas import MAS
from implementations.memory import Memory
from implementations.faiss_kb import FAISSKnowledgeBase
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


def generate_agent_from_ag2_agent(
    ag2_agent: ConversableAgent, agent_capabilities: list[Capability]
) -> Agent:
    """Generate an agent from the AG2 agent."""

    ag2_model = AG2Model(ag2_agent)

    capabilities_manager = generate_capabilities_for_ag2_agent(
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


user = HumanUser("User", "The human user of the MAS")
communication_protocol = CommunicationProtocolSpoof(user)

# NOTE: Here you can add the capabilities that do not need to be spoofed
# (completed capabilities ready to use)
capabilities: list[Capability] = [FAISSKnowledgeBase(["pdf", "txt"], 1000, 3)]
capabilities: list[Capability] = [Memory()]

mas = MAS(communication_protocol, user)
api = MASAPI(mas)
app = App(api, UserInterface(api))

assistant_agent = generate_agent_from_ag2_agent(
    ConversableAgent(
        name="Assistant",
        system_message="You are a helpful assistant.",
        llm_config={"api_type": "ollama", "model": "granite3.1-dense"},
    ),
    capabilities,
)

mas.add_agent(assistant_agent)

app.run()
